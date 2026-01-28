from playwright.async_api import Page, expect

async def get_login_input(page: Page):
    """Возвращает локатор для поля ввода логина"""
    return page.locator('input[name="username"]')

async def get_password_input(page: Page):
    """Возвращает локатор для поля ввода пароля"""
    return page.locator('input[name="password"]')

async def get_language_button(page: Page):
    """Возвращает локатор для кнопки выбора языка"""
    return page.locator('button[aria-label="Язык"]:has-text("Русский")')

async def get_auth_heading(page: Page):
    """Возвращает локатор для заголовка 'Авторизация'"""
    return page.locator('h1.login-form__title:has-text("Авторизация")')

async def check_language_is_russian(page: Page):
    """Проверяет, что выбран русский язык"""
    language_button = await get_language_button(page)
    await expect(language_button).to_have_text("Русский")

async def check_auth_heading(page: Page):
    """Проверяет, что заголовок — 'Авторизация'"""
    heading = await get_auth_heading(page)
    await expect(heading).to_have_text("Авторизация")