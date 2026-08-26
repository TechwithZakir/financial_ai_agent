frappe.ui.form.on("AI Approval Request", {
  refresh(frm) {
    const roles = frappe.user_roles || [];
    const reviewer = ["Financial AI Manager", "Financial AI Compliance Reviewer", "System Manager"].some((role) => roles.includes(role));
    if (!frm.is_new() && reviewer && frm.doc.status === "Pending") {
      ["Approved", "Rejected"].forEach((decision) => {
        frm.add_custom_button(__(decision === "Approved" ? "Approve" : "Reject"), async () => {
          await frappe.call("financial_ai_agent.api.approvals.decide", { approval: frm.doc.name, decision });
          frm.reload_doc();
        }, __("Decision"));
      });
    }
    if (!frm.is_new() && reviewer && frm.doc.status === "Approved") {
      frm.add_custom_button(__("Execute Approved Action"), async () => {
        const result = await frappe.call("financial_ai_agent.api.approvals.execute", { approval: frm.doc.name });
        frappe.show_alert({ message: __(result.message.status), indicator: result.message.status === "Executed" ? "green" : "red" });
        frm.reload_doc();
      }, __("Execution"));
    }
  },
});

