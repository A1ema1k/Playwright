# pages/authorization_page/actions.py
from playwright.async_api import Page
from utils.screenshot_utils import take_screenshot


async def perform_login_with_screenshots(
    page: Page,
    panel_name: str,
    username: str,
    password: str,
    step_name: str,
    *,
    screenshot_before: bool = True,   # ← можно отключить
    screenshot_after: bool = False    # ← можно включить при отладке
):
    """
    Логин с гибкими скриншотами:
    - ДО ввода (по умолчанию) — для сравнения
    - ПОСЛЕ ввода (опционально) — для отладки
    """
    # Ждём полной загрузки формы
    await page.wait_for_load_state("networkidle", timeout=10000)

    # 1. Скриншот ДО ввода — ЧИСТАЯ ФОРМА (обязательно для сравнения)
    if screenshot_before:
        await take_screenshot(
            page,
            panel_name,
            f"{step_name}_before",
            auth_page=True
        )

    # 2. Заполняем форму
    await page.locator('input[name="username"]').fill(username)
    await page.locator('input[name="password"]').fill(password)

    # 3. Опциональный скриншот ПОСЛЕ ввода (для дебага)
    if screenshot_after:
        await take_screenshot(
            page,
            panel_name,
            f"{step_name}_after",
            auth_page=True
        )

    # 4. Клик + ожидание перехода (самое быстрое)
    async with page.expect_navigation(timeout=15000):
        await page.get_by_role("button", name="Войти").click()

    await page.locator('input[name="username"]').wait_for(state="hidden", timeout=10000)