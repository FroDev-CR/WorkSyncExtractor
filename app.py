"""
ShineAndBright — SupplyPro Extractor
"""
import streamlit as st
import pandas as pd
from io import BytesIO
import subprocess
import sys


# ── Playwright install (solo primera vez en Streamlit Cloud) ──────────────────
@st.cache_resource
def install_playwright():
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
        )
    except Exception as e:
        st.warning(f"Playwright setup: {e}")


install_playwright()

from i18n import t
from config import SUPPLYPRO_USERNAME, SUPPLYPRO_PASSWORD
from scraper import ejecutar_extraccion
from transformer import transformar_ordenes


# ── CSS responsive (colapsa columnas en móvil) ────────────────────────────────
MOBILE_CSS = """
<style>
/* En pantallas angostas, los st.columns se apilan verticalmente */
@media (max-width: 640px) {
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    [data-testid="stMetric"] {
        margin-bottom: 0.5rem;
    }
}
/* Sidebar más compacta en móvil */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        min-width: 200px !important;
    }
}
</style>
"""


# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="ShineAndBright — SupplyPro",
    page_icon="✨",
    layout="wide",
)

st.markdown(MOBILE_CSS, unsafe_allow_html=True)


# ── Inicializar session_state ─────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "es"
if "df_result" not in st.session_state:
    st.session_state.df_result = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✨ ShineAndBright")
    st.markdown("---")

    # Toggle de idioma
    st.caption(t("sidebar_lang"))
    lang_choice = st.radio(
        label="lang",
        options=["🇪🇸 Español", "🇬🇧 English"],
        index=0 if st.session_state.lang == "es" else 1,
        label_visibility="collapsed",
    )
    st.session_state.lang = "es" if lang_choice.startswith("🇪🇸") else "en"

    st.markdown("---")
    # Placeholder para estado de Jobber (se poblará en Fase 2)
    st.caption(t("sidebar_jobber_status"))
    st.info(t("jobber_not_connected"))


# ── Contenido principal ───────────────────────────────────────────────────────
st.title(t("app_title"))
st.markdown(f"### {t('app_subtitle')}")
st.markdown("---")

if st.button(t("btn_export"), type="primary", use_container_width=True):
    with st.spinner(t("spinner_extracting")):
        try:
            st.info(t("info_connecting"))
            df_raw = ejecutar_extraccion(SUPPLYPRO_USERNAME, SUPPLYPRO_PASSWORD)

            st.info(t("info_processing"))
            df_final = transformar_ordenes(df_raw, "ShineAndBright")

            if len(df_final) == 0:
                st.warning(t("warning_no_orders"))
                st.session_state.df_result = None
            else:
                st.session_state.df_result = df_final
                st.success(t("success_extracted", n=len(df_final)))

        except Exception as e:
            st.error(t("error_extraction", err=e))
            st.info(t("info_retry"))

# ── Resultados ────────────────────────────────────────────────────────────────
if st.session_state.df_result is not None:
    df = st.session_state.df_result

    st.markdown("---")
    st.markdown(f"### {t('section_results')}")
    st.dataframe(df, use_container_width=True, height=400)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("metric_total_orders"), len(df))
    with col2:
        st.metric(t("metric_unique_clients"), df["Client Name"].nunique())
    with col3:
        try:
            total_amt = (
                df["total"]
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .astype(float)
                .sum()
            )
            st.metric(t("metric_total_amount"), f"${total_amt:,.2f}")
        except Exception:
            st.metric(t("metric_total_amount"), "N/A")

    # ── Descargas ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### {t('section_download')}")

    col_csv, col_xlsx = st.columns(2)
    with col_csv:
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label=t("btn_csv"),
            data=csv_data.encode("utf-8-sig"),
            file_name="ordenes_shineandbright.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_xlsx:
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            label=t("btn_excel"),
            data=buffer,
            file_name="ordenes_shineandbright.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ── Ayuda ─────────────────────────────────────────────────────────────────────
with st.expander(t("help_title")):
    st.markdown(t("help_text"))

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center; color:gray;'>{t('footer')}</p>",
    unsafe_allow_html=True,
)
