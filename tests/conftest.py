# conftest.py
import pytest
import asyncio
from utils.ssh_client import disable_license_agreement_on_servers
from utils.config import ALL_SERVERS


@pytest.fixture(scope="session")
def event_loop():
    """Правильный event loop для session-scoped async фикстур"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_license_agreement():
    print("Подготавливаем серверы — отключаем лицензионное соглашение...")

    if not ALL_SERVERS:
        print("Серверы не настроены, пропускаем")
        return

    results = await disable_license_agreement_on_servers(ALL_SERVERS)

    success_count = sum(1 for r in results.values() if r["success"])
    print(f"Итог: Успешно — {success_count}, Ошибок — {len(results) - success_count}")

    await asyncio.sleep(5)


# Остальные фикстуры — можно оставить, но лучше упростить
@pytest.fixture(scope="function")
async def page():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        yield page
        await context.close()
        await browser.close()