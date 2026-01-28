# pages/two_factor_auth/actions.py
import re
from playwright.async_api import Page
from . import page as twofa_page
from . import verifications as twofa_checks
from utils.screenshot_utils import take_screenshot


async def open_2fa_settings_with_screenshots(page: Page, panel_name: str, step_name: str):
    """
    Открывает настройки 2яFA со скриншотами
    """
    # Нажимаем на ссылку настройки 2FA
    await twofa_page.click_2fa_settings_link(page)

    # Ждем открытия дравера
    await twofa_checks.verify_2fa_drawer_visible(page)

    # Скриншот открытого дравера
    await take_screenshot(page, panel_name, f"{step_name}_drawer_opened", full_page=True)

    # Нажимаем на кнопки для отображения данных
    secret_key_btn = await twofa_page.get_secret_key_button(page)
    await secret_key_btn.click()

    account_btn = await twofa_page.get_account_name_button(page)
    await account_btn.click()

    # Ждем отображения данных
    await twofa_checks.verify_secret_key_visible(page)
    await twofa_checks.verify_account_name_visible(page)

    return page


async def extract_secret_key_and_account(page: Page):
    """
    Извлекает секретный ключ и имя аккаунта со страницы
    """
    try:
        # Получаем секретный ключ
        secret_key_element = await twofa_page.get_secret_key_container(page)
        secret_key_text = await secret_key_element.text_content()

        # Ищем ключ в тексте
        secret_key_match = re.search(r'[A-Z2-7]{32,}', secret_key_text)
        if secret_key_match:
            secret_key = secret_key_match.group(0)
            print(f"  🔑 Найден секретный ключ: {secret_key}")
        else:
            print("  ❌ Не удалось найти секретный ключ в тексте:")
            print(secret_key_text)
            return None, None

        # Получаем имя аккаунта
        account_element = await twofa_page.get_account_name_container(page)
        account_text = await account_element.text_content()

        # Извлекаем имя аккаунта из текста
        account_match = re.search(r"Наименование аккаунта\s*([^.\s]+)", account_text)
        if account_match:
            account_name = account_match.group(1)
            print(f"  👤 Найдено имя аккаунта: {account_name}")
        else:
            print("  ❌ Не удалось найти имя аккаунта в тексте:")
            print(account_text)
            return secret_key, None

        return secret_key, account_name

    except Exception as e:
        print(f"  ❌ Ошибка при извлечении данных: {e}")
        return None, None


async def activate_2fa_with_code(page: Page, code: str, panel_name: str, step_name: str):
    """
    Активирует 2FA с вводом кода и скриншотами
    """
    # Вводим код
    code_input = await twofa_page.get_2fa_code_input(page)
    await code_input.click()
    await code_input.fill(code)

    # Нажимаем активировать
    activate_btn = await twofa_page.get_activate_button(page)
    await activate_btn.click()

    # Ждем закрытия дравера или появления сообщения об успехе
    try:
        await page.wait_for_selector("#dynamic-form-drawer-totp-new-header", state="hidden", timeout=10000)
        print("  ✅ Дравер 2FA закрыт - активация прошла успешно")
    except:
        print("  ⚠️ Дравер не закрылся, но продолжаем...")

    return page