"""
Parser del Jobber Visits Report para generar facturas en QBO.
"""
import math
import pandas as pd
from datetime import datetime


def parse_visits_csv(df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    """
    Filtra y convierte las filas del Visits Report en dicts listos para create_invoice.

    Returns (parsed_rows, skipped_rows).
    skipped_rows: list of {title, reason} for debugging.

    Filas excluidas:
    - ORDER NUMBER (columna) == 'EPO'
    - One-off job ($) vacío o <= 0
    - Visit title no parseable
    - Fecha no parseable
    """
    rows = []
    skipped = []
    for _, row in df.iterrows():
        title = str(row.get("Visit title", "") or "").strip()
        order_num_col = str(row.get("ORDER NUMBER", "") or "").strip().upper()

        if order_num_col == "EPO":
            skipped.append({"title": title, "reason": "EPO"})
            continue

        try:
            amount = float(row.get("One-off job ($)") or 0)
        except (ValueError, TypeError):
            skipped.append({"title": title, "reason": "monto inválido"})
            continue
        if math.isnan(amount) or amount <= 0:
            skipped.append({"title": title, "reason": f"monto vacío o ≤ 0 ({row.get('One-off job ($)')})"})
            continue

        parsed = _parse_visit_title(title)
        if not parsed:
            skipped.append({"title": title, "reason": "título no parseable (falta ' - ')"})
            continue

        txn_date = _parse_date(str(row.get("Date", "") or "").strip())
        if not txn_date:
            skipped.append({"title": title, "reason": f"fecha no parseable ({row.get('Date')})"})
            continue

        # order_number: prefer from title, fall back to ORDER NUMBER column
        order_number = parsed["order_number"]
        if not order_number and order_num_col not in ("", "INVOICE"):
            order_number = order_num_col

        # cleaner: first word of "Assigned to" column, uppercased
        assigned = str(row.get("Assigned to", "") or "").strip()
        cleaner  = assigned.split()[0].upper() if assigned else ""

        rows.append({
            "title":        title,
            "builder":      parsed["builder"],
            "service_type": parsed["service_type"],
            "community":    parsed["community"],
            "lot":          parsed["lot"],
            "order_number": order_number,
            "amount":       amount,
            "txn_date":     txn_date,
            "cleaner":      cleaner,
        })

    return rows, skipped


def _parse_visit_title(title: str) -> dict | None:
    """
    Parse: 'Builder - SERVICE TYPE / LOT xxx / Community / order-number'

    Returns dict with keys: builder, service_type, community, lot, order_number
    """
    if not title:
        return None

    segments = [s.strip() for s in title.split(" / ")]

    # First segment: "Builder - ... - SERVICE TYPE"
    first = segments[0]
    parts = [p.strip() for p in first.split(" - ")]
    if len(parts) < 2:
        return None

    service_type = parts[-1]
    builder      = " - ".join(parts[:-1])

    rest = segments[1:]  # Everything after the first segment

    # Extract lot number from first rest segment if it starts with "LOT"
    lot = ""
    if rest and rest[0].upper().startswith("LOT"):
        lot_parts = rest[0].split()
        if len(lot_parts) >= 2:
            lot = lot_parts[1]

    community    = ""
    order_number = ""

    if len(rest) >= 3:
        # Pattern: [LOT, community, order_number, ...]
        community    = rest[-2]
        order_number = rest[-1]
    elif len(rest) == 2:
        # Pattern: [something, community] — last is community
        community = rest[-1]
    elif len(rest) == 1:
        # Pattern: [LOT/location] — skip if starts with LOT
        if not rest[0].upper().startswith("LOT"):
            community = rest[0]

    return {
        "builder":      builder,
        "service_type": service_type,
        "community":    community,
        "lot":          lot,
        "order_number": order_number,
    }


_DATE_FORMATS = ["%b %d, %Y", "%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y"]


def _parse_date(date_str: str) -> str | None:
    """Convierte 'Apr 17, 2026' → '2026-04-17'. Devuelve None si no puede parsear."""
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None
