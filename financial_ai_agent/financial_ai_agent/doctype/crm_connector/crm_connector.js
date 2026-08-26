frappe.ui.form.on("CRM Connector", {
  refresh(frm) {
    if (!frm.is_new() && frm.doc.enabled) {
      frm.add_custom_button(__("Test Connection"), async () => {
        const { message } = await frappe.call(
          "financial_ai_agent.api.crm.test_connection",
          { connector: frm.doc.name }
        );
        frappe.msgprint({
          title: __("CRM Connection"),
          indicator: message.ok ? "green" : "orange",
          message: message.ok ? __("Connection successful") : __("CRM is not available on this site"),
        });
      });
    }
  },
});

