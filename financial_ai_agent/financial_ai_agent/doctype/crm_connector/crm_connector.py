from urllib.parse import urlparse

import frappe
from frappe.model.document import Document


class CRMConnector(Document):
    def validate(self):
        if self.site_url and urlparse(self.site_url).scheme != "https":
            frappe.throw("Remote CRM URLs must use HTTPS")
        if self.crm_type == "Salesforce Headless 360":
            for fieldname in ("salesforce_login_url", "salesforce_mcp_url"):
                value = self.get(fieldname)
                parsed = urlparse(value or "")
                if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                    frappe.throw(f"{self.meta.get_label(fieldname)} must be a valid HTTPS URL")
        if self.is_default and self.enabled:
            frappe.db.set_value("CRM Connector", {"is_default": 1, "name": ["!=", self.name]}, "is_default", 0)
