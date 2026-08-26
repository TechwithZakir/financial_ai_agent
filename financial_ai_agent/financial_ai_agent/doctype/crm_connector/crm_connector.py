from urllib.parse import urlparse

import frappe
from frappe.model.document import Document


class CRMConnector(Document):
    def validate(self):
        if self.site_url and urlparse(self.site_url).scheme != "https":
            frappe.throw("Remote CRM URLs must use HTTPS")
        if self.is_default and self.enabled:
            frappe.db.set_value("CRM Connector", {"is_default": 1, "name": ["!=", self.name]}, "is_default", 0)

