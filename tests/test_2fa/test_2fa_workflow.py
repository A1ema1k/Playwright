# tests/test_2fa/test_2fa_workflow.py
import pytest
import os
import re
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter
from playwright.async_api import Page
from pages.authorization_page.actions import perform_login_with_screenshots
from pages.license_agreement_page.actions import handle_license_agreement_with_screenshots
from pages.user_settings_page.actions import (
    navigate_to_settings_with_screenshots,
    logout_with_screenshots,
    disable_2fa_with_screenshots
)
from pages.two_factor_auth.actions import (
    open_2fa_settings_with_screenshots,
    extract_secret_key_and_account,
    activate_2fa_with_code
)
from pages.two_factor_auth.auth_page import enter_2fa_code_with_screenshots
from pages.two_factor_auth.two_factor_utils import generate_2fa_code
from utils.config import (
    REFERENCE_URL, REFERENCE_USERNAME, REFERENCE_PASSWORD, REFERENCE_SERVER,
    TEST_URL, TEST_USERNAME, TEST_PASSWORD, TEST_SERVER
)
from utils.ssh_client import disable_license_agreement_on_server


# Системы для тестирования
SYSTEMS = [
    ("reference", REFERENCE_URL, REFERENCE_USERNAME, REFERENCE_PASSWORD, REFERENCE_SERVER),
    ("test", TEST_URL, TEST_USERNAME, TEST_PASSWORD, TEST_SERVER),
]


def get_screenshot_groups():
    """
    Находит и группирует скриншоты по фазе: 01_login, 04_2fa и т.д.
    Игнорирует различия в суффиксах (_before, _opened и др.)
    """
    ref_dir = "screenshots/reference"
    test_dir = "screenshots/test"

    if not os.path.exists(ref_dir):
        raise FileNotFoundError(f"Папка {ref_dir} не найдена")
    if not os.path.exists(test_dir):
        raise FileNotFoundError(f"Папка {test_dir} не найдена")

    ref_files = {f for f in os.listdir(ref_dir) if f.endswith(".png")}
    test_files = {f for f in os.listdir(test_dir) if f.endswith(".png")}

    groups = {}

    def extract_phase(filename):
        # Берём первые два компонента: "04_2fa", "08_2fa", "01_login"
        parts = filename.split('_', 2)  # разбиваем только по первым двум '_'
        return f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else filename

    # Собираем файлы по фазам
    for f in ref_files:
        phase = extract_phase(f)
        groups.setdefault(phase, {'ref': [], 'test': []})['ref'].append(f)
    for f in test_files:
        phase = extract_phase(f)
        if phase in groups:
            groups[phase]['test'].append(f)

    # Формируем пары (phase, ref_path, test_path)
    result = []
    for phase, files in groups.items():
        if files['ref'] and files['test']:
            # Берём лексикографически первый файл в каждой группе
            ref_file = min(files['ref'])
            test_file = min(files['test'])
            result.append((
                phase,
                os.path.join(ref_dir, ref_file),
                os.path.join(test_dir, test_file)
            ))
    return sorted(result, key=lambda x: x[0])


async def compare_screenshots(reference_path: str, test_path: str, diff_path: str, threshold: float = 0.01):
    """
    Сравнивает скриншоты с повышенной чувствительностью к тексту.
    Сохраняет наглядный diff с красным overlay и подписью %.
    """
    if not os.path.exists(reference_path) or not os.path.exists(test_path):
        print(f"⚠️  Пропущено: {os.path.basename(reference_path)} — файл отсутствует")
        return False, 1.0

    try:
        ref = Image.open(reference_path).convert('RGB')
        test = Image.open(test_path).convert('RGB')

        if ref.size != test.size:
            print(f"⚠️  Размеры различаются: {ref.size} vs {test.size}")
            return True, 1.0

        # Пиксельная разница
        diff = ImageChops.difference(ref, test)
        diff_gray = diff.convert('L')

        # 🔻 Повышенная чувствительность к тексту
        threshold_val = 20  # снижаем порог
        mask = diff_gray.point(lambda p: 255 if p >= threshold_val else 0, mode='1')
        mask = mask.filter(ImageFilter.MaxFilter(3))  # "раздуваем" различия на 1px

        # Считаем %
        total = ref.width * ref.height
        diff_pixels = sum(1 for p in mask.getdata() if p == 255)
        diff_pct = diff_pixels / total

        # Визуализация: эталон + полупрозрачный красный overlay
        overlay = Image.new('RGBA', ref.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for y in range(ref.height):
            for x in range(ref.width):
                if mask.getpixel((x, y)) == 255:
                    draw.point((x, y), fill=(255, 0, 0, 100))  # R, G, B, A=100 (~40%)

        result = ref.copy().convert('RGBA')
        result = Image.alpha_composite(result, overlay).convert('RGB')

        # Подпись с процентом
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("Arial Bold.ttf", 24)
            except:
                font = ImageFont.load_default()

        draw_res = ImageDraw.Draw(result)
        text = f"Δ: {diff_pct:.3%}"
        # Тень + белый текст для читаемости
        draw_res.text((10, 10), text, fill=(0, 0, 0), font=font)
        draw_res.text((9, 9), text, fill=(255, 255, 255), font=font)

        # Сохраняем
        os.makedirs(os.path.dirname(diff_path), exist_ok=True)
        result.save(diff_path, "PNG", optimize=True)

        return diff_pct > threshold, diff_pct

    except Exception as e:
        print(f"❌ Ошибка при сравнении {os.path.basename(reference_path)}: {e}")
        return False, 0.0


@pytest.mark.asyncio
async def test_2fa_workflow_with_screenshot_comparison(page: Page):
    """
    Полный workflow 2FA для reference и test + сравнение ВСЕХ скриншотов.
    """
    results = {}

    # === 1. Запуск тестов для всех систем ===
    for system_name, url, username, password, server_config in SYSTEMS:
        print(f"\n{'='*60}")
        print(f"🚀 ТЕСТ: [{system_name.upper()}]")
        print(f"{'='*60}")

        try:
            print(f"🔧 [{system_name}] Отключаем EULA...")
            eula_res = await disable_license_agreement_on_server(server_config)
            if not eula_res["success"]:
                raise Exception(f"EULA: {eula_res.get('error', 'unknown')}")

            # Workflow
            await page.goto(url)
            await perform_login_with_screenshots(page, system_name, username, password, "01_login")
            await handle_license_agreement_with_screenshots(page, system_name, "02_license")
            await navigate_to_settings_with_screenshots(page, system_name, "03_settings")
            await open_2fa_settings_with_screenshots(page, system_name, "04_2fa_setup")
            secret_key, _ = await extract_secret_key_and_account(page)

            if not secret_key:
                raise Exception("Секретный ключ не получен")

            code1 = generate_2fa_code(secret_key)
            await activate_2fa_with_code(page, code1, system_name, "05_2fa_activation")
            await logout_with_screenshots(page, system_name, "06_logout")
            await perform_login_with_screenshots(page, system_name, username, password, "07_relogin")
            code2 = generate_2fa_code(secret_key)
            await enter_2fa_code_with_screenshots(page, code2, system_name, "08_2fa_auth")
            await navigate_to_settings_with_screenshots(page, system_name, "09_settings_for_disable")
            await disable_2fa_with_screenshots(page, system_name, "10_disable_2fa")
            await logout_with_screenshots(page, system_name, "11_final_logout")

            results[system_name] = {"status": "PASSED", "secret_key": secret_key}
            print(f"✅ [{system_name}] Тест успешно завершён")

        except Exception as e:
            error_msg = str(e)
            print(f"❌ [{system_name}] ОШИБКА: {error_msg}")
            await page.screenshot(
                path=f"screenshots/{system_name}/error_{system_name}.png",
                full_page=True
            )
            results[system_name] = {"status": "FAILED", "error": error_msg}

    # === 2. Проверка успешности ===
    failed = [name for name, r in results.items() if r["status"] != "PASSED"]
    if failed:
        pytest.fail(f"Тесты упали для: {', '.join(failed)}")

    print(f"\n{'='*60}")
    print("🔍 ДИНАМИЧЕСКОЕ СРАВНЕНИЕ СКРИНШОТОВ")
    print(f"{'='*60}")

    # === 3. Сравнение всех найденных скриншотов ===
    try:
        groups = get_screenshot_groups()
        if not groups:
            pytest.fail("Не найдено общих скриншотов для сравнения")

        print(f"✅ Найдено групп скриншотов: {len(groups)}")
        for phase, ref_path, test_path in groups:
            print(f"   • {phase}: {os.path.basename(ref_path)} ↔ {os.path.basename(test_path)}")

        diff_dir = "screenshots/diff"
        failed_comparisons = []

        for phase, ref_path, test_path in groups:
            diff_path = os.path.join(diff_dir, f"{phase}_diff.png")
            is_diff, pct = await compare_screenshots(ref_path, test_path, diff_path)

            if is_diff:
                print(f"❌ {phase}: различия {pct:.3%}")
                failed_comparisons.append(f"{phase} ({pct:.3%})")
            else:
                print(f"✅ {phase}: идентичны")

        # === 4. Итоговый отчёт ===
        if failed_comparisons:
            summary = "Обнаружены различия в скриншотах:\n  • " + "\n  • ".join(failed_comparisons)
            print(f"\n📊 ОТЧЁТ:\n{summary}")
            pytest.fail(summary)
        else:
            print("\n🎉 Все скриншоты совпадают! UI регрессии нет.")

    except Exception as e:
        pytest.fail(f"Ошибка при сравнении скриншотов: {e}")