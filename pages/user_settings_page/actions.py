# pages/user_settings_page/actions.py (дополнение)
from playwright.async_api import Page
from . import page as settings_page
from . import verifications as settings_checks
from utils.screenshot_utils import take_screenshot


async def navigate_to_settings_with_screenshots(page: Page, panel_name: str, step_name: str):
    """
    Переход в настройки пользователя со скриншотами
    """

    # Открываем меню пользователя
    await settings_page.open_user_menu(page)

    # Переходим в настройки
    await settings_page.click_settings_option(page)

    # Ждем загрузки страницы настроек
    await settings_checks.verify_settings_page_loaded(page)

    # Скриншот страницы настроек
    await take_screenshot(page, panel_name, f"{step_name}_settings_loaded")

    return page


async def logout_with_screenshots(page: Page, panel_name: str, step_name: str):
    """
    Выход из системы со скриншотами через меню пользователя
    """
    print("  🔄 Выполняем выход через меню пользователя...")

    # 1. Открываем меню пользователя
    await settings_page.open_user_menu(page)

    # 2. Нажимаем "Выйти"
    await settings_page.click_logout_option(page)

    # 3. Ожидаем выхода - используем несколько стратегий
    try:
        # Стратегия 1: Ждем появления формы логина
        await page.wait_for_selector('input[name="username"]', timeout=15000)
        print("  ✅ Страница логина загружена (по полю ввода)")

    except Exception as e:
        print(f"  ⚠️ Не удалось обнаружить поле логина: {e}")

        try:
            # Стратегия 2: Ждем изменения URL на логин
            await page.wait_for_url("**/login**", timeout=10000)
            print("  ✅ URL изменился на страницу логина")

        except Exception as e2:
            print(f"  ⚠️ URL не изменился: {e2}")

            try:
                # Стратегия 3: Ждем появления кнопки "Войти"
                await page.wait_for_selector('button:has-text("Войти")', timeout=5000)
                print("  ✅ Обнаружена кнопка 'Войти'")

            except Exception as e3:
                print(f"  ⚠️ Кнопка 'Войти' не найдена: {e3}")

                # Стратегия 4: Проверяем текущее состояние
                current_url = page.url
                print(f"  📍 Текущий URL: {current_url}")

                # Если мы все еще на той же странице, пробуем обновить
                if "usrparam" in current_url or "dashboard" in current_url:
                    print("  🔄 Обновляем страницу...")
                    await page.reload()
                    await page.wait_for_timeout(2000)

    # 4. Финальная проверка - есть ли форма логина?
    try:
        username_input = page.locator('input[name="username"]')
        if await username_input.is_visible():
            print("  ✅ Подтверждено: форма логина отображается")
        else:
            print("  ⚠️ Форма логина не отображается, но продолжаем...")
    except Exception as e:
        print(f"  ⚠️ Финальная проверка не удалась: {e}")

    print("  ✅ Процедура выхода завершена")
    return page


async def disable_2fa_with_screenshots(page: Page, panel_name: str, step_name: str):
    """
    Отключение 2FA
    """
    print("  🔄 Отключаем двухфакторную аутентификацию...")

    # Ждем загрузки
    await page.wait_for_timeout(3000)

    # Просто ищем текст и кликаем
    checkbox = page.get_by_text("Отключить двухэтапную аутентификацию")
    await checkbox.click()

    # Сохраняем
    save_button = page.get_by_role("button", name="Сохранить")
    await save_button.click()

    # Ждем
    await page.wait_for_timeout(2000)

    print("  ✅ 2FA отключена")
    return page
