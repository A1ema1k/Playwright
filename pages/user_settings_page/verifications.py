# pages/user_settings_page/verifications.py
from playwright.async_api import expect
from .page import get_settings_heading

async def verify_settings_page_loaded(page):
    """Проверяет, что страница настроек загружена"""
    heading = await get_settings_heading(page)
    await expect(heading).to_be_visible()

async def verify_user_menu_visible(page):
    """Проверяет, что меню пользователя доступно"""
    user_menu_btn = page.get_by_role("button", name="Меню пользователя root")
    await expect(user_menu_btn).to_be_visible()