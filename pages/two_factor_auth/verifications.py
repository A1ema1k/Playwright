# pages/two_factor_auth/verifications.py
from playwright.async_api import expect
from .page import get_2fa_header, get_secret_key_container, get_account_name_container


async def verify_2fa_drawer_visible(page):
    """Проверяет, что дравер 2FA открыт"""
    header = await get_2fa_header(page)
    await expect(header).to_be_visible()

    header_text = await header.text_content()
    assert "Двухэтапная аутентификация" in header_text, f"Ожидался заголовок 2FA, но найден: {header_text}"


async def verify_secret_key_visible(page):
    """Проверяет, что секретный ключ отображается"""
    secret_key_container = await get_secret_key_container(page)
    await expect(secret_key_container).to_be_visible()


async def verify_account_name_visible(page):
    """Проверяет, что имя аккаунта отображается"""
    account_container = await get_account_name_container(page)
    await expect(account_container).to_be_visible()