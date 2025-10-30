"""
Módulo de transformación de órdenes según reglas de negocio
"""
import re
import sys
import pandas as pd
from config import (
    SHINE_TASK_MAP,
    SHINE_CLIENT_MAP,
    SHINE_SUBDIVISION_MAP,
    APEX_INSTRUCTION_REGEX
)

def log(msg):
    """Log que SÍ se ve en Streamlit Cloud"""
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()


def transformar_ordenes(df_raw: pd.DataFrame, config: str) -> pd.DataFrame:
    """
    Transforma el DataFrame crudo según las reglas del cliente

    Replica EXACTAMENTE el proceso del código original de Python
    """
    try:
        # Replicar el proceso original: extraer desde fila 57
        sub = df_raw.iloc[57:-4].reset_index(drop=True) if len(df_raw) > 61 else df_raw.copy()

        # Los headers están en la primera fila
        headers = [str(x).strip().replace('\n', ' ') for x in sub.iloc[0]]
        df = sub.iloc[1:].copy()
        df.columns = headers
        df = df.map(lambda v: str(v).strip().replace('\n', ' '))

        log(f"✅ COLUMNAS ORIGINALES: {list(df.columns)}")

        # Renombrar columnas EXACTAMENTE como el original
        rename_map = {
            'Builder Order #': 'Number order',
            'Account': 'Client Name',
            'Subdivision': 'Job title',
            'Lot / Block Plan/Elv/Swing': 'lote number',
            'Job Address': 'Job Address',
            'Task Task Filter': 'instruction',
            'Total Excl Tax': 'total',
            'Request Acknowledged Actual': 'Start Date'
        }

        df.rename(columns=rename_map, inplace=True)
        log(f"✅ DESPUÉS DE RENOMBRAR: {list(df.columns)}")

        # Eliminar columnas irrelevantes
        drop_cols = [c for c in df.columns if any(x in c for x in ['Supplier Order', 'Order Status', 'Builder Status'])]
        df.drop(columns=drop_cols, inplace=True)

        # Extraer solo la fecha (formato MM/DD/YYYY) - solo si existe la columna
        if 'Start Date' in df.columns:
            df['Start Date'] = df['Start Date'].apply(
                lambda x: re.search(r"\d{1,2}/\d{1,2}/\d{4}", x).group(0)
                if re.search(r"\d{1,2}/\d{1,2}/\d{4}", x) else ''
            )
        else:
            # Si no existe, buscar columnas con 'date' o 'request' en el nombre
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'request' in col.lower() or 'acknowledged' in col.lower()]
            log(f"⚠️ 'Start Date' no encontrada. Columnas con fecha disponibles: {date_cols}")

            if date_cols:
                # Tomar la primera columna que parezca una fecha
                df['Start Date'] = df[date_cols[0]].apply(
                    lambda x: re.search(r"\d{1,2}/\d{1,2}/\d{4}", str(x)).group(0)
                    if re.search(r"\d{1,2}/\d{1,2}/\d{4}", str(x)) else ''
                )
            else:
                # Si definitivamente no hay, dejar vacío
                df['Start Date'] = ''

        # Full Property Address sin subdividir y quitar Lennar Options from CRM
        df['Full Property Address'] = df['Job Address']\
            .str.replace("Lennar Options from CRM", "", regex=False)\
            .str.strip()
        df.drop(columns=['Job Address'], inplace=True)

        # Limpieza de Client Name
        df['Client Name'] = df['Client Name'].apply(
            lambda x: next((rep for pat, rep in SHINE_CLIENT_MAP.items() if re.match(pat, x)), x)
        )

        # Limpieza de instruction y Shine map
        df['instruction'] = df['instruction']\
            .str.replace(r"\s*[\(\[].*?[\)\]]", "", regex=True)\
            .str.strip()
        df['instruction'] = df['instruction'].apply(lambda x: SHINE_TASK_MAP.get(x, x))

        if config == 'Apex':
            df['instruction'] = df['instruction'].str.replace(r'^Concrete Labor -\s*', '', regex=True)
            for pattern, repl in APEX_INSTRUCTION_REGEX:
                df['instruction'] = df['instruction'].str.replace(pattern, repl, regex=True)

        # Limpieza de Job title
        df['job_title_clean'] = df['Job title']\
            .str.replace(r'^GAL\s*-\s*', '', regex=True)\
            .str.replace(r'\s*-\s*\d+$', '', regex=True)\
            .str.strip()

        # Lote number previo a /
        df['lote number'] = df['lote number'].str.partition('/')[0].str.strip()

        # Construir Job title Final
        df['Job title Final'] = df.apply(
            lambda r: f"{r['instruction']} / LOT {r['lote number']} / {r['job_title_clean']} / {r['Number order']}",
            axis=1
        )

        # Filtrado de filas inválidas
        df = df[
            df['Number order'].notna() &
            df['Number order'].str.strip().ne('') &
            (df['Number order'].str.lower() != 'nan')
        ]

        # Seleccionar columnas finales y eliminar nan
        final = df[['Client Name', 'Job title Final', 'Full Property Address', 'total', 'Start Date']]
        final = final[~final.apply(lambda row: row.astype(str).str.lower().eq('nan').any(), axis=1)]

        log(f"✅ Procesamiento completado: {len(final)} órdenes")
        return final

    except Exception as e:
        log(f"❌ Error en transformación: {str(e)}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise Exception(f"Error al procesar órdenes: {str(e)}")
