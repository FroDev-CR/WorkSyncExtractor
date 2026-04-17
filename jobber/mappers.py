"""
Mapea filas del DataFrame de ShineAndBright a variables GraphQL de Jobber.
"""
import re
from datetime import datetime, timezone


def parse_total(raw: str) -> float:
    """Limpia '$1,234.56' → 1234.56. Lanza ValueError si no parsea."""
    cleaned = re.sub(r"[^\d.]", "", str(raw))
    if not cleaned:
        raise ValueError(f"No se pudo parsear el total: {repr(raw)}")
    return float(cleaned)


def parse_date_iso(raw: str) -> str:
    """Convierte 'MM/DD/YYYY' → 'YYYY-MM-DDT00:00:00Z'. Devuelve '' si falla."""
    raw = str(raw).strip()
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", raw)
    if not match:
        return ""
    m, d, y = match.groups()
    return f"{y}-{int(m):02d}-{int(d):02d}T00:00:00Z"


def parse_address(raw: str) -> dict:
    """
    Intenta separar 'NÚMERO CALLE, CIUDAD, ESTADO ZIP' en campos.
    Jobber acepta solo street1 si no se puede parsear más.
    """
    raw = str(raw).strip()
    parts = [p.strip() for p in raw.split(",")]

    street1 = parts[0] if len(parts) > 0 else raw
    city    = parts[1] if len(parts) > 1 else ""
    # Último fragmento puede ser "TX 78610" o "TX"
    province = ""
    postal   = ""
    if len(parts) > 2:
        state_zip = parts[-1].strip().split()
        province  = state_zip[0] if state_zip else ""
        postal    = state_zip[1] if len(state_zip) > 1 else ""

    return {
        "street1":    street1,
        "city":       city,
        "province":   province,
        "postalCode": postal,
        "country":    "US",
    }


def addresses_match(stored: dict, candidate: str) -> bool:
    """Compara street1 de una Property guardada contra la dirección candidata."""
    stored_street = (stored.get("street1") or "").strip().lower()
    candidate_street = parse_address(candidate).get("street1", "").strip().lower()
    return stored_street == candidate_street


def map_row_to_job_input(row: dict, client_id: str, property_id: str) -> dict:
    """
    Construye el dict de atributos para la mutation jobCreate.

    row debe tener: Client Name, Job title Final, Full Property Address, total, Start Date
    """
    unit_price = parse_total(row["total"])
    start_iso  = parse_date_iso(row["Start Date"])

    attributes: dict = {
        "clientId":   client_id,
        "title":      row["Job title Final"],
        "propertyId": property_id,
        "lineItems": [
            {
                "name":        "Cleaning Service",
                "description": row["Job title Final"],
                "quantity":    1,
                "unitPrice":   unit_price,
            }
        ],
    }

    if start_iso:
        attributes["startAt"] = start_iso

    return attributes


def validate_row(row: dict) -> str | None:
    """Devuelve mensaje de error si la fila tiene datos inválidos, None si está ok."""
    try:
        parse_total(row["total"])
    except ValueError as e:
        return str(e)
    if not str(row.get("Full Property Address", "")).strip():
        return "Dirección vacía"
    if not str(row.get("Client Name", "")).strip():
        return "Cliente vacío"
    return None
