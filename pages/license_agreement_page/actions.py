# pages/license_agreement_page/actions.py
from playwright.async_api import Page
from . import page as license_page
from utils.screenshot_utils import take_screenshot


async def handle_license_agreement_with_screenshots(page: Page, panel_name: str, step_name: str):
    """
    Обработка лицензионного соглашения со скриншотами
    """
    # Проверяем, есть ли соглашение
    has_license = await license_page.check_license_agreement_visible(page)

    if has_license:
        # Скриншот соглашения
        await take_screenshot(page, panel_name, f"{step_name}_license_shown", full_page=True)

        # Принимаем соглашение
        await license_page.accept_license_agreement(page)


        print(f"✅ Лицензионное соглашение принято на панели {panel_name}")
    else:
        # Скриншот отсутствия соглашения
        await take_screenshot(page, panel_name, f"{step_name}_no_license", full_page=True)
        print(f"ℹ️ Лицензионное соглашение не показано на панели {panel_name}")

    return has_license