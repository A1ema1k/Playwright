# pages/two_factor_auth/page.py
from playwright.async_api import Page

async def get_2fa_settings_link(page: Page):
    """Возвращает локатор для ссылки 'Настроить двухэтапную аутентификацию'"""
    return page.get_by_role("link", name="Настроить двухэтапную аутентификацию")

async def click_2fa_settings_link(page: Page):
    """Нажимает на ссылку настройки 2FA"""
    link = await get_2fa_settings_link(page)
    await link.click()

async def get_secret_key_container(page: Page):
    """Возвращает локатор контейнера секретного ключа"""
    return page.locator("isp-form-view-text-with-link-container")

async def get_secret_key_button(page: Page):
    """Возвращает локатор кнопки секретного ключа"""
    return page.locator("isp-form-view-text-with-link-container").get_by_role("button")

async def get_account_name_container(page: Page):
    """Возвращает локатор контейнера имени аккаунта"""
    return page.locator("isp-form-view-text-auxiliary").filter(has_text="Наименование аккаунта")

async def get_account_name_button(page: Page):
    """Возвращает локатор кнопки имени аккаунта"""
    return page.locator("isp-form-view-text-auxiliary").filter(has_text="Наименование аккаунта").get_by_role("button")

async def get_2fa_code_input(page: Page):
    """Возвращает локатор поля ввода 2FA кода"""
    return page.get_by_role("textbox", name="Временный пароль*")

async def get_activate_button(page: Page):
    """Возвращает локатор кнопки 'Активировать'"""
    return page.get_by_role("button", name="Активировать")

async def get_2fa_header(page: Page):
    """Возвращает локатор заголовка дравера 2FA"""
    return page.locator("#dynamic-form-drawer-totp-new-header > div > isp-form-view-element > isp-form-view-header-auxiliary > h1")