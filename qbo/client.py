"""
Cliente REST para QuickBooks Online API v3.
"""
import requests
from datetime import datetime, timedelta, timezone

from qbo import storage
from qbo import oauth as qbo_oauth
import logger as _log

_logger = _log.get(__name__)

QBO_BASE = "https://quickbooks.api.intuit.com/v3/company"
MINOR_VERSION = "75"


class QBOAuthError(Exception):
    pass


class QBOClient:
    def __init__(self):
        tokens = storage.get_tokens()
        if not tokens:
            raise QBOAuthError("No conectado a QuickBooks. Conecta desde el panel lateral.")

        self._access_token  = tokens["access_token"]
        self._refresh_token = tokens["refresh_token"]
        self._realm_id      = tokens["realm_id"]
        self._expires_at    = datetime.fromisoformat(tokens["expires_at"])

        self._item_cache         = {}  # name.lower() → id
        self._custom_field_ids   = None  # {field_name → DefinitionId}
        self._sales_term_net15   = None  # SalesTermRef id for Net 15

        self._maybe_refresh()

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _maybe_refresh(self) -> None:
        now = datetime.now(timezone.utc)
        if self._expires_at - now < timedelta(minutes=5):
            try:
                data = qbo_oauth.refresh_tokens(self._refresh_token, self._realm_id)
                qbo_oauth.save_token_response(data)
                self._access_token = data["access_token"]
                self._refresh_token = data["refresh_token"]
                expires_in = int(data.get("expires_in", 3600))
                self._expires_at = now + timedelta(seconds=expires_in)
            except Exception as e:
                raise QBOAuthError(f"Token QBO expirado y no se pudo renovar: {e}")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept":        "application/json",
            "Content-Type":  "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{QBO_BASE}/{self._realm_id}/{path}"

    # ── Low-level API ─────────────────────────────────────────────────────────

    def query(self, sql: str) -> list:
        resp = requests.get(
            self._url("query"),
            params={"query": sql, "minorversion": MINOR_VERSION},
            headers=self._headers(),
            timeout=30,
        )
        if resp.status_code == 401:
            raise QBOAuthError("Token QBO inválido. Reconecta QBO.")
        resp.raise_for_status()
        data = resp.json()
        qr = data.get("QueryResponse", {})
        for key, val in qr.items():
            if isinstance(val, list):
                return val
        return []

    def create(self, entity: str, body: dict) -> dict:
        resp = requests.post(
            self._url(entity.lower()),
            params={"minorversion": MINOR_VERSION},
            headers=self._headers(),
            json=body,
            timeout=30,
        )
        if resp.status_code == 401:
            raise QBOAuthError("Token QBO inválido. Reconecta QBO.")
        if not resp.ok:
            try:
                fault = resp.json().get("Fault", {})
                msg = fault.get("Error", [{}])[0].get("Detail", resp.text)
            except Exception:
                msg = resp.text
            raise Exception(f"QBO {entity} error {resp.status_code}: {msg}")
        data = resp.json()
        # QBO wraps the created entity in a key matching the entity name (capitalized)
        for key in (entity, entity.capitalize(), entity.title()):
            if key in data:
                return data[key]
        return data

    def fetch_company_info(self) -> dict:
        results = self.query("SELECT * FROM CompanyInfo")
        return results[0] if results else {}

    # ── Customers ─────────────────────────────────────────────────────────────

    def find_customer_by_name(self, display_name: str) -> dict | None:
        safe = display_name.replace("'", "\\'")
        results = self.query(f"SELECT * FROM Customer WHERE DisplayName = '{safe}' MAXRESULTS 1")
        return results[0] if results else None

    def find_customers_like(self, prefix: str, parent_only: bool = False) -> list:
        safe = prefix.replace("'", "\\'").replace("%", "\\%")
        sql = f"SELECT * FROM Customer WHERE DisplayName LIKE '{safe}%' MAXRESULTS 10"
        results = self.query(sql)
        if parent_only:
            results = [r for r in results if not r.get("Job")]
        return results

    def create_customer(self, display_name: str, parent_id: str = "") -> dict:
        body: dict = {"DisplayName": display_name}
        if parent_id:
            body["Job"] = True
            body["ParentRef"] = {"value": parent_id}
            body["BillWithParent"] = True
        return self.create("Customer", body)

    def get_or_create_parent_customer(self, builder_name: str) -> str:
        # Exact match first
        c = self.find_customer_by_name(builder_name)
        if c and not c.get("Job"):
            return c["Id"]
        # LIKE match (handles "Lennar Homes" matching "Lennar Homes LLC")
        matches = self.find_customers_like(builder_name, parent_only=True)
        if matches:
            return matches[0]["Id"]
        result = self.create_customer(builder_name)
        _logger.info("QBO: cliente creado — %s (id=%s)", builder_name, result["Id"])
        return result["Id"]

    def get_or_create_sub_customer(self, community_name: str, parent_id: str) -> str:
        c = self.find_customer_by_name(community_name)
        if c:
            return c["Id"]
        result = self.create_customer(community_name, parent_id=parent_id)
        _logger.info("QBO: sub-cliente creado — %s (id=%s)", community_name, result["Id"])
        return result["Id"]

    def resolve_customer_id(self, builder: str, community: str) -> str:
        """Returns the QBO customer ID to use for the invoice."""
        parent_id = self.get_or_create_parent_customer(builder)
        if community:
            return self.get_or_create_sub_customer(community, parent_id)
        return parent_id

    # ── Items (Products & Services) ───────────────────────────────────────────

    def get_or_create_item(self, name: str) -> str:
        key = name.lower()
        if key in self._item_cache:
            return self._item_cache[key]

        results = self.query(f"SELECT * FROM Item WHERE Name = '{name.replace(chr(39), chr(92)+chr(39))}' AND Active = true MAXRESULTS 1")
        if results:
            item_id = results[0]["Id"]
            self._item_cache[key] = item_id
            return item_id

        # Find an income account to attach
        accounts = self.query("SELECT * FROM Account WHERE AccountType = 'Income' AND Active = true MAXRESULTS 1")
        income_ref = {"value": accounts[0]["Id"]} if accounts else {"name": "Services"}

        body = {
            "Name": name,
            "Type": "Service",
            "IncomeAccountRef": income_ref,
        }
        result = self.create("Item", body)
        item_id = result["Id"]
        self._item_cache[key] = item_id
        _logger.info("QBO: item creado — %s (id=%s)", name, item_id)
        return item_id

    # ── Custom Fields ─────────────────────────────────────────────────────────

    def get_custom_field_ids(self) -> dict:
        """Reads custom field DefinitionIds from QBO Preferences (reliable, no invoice needed)."""
        if self._custom_field_ids is not None:
            return self._custom_field_ids

        resp = requests.get(
            self._url("preferences"),
            params={"minorversion": MINOR_VERSION},
            headers=self._headers(),
            timeout=30,
        )
        if resp.status_code == 401:
            raise QBOAuthError("Token QBO inválido. Reconecta QBO.")
        resp.raise_for_status()

        prefs        = resp.json().get("Preferences", {})
        sales_prefs  = prefs.get("SalesFormsPrefs", {})
        custom_fields = sales_prefs.get("CustomField", [])

        mapping = {}
        for f in custom_fields:
            name   = f.get("Name", "")
            def_id = f.get("DefinitionId", "")
            # BooleanValue=True means the field is enabled in this company
            if name and def_id and f.get("BooleanValue"):
                mapping[name] = def_id

        self._custom_field_ids = mapping
        _logger.info("QBO: custom fields desde Preferences: %s", mapping)
        return mapping

    # ── Sales Terms ───────────────────────────────────────────────────────────

    def get_net15_term_id(self) -> str | None:
        if self._sales_term_net15 is not None:
            return self._sales_term_net15

        terms = self.query("SELECT * FROM Term WHERE Active = true")
        for t in terms:
            name = (t.get("Name") or "").lower()
            if "net 15" in name or "net15" in name:
                self._sales_term_net15 = t["Id"]
                return t["Id"]
        return None

    # ── Invoices ──────────────────────────────────────────────────────────────

    def create_invoice(
        self,
        customer_id: str,
        txn_date: str,
        amount: float,
        service_type: str,
        order_number: str,
    ) -> dict:
        item_id   = self.get_or_create_item(service_type)
        cf_ids    = self.get_custom_field_ids()
        term_id   = self.get_net15_term_id()

        # Due date = txn_date + 15 days
        from datetime import date
        txn = date.fromisoformat(txn_date)
        due = (txn + timedelta(days=15)).isoformat()

        body: dict = {
            "CustomerRef": {"value": customer_id},
            "TxnDate":     txn_date,
            "DueDate":     due,
            "PrivateNote": service_type,
            "Line": [{
                "Amount":     round(amount, 2),
                "DetailType": "SalesItemLineDetail",
                "Description": service_type,
                "SalesItemLineDetail": {
                    "ItemRef":   {"value": item_id},
                    "Qty":       1,
                    "UnitPrice": round(amount, 2),
                },
            }],
        }

        if term_id:
            body["SalesTermRef"] = {"value": term_id}

        # Build custom fields from discovered IDs
        custom_fields = []
        cf_map = {
            "ORDER NUMBER":  order_number,
            "FECHA ENVIADO": "",
            "NOTAS":         "",
        }
        for field_name, field_value in cf_map.items():
            def_id = cf_ids.get(field_name)
            if def_id:
                custom_fields.append({
                    "DefinitionId": def_id,
                    "Name":         field_name,
                    "Type":         "StringType",
                    "StringValue":  field_value,
                })
        if custom_fields:
            body["CustomField"] = custom_fields

        return self.create("Invoice", body)
