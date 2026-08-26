frappe.ui.form.on("Client Document", {
  refresh(frm) {
    if (!frm.is_new() && !["Queued", "Processing"].includes(frm.doc.processing_status)) {
      frm.add_custom_button(__("Process Document"), async () => {
        await frappe.call("financial_ai_agent.api.documents.queue_client_document", { document: frm.doc.name });
        frappe.show_alert({ message: __("Document queued for processing"), indicator: "blue" });
        frm.reload_doc();
      }, __("AI Actions"));
    }
  },
});

