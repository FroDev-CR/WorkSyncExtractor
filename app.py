"""
SupplyPro Extractor - Versión Web con Streamlit
"""
import streamlit as st
import pandas as pd
from io import BytesIO
import subprocess
import sys
from pathlib import Path

# Instalar Playwright browsers en primera ejecución
@st.cache_resource
def install_playwright():
    """Instala los navegadores de Playwright si no están instalados"""
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True
        )
    except Exception as e:
        st.warning(f"Nota: {str(e)}")

# Instalar Playwright al inicio
install_playwright()

from config import CREDENTIALS
from utils.scraper import ejecutar_extraccion
from utils.transformer import transformar_ordenes


# Configuración de la página
st.set_page_config(
    page_title="SupplyPro Extractor",
    page_icon="📦",
    layout="centered"
)

# Inicializar estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'df_result' not in st.session_state:
    st.session_state.df_result = None


def login_page():
    """Página de autenticación simple"""
    st.title("🔐 SupplyPro Extractor")
    st.markdown("### Acceso al sistema")

    # Sistema de autenticación simple con contraseña
    password = st.text_input("Ingresa tu clave de acceso", type="password")

    # Puedes configurar esto en secrets de Streamlit
    valid_keys = st.secrets.get("license_keys", ["X30XH3-S9JH34", "TU-LLAVE-2"])

    if st.button("Acceder", type="primary"):
        if password.strip().upper() in [k.upper() for k in valid_keys]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Clave incorrecta. Intenta nuevamente.")


def main_page():
    """Página principal de la aplicación"""
    st.title("📦 SupplyPro Extractor")
    st.markdown("### Extracción y transformación de órdenes")

    # Botón de logout en sidebar
    with st.sidebar:
        st.markdown("### Sesión")
        if st.button("🚪 Cerrar sesión"):
            st.session_state.authenticated = False
            st.session_state.df_result = None
            st.rerun()

        st.markdown("---")
        st.markdown("### Información")
        st.info("Desarrollado por FroDev")

    # Selector de configuración
    config = st.radio(
        "Selecciona la configuración:",
        ["ShineAndBright", "Apex"],
        horizontal=True
    )

    st.markdown("---")

    # Botón principal de extracción
    if st.button("🚀 Exportar órdenes de SupplyPro", type="primary", use_container_width=True):
        with st.spinner(f"Extrayendo órdenes de {config}..."):
            try:
                # Obtener credenciales
                creds = CREDENTIALS[config]
                username = creds['username']
                password = creds['password']

                # Extraer datos
                st.info("⏳ Conectando a SupplyPro...")
                df_raw = ejecutar_extraccion(username, password)

                # Transformar datos
                st.info("⚙️ Procesando órdenes...")
                df_final = transformar_ordenes(df_raw, config)

                # Guardar resultado
                st.session_state.df_result = df_final
                st.session_state.config_name = config

                st.success(f"✅ ¡Operación completada! Se encontraron {len(df_final)} órdenes.")

            except Exception as e:
                st.error(f"❌ Error en la extracción: {str(e)}")

    # Mostrar resultados si existen
    if st.session_state.df_result is not None:
        st.markdown("---")
        st.markdown("### 📊 Resultados")

        df = st.session_state.df_result

        # Mostrar preview
        st.dataframe(df, use_container_width=True, height=400)

        # Estadísticas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total órdenes", len(df))
        with col2:
            st.metric("Clientes únicos", df['Client Name'].nunique())
        with col3:
            total_amount = df['total'].str.replace('$', '').str.replace(',', '').astype(float).sum()
            st.metric("Total $", f"${total_amount:,.2f}")

        # Botones de descarga
        st.markdown("### 💾 Descargar")

        col1, col2 = st.columns(2)

        with col1:
            # Descargar CSV
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"ordenes_{st.session_state.config_name}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Descargar Excel
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            st.download_button(
                label="📥 Descargar Excel",
                data=buffer,
                file_name=f"ordenes_{st.session_state.config_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    # Información adicional en expander
    with st.expander("ℹ️ Cómo usar esta aplicación"):
        st.markdown("""
        **Pasos:**
        1. Selecciona la configuración (ShineAndBright o Apex)
        2. Haz clic en "Exportar órdenes de SupplyPro"
        3. Espera a que se extraigan y procesen las órdenes
        4. Revisa los resultados y descarga el archivo CSV o Excel

        **Nota:** Las credenciales de acceso a SupplyPro están configuradas automáticamente.
        """)


# Enrutador principal
if st.session_state.authenticated:
    main_page()
else:
    login_page()
