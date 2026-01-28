from playwright.async_api import Page, expect

async def get_license_heading(page: Page):
    """Возвращает локатор для заголовка лицензионного соглашения"""
    return page.get_by_role("heading", name="ЛИЦЕНЗИОННОЕ СОГЛАШЕНИЕ С КОНЕЧНЫМ ПОЛЬЗОВАТЕЛЕМ", level=1)

async def get_accept_button(page: Page):
    """Возвращает локатор для кнопки 'Согласен'"""
    return page.get_by_role("button", name="Согласен", exact=True)

async def is_license_page_visible(page: Page):
    """Проверяет, видна ли страница лицензионного соглашения (ожидает заголовок)"""
    heading = await get_license_heading(page)
    try:
        await heading.wait_for(state="visible", timeout=3000)
        return True
    except:
        return False