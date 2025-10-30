"""
Módulo de extracción de órdenes de SupplyPro usando Playwright
"""
import pandas as pd
import asyncio
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
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        try:
            # Paso 1: Ir a la página de login
            print(f"🔗 Navegando a SupplyPro...")
            await page.goto(SUPPLYPRO_URL, wait_until='networkidle', timeout=60000)
            print(f"✅ Página cargada: {page.url}")

            # Paso 2: Esperar y llenar formulario
            print(f"📝 Llenando formulario de login...")
            await page.wait_for_selector('#user_name', state='visible', timeout=15000)
            await page.type('#user_name', username, delay=100)

            await page.wait_for_selector('#password', state='visible', timeout=15000)
            await page.type('#password', password, delay=100)

            print(f"✅ Credenciales ingresadas")

            # Paso 3: Submit y esperar navegación
            print(f"🚀 Enviando login...")
            submit_button = await page.query_selector('input[type="submit"]')

            # Click y esperar navegación
            await submit_button.click()
            await page.wait_for_load_state('networkidle', timeout=60000)
            await page.wait_for_timeout(3000)

            current_url = page.url
            print(f"📍 URL después del login: {current_url}")

            # Paso 4: Verificar que el login fue exitoso
            if 'Login.asp' in current_url:
                # Aún estamos en la página de login - el login falló
                page_text = await page.content()
                if 'invalid' in page_text.lower() or 'incorrect' in page_text.lower():
                    raise Exception("❌ Credenciales incorrectas. Verifica usuario y contraseña.")
                else:
                    raise Exception("❌ El login no se completó. SupplyPro puede estar experimentando problemas.")

            print(f"✅ Login exitoso")

            # Paso 5: Buscar y hacer click en "Newly Received Orders"
            print(f"🔍 Buscando link 'Newly Received Orders'...")

            # Esperar un poco más para que la página cargue completamente
            await page.wait_for_timeout(5000)

            # Intentar múltiples selectores
            orden_clickeado = False

            # Intento 1: Link con texto exacto
            try:
                link = page.locator('a:has-text("Newly Received Orders")').first
                if await link.count() > 0:
                    print(f"✅ Link encontrado (método 1)")
                    await link.click(timeout=10000)
                    orden_clickeado = True
            except Exception as e:
                print(f"⚠️ Método 1 falló: {str(e)}")

            # Intento 2: Por href
            if not orden_clickeado:
                try:
                    link = page.locator('a[href*="orders"]').first
                    if await link.count() > 0:
                        print(f"✅ Link encontrado (método 2)")
                        await link.click(timeout=10000)
                        orden_clickeado = True
                except Exception as e:
                    print(f"⚠️ Método 2 falló: {str(e)}")

            # Intento 3: Buscar en toda la página
            if not orden_clickeado:
                try:
                    all_links = await page.query_selector_all('a')
                    for link in all_links:
                        text = await link.text_content()
                        if text and 'Newly Received Orders' in text:
                            print(f"✅ Link encontrado (método 3)")
                            await link.click()
                            orden_clickeado = True
                            break
                except Exception as e:
                    print(f"⚠️ Método 3 falló: {str(e)}")

            if not orden_clickeado:
                # Obtener todos los links disponibles para debug
                all_links = await page.query_selector_all('a')
                links_text = []
                for link in all_links[:20]:  # Primeros 20 links
                    text = await link.text_content()
                    if text:
                        links_text.append(text.strip())

                raise Exception(f"❌ No se encontró el link 'Newly Received Orders'. Links disponibles: {', '.join(links_text[:10])}")

            # Paso 6: Esperar a que cargue la página de órdenes
            print(f"⏳ Esperando página de órdenes...")
            await page.wait_for_load_state('networkidle', timeout=60000)
            await page.wait_for_timeout(3000)

            # Paso 7: Esperar el filtro
            print(f"🔍 Buscando filtro de órdenes...")
            await page.wait_for_selector('select[name="ref_epo_filter"]', state='visible', timeout=30000)
            print(f"✅ Filtro encontrado")

            # Paso 8: Seleccionar filtro
            print(f"⚙️ Aplicando filtro...")
            await page.select_option('select[name="ref_epo_filter"]', label='Show All Except EPOs')
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state('networkidle', timeout=30000)
            print(f"✅ Filtro aplicado")

            # Paso 9: Extraer tabla
            print(f"📊 Extrayendo tabla de órdenes...")
            table_element = await page.query_selector('//th[contains(normalize-space(.), "Builder")]/ancestor::table')

            if not table_element:
                raise Exception("❌ No se encontró la tabla de órdenes. Puede que no haya órdenes disponibles.")

            # Obtener HTML de la tabla
            table_html = await table_element.inner_html()
            full_table_html = f"<table>{table_html}</table>"

            # Convertir a DataFrame SIN interpretar headers (igual que el código original)
            from io import StringIO
            import tempfile
            import os

            df = pd.read_html(StringIO(full_table_html), header=None)[0]
            print(f"✅ Extraídas {len(df)} filas")

            # Guardar a CSV temporal (como hace el código original)
            temp_csv = tempfile.mktemp(suffix='.csv')
            df.to_csv(temp_csv, index=False, encoding='utf-8-sig', header=False)
            print(f"✅ Guardado a CSV temporal")

            # Leer de vuelta SIN headers (como el código original)
            df_final = pd.read_csv(temp_csv, header=None, dtype=str, encoding='utf-8-sig')
            print(f"✅ Releído desde CSV: {len(df_final)} filas")

            # Limpiar archivo temporal
            try:
                os.remove(temp_csv)
            except:
                pass

            # Cerrar sesión
            try:
                await page.click('text=Sign Out', timeout=5000)
                await page.wait_for_timeout(1000)
            except:
                pass

            return df_final

        except Exception as e:
            # Capturar screenshot para debugging
            try:
                screenshot_bytes = await page.screenshot(full_page=True)
                # Guardar para debugging
                with open('/tmp/error_screenshot.png', 'wb') as f:
                    f.write(screenshot_bytes)
                error_msg = f"{str(e)}\n\n[DEBUG] Screenshot guardado en /tmp/error_screenshot.png"
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
