from playwright.async_api import Page, expect

async def get_user_menu_button(page: Page):
    """Возвращает локатор для кнопки меню пользователя"""
    return page.get_by_role("button", name="Меню пользователя root")

async def get_settings_option(page: Page):
    """Возвращает локатор для пункта 'Настройки' в выпадающем меню"""
    return page.locator('div.user-menu__item:has-text("Настройки")')

async def get_logout_option(page: Page):
    """Возвращает локатор для пункта 'Выйти' в выпадающем меню"""
    return page.locator('div.user-menu__item:has-text("Выйти")')

async def get_settings_heading(page: Page):
    """Возвращает локатор для заголовка 'Настройки пользователя'"""
    return page.get_by_role("heading", name="Настройки пользователя - root", level=1)

async def get_2fa_setup_link(page: Page):
    """Возвращает локатор для ссылки 'Настроить двухэтапную аутентификацию'"""
    return page.get_by_role("link", name="Настроить двухэтапную аутентификацию")

async def get_disable_2fa_checkbox(page: Page):
    """Возвращает локатор для чек-бокса 'Отключить двухэтапную аутентификацию'"""
    return page.get_by_text("Отключить двухэтапную аутентификацию")

async def get_save_button(page: Page):
    """Возвращает локатор для кнопки 'Сохранить'"""
    return page.get_by_role("button", name="Сохранить")

async def check_settings_heading(page: Page):
    """Проверяет, что заголовок — 'Настройки пользователя - root'"""
    heading = await get_settings_heading(page)
    await expect(heading).to_be_visible()
    await expect(heading).to_have_text("Настройки пользователя - root")

async def check_and_activate_disable_2fa_checkbox(page: Page):
    """Активирует чек-бокс 'Отключить двухэтапную аутентификацию'"""
    checkbox = await get_disable_2fa_checkbox(page)
    await checkbox.click()

async def is_settings_page_visible(page: Page):
    """Проверяет, находится ли страница на настройках пользователя"""
    heading = await get_settings_heading(page)
    try:
        await heading.wait_for(state="visible", timeout=3000)
        return True
    except:
        return False