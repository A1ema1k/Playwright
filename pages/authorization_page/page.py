# pages/authorization_page/page.py
from playwright.async_api import Page

async def fill_username(page: Page, username: str):
    """Заполняет поле логина"""
    input_field = page.locator('input[name="username"]')
    await input_field.click()
    await input_field.fill(username)

async def fill_password(page: Page, password: str):
    """Заполняет поле пароля"""
    input_field = page.locator('input[name="password"]')
    await input_field.click()
    await input_field.fill(password)

async def click_login_button(page: Page):
    """Нажимает кнопку Войти"""
    login_btn = page.get_by_role("button", name="Войти")
    await login_btn.click()

#async def get_language_button(page: Page):
#    """Возвращает локатор кнопки языка"""
#    return page.locator('button[aria-label="Язык"]:has-text("Русский")')
#
#async def get_auth_heading(page: Page):
#    """Возвращает локатор заголовка авторизации"""
#    return page.locator('h1.login-form__title:has-text("Авторизация")')