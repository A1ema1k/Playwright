from playwright.async_api import Page, Locator

def get_2fa_settings_link(page: Page) -> Locator:
    """Локатор для ссылки 'Настроить двухэтапную аутентификацию'"""
    return page.get_by_role("link", name="Настроить двухэтапную аутентификацию")

def get_secret_key_container(page: Page) -> Locator:
    """Локатор для контейнера секретного ключа"""
    return page.locator("isp-form-view-text-with-link-container")

def get_secret_key_button(page: Page) -> Locator:
    """Локатор для кнопки в контейнере секретного ключа"""
    return page.locator("isp-form-view-text-with-link-container").get_by_role("button")

def get_account_name_container(page: Page) -> Locator:
    """Локатор для контейнера имени аккаунта"""
    return page.locator("isp-form-view-text-auxiliary").filter(has_text="Наименование аккаунта")

def get_account_name_button(page: Page) -> Locator:
    """Локатор для кнопки в контейнере имени аккаунта"""
    return page.locator("isp-form-view-text-auxiliary").filter(has_text="Наименование аккаунта").get_by_role("button")

def get_2fa_code_input(page: Page) -> Locator:
    """Локатор для поля ввода 2FA кода"""
    return page.get_by_role("textbox", name="Временный пароль*")

def get_activate_button(page: Page) -> Locator:
    """Локатор для кнопки 'Активировать'"""
    return page.get_by_role("button", name="Активировать")

def get_2fa_header(page: Page) -> Locator:
    """Локатор для заголовка дравера 'Двухэтапная аутентификация'"""
    return page.locator("#dynamic-form-drawer-totp-new-header > div > isp-form-view-element > isp-form-view-header-auxiliary > h1")

def get_2fa_code_login_input(page: Page) -> Locator:
    """Локатор для поля ввода 2FA кода на странице авторизации"""
    return page.get_by_role("textbox", name="Введите код")

def get_login_button(page: Page) -> Locator:
    """Локатор для кнопки 'Войти' на странице авторизации"""
    return page.get_by_role("button", name="Войти")