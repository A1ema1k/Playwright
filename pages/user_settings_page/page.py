# pages/user_settings_page/page.py
from playwright.async_api import Page

async def open_user_menu(page: Page):
    """Открывает меню пользователя"""
    user_menu_btn = page.get_by_role("button", name="Меню пользователя root")
    await user_menu_btn.click()

async def click_settings_option(page: Page):
    """Нажимает на пункт 'Настройки' в меню"""
    settings_option = page.locator('div.user-menu__item:has-text("Настройки")')
    await settings_option.click()

async def click_logout_option(page: Page):
    """Нажимает на пункт 'Выйти' в меню"""
    logout_option = page.locator('div.user-menu__item:has-text("Выйти")')
    await logout_option.click()

async def get_settings_heading(page: Page):
    """Возвращает локатор заголовка настроек"""
    return page.get_by_role("heading", name="Настройки пользователя - root", level=1)