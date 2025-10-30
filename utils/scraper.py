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
        # Lanzar navegador en modo headless
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Login
            await page.goto(SUPPLYPRO_URL, timeout=30000)
            await page.fill('#user_name', username)
            await page.fill('#password', password)
            await page.click('input[type="submit"]')
            await page.wait_for_timeout(5000)

            # Navegar a órdenes
            await page.click('text=Newly Received Orders')
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

        finally:
            await browser.close()


def ejecutar_extraccion(username: str, password: str) -> pd.DataFrame:
    """
    Wrapper síncrono para la función asíncrona de extracción
    """
    return asyncio.run(extraer_ordenes(username, password))
