"""
ShineAndBright — SupplyPro Extractor + Jobber Uploader
"""
import streamlit as st
import pandas as pd
from io import BytesIO, StringIO
import subprocess
import sys

import logger as _log
_log.setup()


# ── Playwright install ────────────────────────────────────────────────────────
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
from jobber import storage, oauth
from jobber.client import JobberClient, JobberAuthError
from jobber.mappers import parse_total, validate_row

# ── CSS responsive ────────────────────────────────────────────────────────────
MOBILE_CSS = """
<style>
@media (max-width: 640px) {
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    [data-testid="stMetric"] { margin-bottom: 0.5rem; }
}
@media (max-width: 768px) {
    section[data-testid="stSidebar"] { min-width: 200px !important; }
}
</style>
"""

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShineAndBright — SupplyPro",
    page_icon="✨",
    layout="wide",
)
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in [
    ("lang",         "es"),
    ("df_result",    None),
    ("df_editor",    None),   # DataFrame con columnas Subir + Ya subido
    ("upload_report", None),  # Resultados del último batch
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── OAuth callback ────────────────────────────────────────────────────────────
if oauth.handle_callback():
    if st.session_state.get("jobber_just_connected"):
        st.session_state.pop("jobber_just_connected", None)
        try:
            client = JobberClient()
            client.enrich_account_info()
            tokens = storage.get_tokens()
            account_name = tokens.get("account_name", "Jobber") if tokens else "Jobber"
            st.success(t("jobber_connect_success", account=account_name))
        except Exception as e:
            st.error(t("jobber_connect_error", err=e))
    elif err := st.session_state.pop("jobber_connect_error", None):
        st.error(t("jobber_connect_error", err=err))


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✨ ShineAndBright")
    st.markdown("---")

    st.caption(t("sidebar_lang"))
    lang_choice = st.radio(
        label="lang",
        options=["🇪🇸 Español", "🇬🇧 English"],
        index=0 if st.session_state.lang == "es" else 1,
        label_visibility="collapsed",
    )
    st.session_state.lang = "es" if lang_choice.startswith("🇪🇸") else "en"

    st.markdown("---")
    st.caption(t("sidebar_jobber_status"))

    tokens = storage.get_tokens()
    if tokens:
        account_name = tokens.get("account_name") or "Jobber"
        st.success(t("jobber_connected", account=account_name))

        col_test, col_disc = st.columns(2)
        with col_test:
            if st.button(t("btn_test_connection"), use_container_width=True):
                try:
                    client = JobberClient()
                    account = client.fetch_account()
                    st.toast(t("jobber_test_ok", account=account["name"]))
                except JobberAuthError:
                    st.warning(t("jobber_token_expired"))
                except Exception as e:
                    st.error(t("jobber_test_fail", err=e))
        with col_disc:
            if st.button(t("btn_disconnect_jobber"), use_container_width=True):
                storage.clear_tokens()
                st.rerun()
    else:
        st.info(t("jobber_not_connected"))
        auth_url, _ = oauth.build_auth_url()
        st.link_button(t("btn_connect_jobber"), auth_url, use_container_width=True)


# ── Contenido principal ───────────────────────────────────────────────────────
st.title(t("app_title"))
st.markdown(f"### {t('app_subtitle')}")
st.markdown("---")

# ── Extracción ────────────────────────────────────────────────────────────────
if st.button(t("btn_export"), type="primary", use_container_width=True):
    with st.spinner(t("spinner_extracting")):
        try:
            st.info(t("info_connecting"))
            df_raw = ejecutar_extraccion(SUPPLYPRO_USERNAME, SUPPLYPRO_PASSWORD)

            st.info(t("info_processing"))
            df_final = transformar_ordenes(df_raw, "ShineAndBright")

            if len(df_final) == 0:
                st.warning(t("warning_no_orders"))
                st.session_state.df_result  = None
                st.session_state.df_editor  = None
            else:
                st.session_state.df_result = df_final
                # Inicializar tabla editable con columnas de control
                df_edit = df_final.copy()
                df_edit.insert(0, t("col_upload"),   True)
                df_edit[t("col_uploaded")] = False
                st.session_state.df_editor  = df_edit
                st.session_state.upload_report = None
                st.success(t("success_extracted", n=len(df_final)))

        except Exception as e:
            st.error(t("error_extraction", err=e))
            st.info(t("info_retry"))


# ── Tabla editable ────────────────────────────────────────────────────────────
if st.session_state.df_editor is not None:
    df_edit = st.session_state.df_editor
    col_subir    = t("col_upload")
    col_uploaded = t("col_uploaded")

    st.markdown("---")
    st.markdown(f"### {t('section_results')}")

    # Detectar filas con total inválido para mostrar advertencia
    invalid_rows = []
    for i, row in df_edit.iterrows():
        err = validate_row(row.to_dict())
        if err:
            invalid_rows.append(f"Fila {i + 1} — {err}")
    if invalid_rows:
        st.warning("⚠️ " + " · ".join(invalid_rows))

    # Botones seleccionar / deseleccionar todas (solo filas no subidas)
    btn_all, btn_none, _ = st.columns([1, 1, 6])
    with btn_all:
        if st.button("☑ Todas", use_container_width=True):
            mask = st.session_state.df_editor[col_uploaded] == False
            st.session_state.df_editor.loc[mask, col_subir] = True
            st.rerun()
    with btn_none:
        if st.button("☐ Ninguna", use_container_width=True):
            mask = st.session_state.df_editor[col_uploaded] == False
            st.session_state.df_editor.loc[mask, col_subir] = False
            st.rerun()

    # Columnas configuradas para el editor
    col_config = {
        col_subir: st.column_config.CheckboxColumn(
            col_subir, help="Marcar para subir a Jobber", default=True
        ),
        col_uploaded: st.column_config.CheckboxColumn(
            col_uploaded, disabled=True
        ),
        "Client Name": st.column_config.TextColumn("Client Name", width="medium"),
        "Job title Final": st.column_config.TextColumn("Job Title", width="large"),
        "Full Property Address": st.column_config.TextColumn("Address", width="large"),
        "total": st.column_config.TextColumn("Total", width="small"),
        "Start Date": st.column_config.TextColumn("Start Date", width="small"),
    }

    edited = st.data_editor(
        df_edit,
        column_config=col_config,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="data_editor_widget",
    )
    # Persistir ediciones entre reruns
    st.session_state.df_editor = edited

    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("metric_total_orders"), len(edited))
    with col2:
        st.metric(t("metric_unique_clients"), edited["Client Name"].nunique())
    with col3:
        try:
            total_amt = (
                edited["total"]
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

    df_download = edited.drop(columns=[col_subir, col_uploaded], errors="ignore")
    col_csv, col_xlsx = st.columns(2)
    with col_csv:
        csv_data = df_download.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label=t("btn_csv"),
            data=csv_data.encode("utf-8-sig"),
            file_name="ordenes_shineandbright.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_xlsx:
        buffer = BytesIO()
        df_download.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            label=t("btn_excel"),
            data=buffer,
            file_name="ordenes_shineandbright.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # ── Botón Subir a Jobber ──────────────────────────────────────────────────
    pending_rows = edited[
        (edited[col_subir] == True) & (edited[col_uploaded] == False)
    ]
    jobber_connected = storage.has_tokens()

    if jobber_connected and len(pending_rows) > 0:
        st.markdown("---")
        if st.button(
            f"{t('btn_upload_jobber')} ({len(pending_rows)})",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["trigger_upload"] = True
            st.rerun()


# ── Upload a Jobber (se ejecuta en el siguiente rerun) ────────────────────────
if st.session_state.pop("trigger_upload", False):
    df_edit      = st.session_state.df_editor
    col_subir    = t("col_upload")
    col_uploaded = t("col_uploaded")
    pending      = df_edit[(df_edit[col_subir] == True) & (df_edit[col_uploaded] == False)]
    total_rows   = len(pending)

    progress_bar = st.progress(0)
    status_text  = st.empty()
    results      = []

    try:
        client = JobberClient()
    except JobberAuthError as e:
        st.error(str(e))
        st.stop()

    # Importar aquí para no cargar en cada rerun
    from jobber.mutations import (
        LIST_CLIENTS_QUERY, CREATE_CLIENT_MUTATION,
        FIND_PROPERTY_QUERY, CREATE_PROPERTY_MUTATION,
        CREATE_JOB_MUTATION,
    )
    from jobber.mappers import parse_total, parse_address, addresses_match, map_row_to_job_input
    import time

    # Cache de clients y properties para evitar queries repetidas
    client_cache   = {}  # nombre → id
    property_cache = {}  # (client_id, address) → property_id

    # Cargar todos los clientes una sola vez al inicio del batch
    status_text.info("Cargando clientes de Jobber...")
    all_clients = client.execute(LIST_CLIENTS_QUERY)["data"]["clients"]["nodes"]
    for node in all_clients:
        for key in (node.get("name") or "", node.get("companyName") or ""):
            if key:
                client_cache[key.lower()] = node["id"]

    def get_or_find_client(name: str) -> str:
        cached = client_cache.get(name.lower())
        if cached:
            return cached
        # No encontrado — crear
        res2 = client.execute(CREATE_CLIENT_MUTATION, {
            "input": {"companyName": name, "isCompany": True}
        })
        errors = res2["data"]["clientCreate"]["userErrors"]
        if errors:
            raise Exception(f"Error creando cliente '{name}': {errors[0]['message']}")
        new_id = res2["data"]["clientCreate"]["client"]["id"]
        client_cache[name] = new_id
        return new_id

    def get_or_create_property(client_id: str, address: str) -> str:
        cache_key = (client_id, address.strip().lower())
        if cache_key in property_cache:
            return property_cache[cache_key]

        result = client.execute(FIND_PROPERTY_QUERY, {"clientId": client_id})
        props  = result["data"]["client"]["clientProperties"]["nodes"]
        for prop in props:
            if addresses_match(prop["address"], address):
                property_cache[cache_key] = prop["id"]
                return prop["id"]

        # Crear nueva property
        addr_input = parse_address(address)
        res2 = client.execute(CREATE_PROPERTY_MUTATION, {
            "clientId": client_id,
            "input":    addr_input,
        })
        errors = res2["data"]["propertyCreate"]["userErrors"]
        if errors:
            raise Exception(f"Error creando property: {errors[0]['message']}")
        new_id = res2["data"]["propertyCreate"]["properties"][0]["id"]
        property_cache[cache_key] = new_id
        return new_id

    for i, (idx, row) in enumerate(pending.iterrows()):
        title = row["Job title Final"]
        status_text.info(t("upload_progress", i=i + 1, n=total_rows, title=title))
        progress_bar.progress((i) / total_rows)

        try:
            client_id   = get_or_find_client(row["Client Name"])
            property_id = get_or_create_property(client_id, row["Full Property Address"])
            attributes  = map_row_to_job_input(row.to_dict(), client_id, property_id)

            res = client.execute(CREATE_JOB_MUTATION, {"attributes": attributes})
            errors = res["data"]["jobCreate"]["userErrors"]
            if errors:
                raise Exception(errors[0]["message"])

            job_data = res["data"]["jobCreate"]["job"]
            results.append({
                "order":  title,
                "ok":     True,
                "number": job_data["jobNumber"],
                "url":    job_data["jobberWebUri"],
                "error":  "",
            })
            # Marcar como subido en el editor
            st.session_state.df_editor.at[idx, col_uploaded] = True
            st.session_state.df_editor.at[idx, col_subir]    = False

        except Exception as e:
            results.append({
                "order": title,
                "ok":    False,
                "number": "",
                "url":   "",
                "error": str(e),
            })

        time.sleep(0.3)  # Rate limit conservador

    progress_bar.progress(1.0)
    status_text.success(t("upload_complete"))
    st.session_state.upload_report = results


# ── Reporte de subida ─────────────────────────────────────────────────────────
if st.session_state.upload_report:
    results = st.session_state.upload_report
    st.markdown("---")
    st.markdown(f"### {t('section_upload_report')}")

    ok_count   = sum(1 for r in results if r["ok"])
    fail_count = len(results) - ok_count
    c1, c2 = st.columns(2)
    c1.metric("✅ Exitosas", ok_count)
    c2.metric("❌ Fallidas", fail_count)

    report_df = pd.DataFrame([
        {
            t("report_col_order"):  r["order"],
            t("report_col_status"): "✅" if r["ok"] else "❌",
            t("report_col_job"):    f"#{r['number']}" if r["ok"] else "",
            "Link":                 r["url"] if r["ok"] else "",
            t("report_col_error"):  r["error"],
        }
        for r in results
    ])

    st.dataframe(
        report_df,
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Abrir en Jobber"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # Descargar reporte
    report_csv = report_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label=t("btn_download_report"),
        data=report_csv.encode("utf-8-sig"),
        file_name="reporte_jobber.csv",
        mime="text/csv",
    )

    # Reintentar fallidas
    failed = [r for r in results if not r["ok"]]
    if failed and st.session_state.df_editor is not None:
        if st.button(t("btn_retry_failed")):
            df_edit = st.session_state.df_editor
            col_subir    = t("col_upload")
            col_uploaded = t("col_uploaded")
            failed_titles = {r["order"] for r in failed}
            mask = df_edit["Job title Final"].isin(failed_titles)
            st.session_state.df_editor.loc[mask, col_subir]    = True
            st.session_state.df_editor.loc[mask, col_uploaded] = False
            st.session_state.upload_report = None
            st.rerun()


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center; color:gray;'>{t('footer')}</p>",
    unsafe_allow_html=True,
)
