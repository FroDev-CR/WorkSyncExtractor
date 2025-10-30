"""
Módulo de extracción de órdenes de SupplyPro usando Playwright
"""
import pandas as pd
import asyncio
import base64
from playwright.async_api import async_playwright
from config import SUPPLYPRO_URL


async def extraer_ordenes(username: str, password: str) -> pd.DataFrame:
    """
    Extrae las órdenes de SupplyPro usando credenciales específicas

    Args:
        username: Usuario de SupplyPro
        password: Contraseña de SupplyPro

    Returns:
        DataFrame con las órdenes extraídas
    """
    async with async_playwright() as p:
        # Lanzar navegador en modo headless con opciones para cloud
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()

        try:
            # Login
            await page.goto(SUPPLYPRO_URL, timeout=60000)
            await page.wait_for_load_state('networkidle')

            # Llenar formulario de login
            await page.fill('#user_name', username)
            await page.fill('#password', password)

            # Submit y esperar navegación
            await page.click('input[type="submit"]')
            await page.wait_for_load_state('networkidle', timeout=60000)

            # Verificar que el login fue exitoso y esperar a que la página esté lista
            # Dar tiempo para que JavaScript cargue el menú
            await page.wait_for_timeout(3000)

            # Intentar encontrar el link de órdenes
            try:
                # Esperar explícitamente a que el link sea visible Y clickable
                link_locator = page.locator('a', has_text='Newly Received Orders')
                await link_locator.wait_for(state='attached', timeout=10000)

                # Verificar si el link existe
                count = await link_locator.count()
                if count == 0:
                    # El login puede haber fallado
                    page_content = await page.content()
                    if 'error' in page_content.lower() or 'invalid' in page_content.lower():
                        raise Exception("Error de autenticación. Verifica las credenciales en config.py")
                    else:
                        raise Exception(f"No se encontró el link 'Newly Received Orders' en el dashboard. URL actual: {page.url}")

                # El link existe, hacer click
                await link_locator.first.click(timeout=10000)

            except Exception as e:
                # Si falla, intentar navegación directa
                current_url = page.url
                if 'Login.asp' in current_url:
                    raise Exception("El login falló. Verifica las credenciales en config.py")

                # Intentar URL directa
                base_url = current_url.split('?')[0].rsplit('/', 1)[0]
                possible_urls = [
                    f"{base_url}/orders_new.asp",
                    f"{base_url}/OrdersNew.asp",
                    f"{base_url}/orders.asp"
                ]

                navigated = False
                for url in possible_urls:
                    try:
                        await page.goto(url, timeout=15000)
                        await page.wait_for_selector('select[name="ref_epo_filter"]', timeout=5000)
                        navigated = True
                        break
                    except:
                        continue

                if not navigated:
                    raise Exception(f"No se pudo acceder a las órdenes. Error original: {str(e)}")

            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_selector('select[name="ref_epo_filter"]', timeout=30000)

            # Seleccionar filtro
            await page.select_option('select[name="ref_epo_filter"]', label='Show All Except EPOs')
            await page.wait_for_timeout(5000)

            # Extraer tabla
            table_element = await page.query_selector('//th[contains(normalize-space(.), "Builder")]/ancestor::table')

            if not table_element:
                raise Exception("No se encontró la tabla de órdenes")

            # Obtener HTML de la tabla
            table_html = await table_element.inner_html()
            full_table_html = f"<table>{table_html}</table>"

            # Convertir a DataFrame
            df = pd.read_html(full_table_html)[0]

            # Cerrar sesión
            try:
                await page.click('text=Sign Out')
                await page.wait_for_timeout(2000)
            except:
                pass

            return df

        except Exception as e:
            # Capturar screenshot para debugging
            try:
                screenshot_bytes = await page.screenshot(full_page=True)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
                error_msg = f"{str(e)}\n\n[DEBUG] Captura de pantalla disponible para análisis."
            except:
                error_msg = str(e)

            raise Exception(error_msg)

        finally:
            await browser.close()


def ejecutar_extraccion(username: str, password: str) -> pd.DataFrame:
    """
    Wrapper síncrono para la función asíncrona de extracción
    """
    return asyncio.run(extraer_ordenes(username, password))
