# pages/two_factor_auth/auth_page.py
from playwright.async_api import Page
from utils.screenshot_utils import take_screenshot


async def get_2fa_code_login_input(page: Page):
    """Возвращает локатор для поля ввода 2FA кода на странице авторизации"""
    return page.get_by_role("textbox", name="Введите код")


async def get_login_button_2fa(page: Page):
    """Возвращает локатор для кнопки 'Войти' на странице 2FA"""
    return page.get_by_role("button", name="Войти")


async def enter_2fa_code_with_screenshots(page: Page, code: str, panel_name: str, step_name: str):
    """
    Вводит 2FA-код на странице двухфакторной аутентификации со скриншотами
    """
    # Скриншот до ввода кода
    #await take_screenshot(page, panel_name, f"{step_name}_before_input", full_page=True)

    # Вводим код
    code_input = await get_2fa_code_login_input(page)
    await code_input.click()
    await code_input.fill(code)

    # Скриншот после ввода кода
    await take_screenshot(page, panel_name, f"{step_name}_code_entered", auth_page=True)

    # Нажимаем войти
    login_btn = await get_login_button_2fa(page)
    await login_btn.click()

    # Скриншот после аутентификации
    #await take_screenshot(page, panel_name, f"{step_name}_after_auth", full_page=True)

    return page