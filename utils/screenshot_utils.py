# utils/screenshot_utils.py
import os
from typing import Optional, List
from playwright.async_api import Page, Locator


async def _mask_login_background(page: Page) -> None:
    """
    Убирает динамический фон на странице логина:
    - canvas#fullscreen-layout-canvas (Three.js)
    - .background блоки (winter/dark/theme)
    - сохраняет SVG-иконки (defs), но удаляет фоновые SVG
    """
    try:
        # ✅ Надёжная проверка: ищем канвас ИЛИ background-классы — не текст!
        has_canvas = await page.locator("#fullscreen-layout-canvas").count() > 0
        has_background = await page.locator(".background").count() > 0
        if not (has_canvas or has_background):
            # Дополнительно проверим URL/title как fallback
            url = page.url.lower()
            title = (await page.title()).lower()
            if "login" not in url and "авторизация" not in title and "вход" not in title:
                return

        print("Форма логина найдена — отключаем фон")

        # === 1. Скрыть canvas ===
        await page.evaluate("""
            () => {
                const canvas = document.getElementById('fullscreen-layout-canvas');
                if (canvas) {
                    canvas.style.display = 'none';
                    canvas.style.visibility = 'hidden';
                    canvas.style.opacity = '0';
                }
            }
        """)

        # === 2. Скрыть .background блоки ===
        await page.evaluate("""
            () => {
                document.querySelectorAll('.background').forEach(el => {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                });
            }
        """)

        # === 3. Обработка SVG: безопасное извлечение defs, без ошибок в селекторах ===
        await page.evaluate("""
            () => {
                const defs = new Set();

                // 🔹 Безопасный поиск use-элементов: поддержка xlink:href и href
                const useElements = document.querySelectorAll(
                    'use[xlink\\\\:href], use[href], use[*|href]'
                );

                useElements.forEach(use => {
                    // Получаем href любым способом
                    let href = use.getAttribute('xlink:href') || 
                               use.getAttribute('href') || 
                               use.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
                    if (href && href.startsWith('#')) {
                        const id = href.slice(1);
                        const symbol = document.getElementById(id);
                        if (symbol) {
                            defs.add(symbol.outerHTML);
                        }
                    }
                });

                // Удаляем фоновые SVG (оставляем только в кнопках/формах)
                document.querySelectorAll('svg').forEach(svg => {
                    const isImportant = svg.closest('button, form, .form, .buttons, .actions, [role="button"]');
                    if (isImportant) return; // оставляем полезные иконки

                    // Удаляем SVG, если он:
                    // - внутри .background
                    // - или маленький и не имеет текста/кнопок рядом
                    if (svg.closest('.background') || 
                        (svg.width?.baseVal?.value < 100 && svg.height?.baseVal?.value < 100)) {
                        svg.remove();
                    }
                });

                // Восстанавливаем defs в скрытом контейнере
                let container = document.getElementById('__playwright_defs__');
                if (!container) {
                    container = document.createElement('div');
                    container.id = '__playwright_defs__';
                    container.style.cssText = 'position: absolute; width: 0; height: 0; overflow: hidden;';
                    document.body.appendChild(container);
                }
                if (defs.size > 0) {
                    container.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                            <defs>${Array.from(defs).join('')}</defs>
                        </svg>
                    `;
                } else {
                    container.innerHTML = '';
                }
            }
        """)

        # === 4. CSS-резерв: принудительная очистка фона ===
        await page.add_style_tag(content="""
            /* Основные фоновые элементы */
            #fullscreen-layout-canvas,
            .background,
            [class*="background_"],
            [id*="background"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
            }
            /* Очистка body и корневых контейнеров */
            body, isp-root, isp-login-layout, isp-fullscreen-layout > div {
                background: #ffffff !important;
                background-color: #ffffff !important;
            }
            /* Убираем псевдоэлементы */
            body::before, body::after {
                display: none !important;
                background: transparent !important;
            }
            /* Гарантируем белый фон под формой */
            isp-login-layout .form-container,
            isp-login-layout form {
                background: #ffffff !important;
            }
        """, type="text/css")

        print("✅ Фон логина отключён: canvas, .background, SVG")

    except Exception as e:
        print(f"⚠️ Ошибка при отключении фона: {e}")


async def take_screenshot(
    page: Page,
    panel: str,
    name: str,
    *,
    center_element: Optional[Locator] = None,
    full_page: bool = False,
    auth_page: bool = False,
    mask_qr_code: bool = False,
    mask_selectors: Optional[List[str]] = None,
    timeout: float = 10000,
    wait_for_stable: bool = True
) -> str:
    """
    Универсальная функция для скриншотов.
    Поддерживает:
    - auth_page=True → чистый логин без фона
    - mask_selectors → скрыть любые элементы
    - center_element → центрировать страницу
    - mask_qr_code → скрыть QR
    """
    screenshot_dir = f"screenshots/{panel}"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = f"{screenshot_dir}/{name}.png"

    to_hide: List[Locator] = []

    # === 1. Центрирование ===
    if center_element:
        try:
            await center_element.wait_for(state="visible", timeout=timeout)
            await center_element.scroll_into_view_if_needed()
            await page.evaluate(
                """(el) => {
                    const rect = el.getBoundingClientRect();
                    const x = rect.left + rect.width / 2;
                    const y = rect.top + rect.height / 2;
                    window.scrollTo(x - window.innerWidth / 2, y - window.innerHeight / 2);
                }""",
                center_element
            )
            await page.wait_for_timeout(300)
            print("Страница центрирована по элементу")
        except Exception as e:
            print(f"Не удалось центрировать: {e}")

    # === 2. Автоматическая маскировка фона логина ===
    if auth_page:
        await _mask_login_background(page)

    # === 3. QR-код ===
    if mask_qr_code:
        qr = page.locator("isp-form-view-image-auxiliary img")
        try:
            if await qr.count() > 0:
                await qr.first.wait_for(state="visible", timeout=2000)
                to_hide.append(qr.first)
                print("QR-код будет скрыт")
        except:
            pass

    # === 4. Пользовательские селекторы ===
    if mask_selectors:
        for selector in mask_selectors:
            try:
                loc = page.locator(selector).first
                if await loc.count() > 0:
                    await loc.wait_for(state="visible", timeout=2000)
                    to_hide.append(loc)
                    print(f"Будет скрыт: {selector}")
            except Exception as e:
                print(f"Не удалось найти {selector}: {e}")

    # === 5. Делаем скриншот ===
    try:
        # Скрываем элементы
        for loc in to_hide:
            await loc.evaluate("el => el.style.visibility = 'hidden'")

        if wait_for_stable:
            try:
                await page.wait_for_load_state('networkidle', timeout=timeout)
            except:
                pass  # не критично

        await page.screenshot(
            path=screenshot_path,
            full_page=full_page,
            timeout=timeout
        )
        print(f"Скриншот сохранён: {screenshot_path}")

    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        # Делаем аварийный скриншот
        try:
            await page.screenshot(path=screenshot_path, full_page=full_page, timeout=5000)
        except:
            pass
    finally:
        # Восстанавливаем видимость
        for loc in to_hide:
            try:
                await loc.evaluate("el => el.style.visibility = ''")
            except:
                pass

    return screenshot_path