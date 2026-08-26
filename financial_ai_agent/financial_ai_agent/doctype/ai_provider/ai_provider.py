from urllib.parse import urlparse

import frappe
from frappe.model.document import Document


class AIProvider(Document):
    def validate(self):
        if self.base_url:
            parsed = urlparse(self.base_url)
            loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
            if parsed.scheme != "https" and not loopback:
                frappe.throw("AI provider Base URL must use HTTPS unless it is loopback")
        self.timeout = max(5, min(int(self.timeout or 60), 600))
        self.retries = max(0, min(int(self.retries or 0), 3))

