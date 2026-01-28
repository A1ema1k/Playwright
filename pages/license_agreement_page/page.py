# pages/license_agreement_page/page.py
from playwright.async_api import Page
from .locators import get_accept_button, is_license_page_visible

async def check_license_agreement_visible(page: Page) -> bool:
    """Проверяет, отображено ли лицензионное соглашение"""
    return await is_license_page_visible(page)

async def accept_license_agreement(page: Page) -> bool:
    """Принимает лицензионное соглашение, если оно отображено"""
    license_visible = await check_license_agreement_visible(page)

    if license_visible:
        print("Обнаружено лицензионное соглашение, принимаем...")
        accept_button = await get_accept_button(page)
        await accept_button.click()
        # Ожидаем перехода на дашборд после принятия соглашения
        await page.wait_for_url("**/ispmgr#/dashboard**", timeout=15000)
        print("Лицензионное соглашение принято")
    else:
        print("Лицензионное соглашение не обнаружено, продолжаем...")

    return license_visible