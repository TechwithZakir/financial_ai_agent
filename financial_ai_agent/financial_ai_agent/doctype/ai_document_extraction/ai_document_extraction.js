frappe.ui.form.on("AI Document Extraction", {
  refresh(frm) {
    const roles = frappe.user_roles || [];
    const reviewer = ["Financial AI Manager", "Financial AI Compliance Reviewer", "System Manager"].some((role) => roles.includes(role));
    if (!frm.is_new() && reviewer && frm.doc.human_review_status === "Pending") {
      ["Approved", "Rejected"].forEach((decision) => {
        frm.add_custom_button(__(decision === "Approved" ? "Approve" : "Reject"), async () => {
          await frappe.call("financial_ai_agent.api.documents.review_extraction", { extraction: frm.doc.name, decision });
          frappe.show_alert({ message: __(`Extraction ${decision.toLowerCase()}`), indicator: decision === "Approved" ? "green" : "red" });
          frm.reload_doc();
        }, __("Review"));
      });
    }
  },
});

