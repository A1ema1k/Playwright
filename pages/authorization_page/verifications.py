# pages/authorization_page/verifications.py
from playwright.async_api import expect
from .page import get_language_button, get_auth_heading


async def verify_login_page_loaded(page):
    """Проверяет, что страница логина загружена"""
    heading = await get_auth_heading(page)
    await expect(heading).to_be_visible()


async def verify_russian_language(page):
    """Проверяет русский язык интерфейса"""
    language_btn = await get_language_button(page)
    await expect(language_btn).to_be_visible()


async def verify_login_form_elements(page):
    """Проверяет наличие всех элементов формы"""
    await verify_login_page_loaded(page)
    await verify_russian_language(page)

    # Проверяем поля ввода
    username_input = page.locator('input[name="username"]')
    password_input = page.locator('input[name="password"]')
    login_button = page.get_by_role("button", name="Войти")

    await expect(username_input).to_be_visible()
    await expect(password_input).to_be_visible()
    await expect(login_button).to_be_visible()