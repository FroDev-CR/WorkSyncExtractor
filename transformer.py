"""
Módulo de transformación de órdenes según reglas de negocio
"""
import re
import pandas as pd
from config import (
    SHINE_TASK_MAP,
    SHINE_CLIENT_MAP,
    SHINE_SUBDIVISION_MAP,
    APEX_INSTRUCTION_REGEX
)


def transformar_ordenes(df_raw: pd.DataFrame, config: str) -> pd.DataFrame:
    """
    Transforma el DataFrame crudo según las reglas del cliente

    Args:
        df_raw: DataFrame con datos crudos de SupplyPro
        config: 'ShineAndBright' o 'Apex'

    Returns:
        DataFrame transformado y listo para exportar
    """
    try:
        # Extraer datos relevantes (filas después de encabezado)
        sub = df_raw.iloc[57:-4].reset_index(drop=True) if len(df_raw) > 61 else df_raw.copy()

        # Limpiar encabezados
        headers = [str(x).strip().replace('\n', ' ') for x in sub.iloc[0]]
        df = sub.iloc[1:].copy()
        df.columns = headers

        print(f"📋 Columnas disponibles: {list(df.columns)}")

        # Limpiar todas las celdas
        df = df.applymap(lambda v: str(v).strip().replace('\n', ' '))

        # Mapeo de columnas con múltiples opciones
        column_mappings = {
            'Number order': ['Builder Order #', 'Builder Order', 'Order #'],
            'Client Name': ['Account', 'Client', 'Builder'],
            'Job title': ['Subdivision', 'Project', 'Job'],
            'lote number': ['Lot / Block Plan/Elv/Swing', 'Lot', 'Lot/Block', 'Lot Number'],
            'Job Address': ['Job Address', 'Address', 'Property Address'],
            'instruction': ['Task Task Filter', 'Task', 'Task Filter'],
            'total': ['Total Excl Tax', 'Total', 'Amount'],
            'Start Date': ['Request Acknowledged Actual', 'Start Date', 'Date', 'Request Date']
        }

        # Renombrar columnas encontrando la primera que exista
        rename_dict = {}
        for target_name, possible_names in column_mappings.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    rename_dict[possible_name] = target_name
                    break

        df.rename(columns=rename_dict, inplace=True)
        print(f"✅ Columnas después de renombrar: {list(df.columns)}")

        # Verificar que existan las columnas esenciales
        required_columns = ['Number order', 'Client Name', 'Job title', 'lote number', 'instruction', 'total']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise Exception(f"Faltan columnas esenciales: {', '.join(missing_columns)}")

        # Eliminar columnas irrelevantes
        drop_cols = [c for c in df.columns if any(x in c for x in ['Supplier Order', 'Order Status', 'Builder Status'])]
        df.drop(columns=drop_cols, inplace=True, errors='ignore')

        # Extraer solo la fecha (formato MM/DD/YYYY) - solo si existe
        if 'Start Date' in df.columns:
            df['Start Date'] = df['Start Date'].apply(
                lambda x: re.search(r"\d{1,2}/\d{1,2}/\d{4}", x).group(0)
                if re.search(r"\d{1,2}/\d{1,2}/\d{4}", x) else ''
            )
        else:
            df['Start Date'] = ''  # Columna vacía si no existe

        # Full Property Address
        if 'Job Address' in df.columns:
            df['Full Property Address'] = df['Job Address']\
                .str.replace("Lennar Options from CRM", "", regex=False)\
                .str.strip()
            df.drop(columns=['Job Address'], inplace=True, errors='ignore')
        else:
            df['Full Property Address'] = ''

        # Limpiar Client Name usando el mapa
        if 'Client Name' in df.columns:
            df['Client Name'] = df['Client Name'].apply(
                lambda x: next((rep for pat, rep in SHINE_CLIENT_MAP.items() if re.match(pat, x)), x)
            )

        # Limpiar instruction (quitar paréntesis y códigos)
        if 'instruction' in df.columns:
            df['instruction'] = df['instruction']\
                .str.replace(r"\s*[\(\[].*?[\)\]]", "", regex=True)\
                .str.strip()

            # Aplicar mapa de tareas Shine
            df['instruction'] = df['instruction'].apply(lambda x: SHINE_TASK_MAP.get(x, x))

            # Reglas específicas para Apex
            if config == 'Apex':
                df['instruction'] = df['instruction'].str.replace(r'^Concrete Labor -\s*', '', regex=True)
                for pattern, repl in APEX_INSTRUCTION_REGEX:
                    df['instruction'] = df['instruction'].str.replace(pattern, repl, regex=True)

        # Limpiar Job title
        if 'Job title' in df.columns:
            df['job_title_clean'] = df['Job title']\
                .str.replace(r'^GAL\s*-\s*', '', regex=True)\
                .str.replace(r'\s*-\s*\d+$', '', regex=True)\
                .str.strip()
        else:
            df['job_title_clean'] = ''

        # Extraer solo el lote (antes del /)
        if 'lote number' in df.columns:
            df['lote number'] = df['lote number'].str.partition('/')[0].str.strip()

        # Construir Job title Final
        df['Job title Final'] = df.apply(
            lambda r: f"{r.get('instruction', '')} / LOT {r.get('lote number', '')} / {r.get('job_title_clean', '')} / {r.get('Number order', '')}",
            axis=1
        )

        # Filtrar filas inválidas
        if 'Number order' in df.columns:
            df = df[
                df['Number order'].notna() &
                df['Number order'].str.strip().ne('') &
                (df['Number order'].str.lower() != 'nan')
            ]

        # Seleccionar columnas finales (solo las que existan)
        final_columns = []
        for col in ['Client Name', 'Job title Final', 'Full Property Address', 'total', 'Start Date']:
            if col in df.columns:
                final_columns.append(col)

        if not final_columns:
            raise Exception("No se pudieron construir las columnas finales")

        final = df[final_columns]

        # Eliminar filas con 'nan' en cualquier columna
        final = final[~final.apply(lambda row: row.astype(str).str.lower().eq('nan').any(), axis=1)]

        print(f"✅ Procesamiento completado: {len(final)} órdenes")
        return final

    except Exception as e:
        print(f"❌ Error en transformación: {str(e)}")
        raise Exception(f"Error al procesar órdenes: {str(e)}")
