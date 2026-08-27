from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, urlparse

import frappe
import httpx
from frappe.utils import get_datetime, now_datetime
from frappe.utils.password import set_encrypted_password

STATE_TTL_SECONDS = 600
CONNECTION_DOCTYPE = "Financial AI Salesforce Connection"


def _https_url(value: str) -> str:
    parsed = urlparse((value or "").strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("A valid HTTPS Salesforce URL is required.")
    return value.rstrip("/")


def _verifier() -> str:
    return secrets.token_urlsafe(64)[:96]


def _challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


class SalesforceOAuthService:
    def __init__(self, connector: str):
        self.connector = frappe.get_doc("CRM Connector", connector)
        if not self.connector.enabled or self.connector.crm_type != "Salesforce Headless 360":
            frappe.throw("Select an enabled Salesforce Headless 360 connector.")
        self.login_url = _https_url(self.connector.salesforce_login_url)
        self.timeout = max(5, min(int(self.connector.timeout or 60), 120))

    @property
    def callback_url(self) -> str:
        return frappe.utils.get_url("/api/method/financial_ai_agent.api.salesforce.salesforce_callback")

    def authorization_url(self, user: str) -> str:
        if not self.connector.salesforce_consumer_key:
            frappe.throw("Configure the Salesforce External Client App Consumer Key first.")
        verifier, state = _verifier(), secrets.token_urlsafe(32)
        frappe.cache.set_value(
            f"financial_ai_salesforce_oauth:{state}",
            {"user": user, "verifier": verifier, "connector": self.connector.name},
            expires_in_sec=STATE_TTL_SECONDS,
        )
        params = {"response_type":"code","client_id":self.connector.salesforce_consumer_key,
                  "redirect_uri":self.callback_url,"scope":"mcp_api refresh_token offline_access",
                  "state":state,"code_challenge":_challenge(verifier),"code_challenge_method":"S256"}
        return f"{self.login_url}/services/oauth2/authorize?{urlencode(params)}"

    @staticmethod
    def consume_state(state: str) -> dict:
        key = f"financial_ai_salesforce_oauth:{state}"
        payload = frappe.cache.get_value(key)
        frappe.cache.delete_value(key)
        if not payload or not payload.get("user") or not payload.get("verifier") or not payload.get("connector"):
            raise RuntimeError("OAuth state is invalid or expired. Please reconnect.")
        return payload

    def exchange_code(self, code: str, verifier: str) -> dict:
        data = {"grant_type":"authorization_code","client_id":self.connector.salesforce_consumer_key,
                "redirect_uri":self.callback_url,"code":code,"code_verifier":verifier}
        secret = self.connector.get_password("salesforce_client_secret", raise_exception=False)
        if secret:
            data["client_secret"] = secret
        try:
            response = httpx.post(f"{self.login_url}/services/oauth2/token", data=data, timeout=self.timeout)
            response.raise_for_status()
            token = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RuntimeError("Salesforce rejected the OAuth token request.") from exc
        if not token.get("access_token"):
            raise RuntimeError("Salesforce did not return an access token.")
        return token

    def save_connection(self, user: str, token: dict) -> None:
        filters = {"frappe_user": user, "connector": self.connector.name}
        name = frappe.db.exists(CONNECTION_DOCTYPE, filters)
        doc = frappe.get_doc(CONNECTION_DOCTYPE, name) if name else frappe.new_doc(CONNECTION_DOCTYPE)
        doc.update(filters)
        doc.salesforce_instance_url = token.get("instance_url")
        doc.salesforce_identity_url = token.get("id")
        doc.salesforce_user_id = (token.get("id") or "").rstrip("/").split("/")[-1] or None
        doc.connected = 1
        try:
            issued = get_datetime(datetime.fromtimestamp(int(token.get("issued_at")) / 1000, tz=timezone.utc).replace(tzinfo=None))
        except (TypeError, ValueError, OverflowError, OSError):
            issued = now_datetime()
        doc.token_issued_at, doc.token_expiry, doc.last_connected_on = issued, issued + timedelta(hours=2), now_datetime()
        doc.flags.ignore_permissions = True
        doc.save()
        set_encrypted_password(CONNECTION_DOCTYPE, doc.name, token["access_token"], fieldname="access_token")
        if token.get("refresh_token"):
            set_encrypted_password(CONNECTION_DOCTYPE, doc.name, token["refresh_token"], fieldname="refresh_token")
        frappe.db.commit()
