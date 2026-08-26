frappe.ui.form.on("AI Knowledge Document", {
  refresh(frm) {
    if (!frm.is_new() && !["Queued", "Processing"].includes(frm.doc.status)) {
      frm.add_custom_button(__("Index Document"), async () => {
        await frappe.call("financial_ai_agent.api.knowledge.queue_index", { document: frm.doc.name });
        frappe.show_alert({ message: __("Knowledge document queued for indexing"), indicator: "blue" });
        frm.reload_doc();
      }, __("AI Actions"));
    }
  },
});

