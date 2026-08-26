frappe.pages["financial-ai-assistant"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __("Financial AI Assistant"),
    single_column: true,
  });
  frappe.require("/assets/financial_ai_agent/css/financial_ai.css").then(() => {
    new FinancialAIDeskPage(page);
  });
};

class FinancialAIDeskPage {
  constructor(page) {
    this.page = page;
    this.session = null;
    this.busy = false;
    this.render();
    this.bind();
    this.load_agents();
  }

  escape(value) {
    return frappe.utils.escape_html(value == null ? "" : String(value));
  }

  render() {
    this.page.main.addClass("fai-desk-page");
    this.page.main.html(`
      <main class="fai-shell">
        <header class="fai-header">
          <div><span class="fai-eyebrow">${__("FINANCIAL INTELLIGENCE")}</span>
            <h1>${__("Financial AI Assistant")}</h1>
            <p>${__("Analyze documents, search knowledge, and prepare controlled CRM actions.")}</p>
          </div>
          <label>${__("Agent")}<select id="fai-agent"><option value="">${__("Loading agents…")}</option></select></label>
        </header>
        <section id="fai-notice" class="fai-notice" hidden></section>
        <section id="fai-messages" class="fai-messages" aria-live="polite">
          <div class="fai-empty"><h2>${__("How can I help?")}</h2>
            <p>${__("Ask a financial question or choose a prompt below.")}</p>
            <div class="fai-suggestions">
              <button>${__("Summarize the latest client financial position.")}</button>
              <button>${__("Identify missing documents for this application.")}</button>
              <button>${__("Search our knowledge base for the relevant policy.")}</button>
            </div>
          </div>
        </section>
        <form id="fai-composer" class="fai-composer">
          <textarea id="fai-message" rows="2" maxlength="20000" placeholder="${__("Ask the financial assistant…")}" required></textarea>
          <button id="fai-send" type="submit">${__("Send")}</button>
        </form>
        <p class="fai-disclaimer">${__("AI output requires professional review. Sensitive actions are approval-controlled.")}</p>
      </main>`);
    this.root = this.page.main;
  }

  bind() {
    this.root.find("#fai-composer").on("submit", (event) => {
      event.preventDefault();
      const input = this.root.find("#fai-message");
      const text = input.val().trim();
      if (text) { input.val(""); this.send(text); }
    });
    this.root.find(".fai-suggestions button").on("click", (event) => this.send(event.currentTarget.textContent));
    this.root.find("#fai-agent").on("change", () => { this.session = null; });
  }

  async load_agents() {
    try {
      const { message } = await frappe.call("financial_ai_agent.api.chat.available_agents");
      const select = this.root.find("#fai-agent");
      select.empty();
      message.forEach((agent) => select.append(`<option value="${this.escape(agent.name)}">${this.escape(agent.name)}</option>`));
      if (!message.length) this.notice(__("No enabled AI Agent exists. Create and configure one from this workspace."));
    } catch (error) {
      this.notice(this.error_text(error));
    }
  }

  async send(text) {
    const agent = this.root.find("#fai-agent").val();
    if (this.busy || !agent) { this.notice(__("Select or configure an enabled AI Agent first.")); return; }
    this.add_message("user", text); this.set_busy(true); this.notice("");
    const waiting = $(`<article class="fai-message assistant waiting"><div class="fai-bubble">${__("Analyzing securely…")}</div></article>`).appendTo(this.root.find("#fai-messages"));
    try {
      const { message } = await frappe.call("financial_ai_agent.api.chat.chat", {
        message: text, agent, session: this.session,
      });
      waiting.remove(); this.session = message.session;
      this.add_message("assistant", message.response.summary, message.response.metadata || {});
      if (message.response.actions?.length) this.notice(__("A proposed action is waiting for approval."));
    } catch (error) {
      waiting.remove(); this.add_message("assistant", this.error_text(error));
    } finally {
      this.set_busy(false);
    }
  }

  add_message(role, text, metadata = {}) {
    this.root.find(".fai-empty").remove();
    const detail = metadata.model ? `<small>${this.escape(metadata.provider)} · ${this.escape(metadata.model)}</small>` : "";
    const html = this.escape(text).replace(/\n/g, "<br>");
    this.root.find("#fai-messages").append(`<article class="fai-message ${role}"><div class="fai-bubble">${html}</div>${detail}</article>`);
    const messages = this.root.find("#fai-messages")[0]; messages.scrollTop = messages.scrollHeight;
  }

  set_busy(value) {
    this.busy = value;
    this.root.find("#fai-send, #fai-message, #fai-agent, .fai-suggestions button").prop("disabled", value);
  }

  notice(text) {
    const element = this.root.find("#fai-notice"); element.text(text).prop("hidden", !text);
  }

  error_text(error) {
    try { const rows = JSON.parse(error._server_messages || "[]"); if (rows.length) return JSON.parse(rows[0]).message; } catch (_) {}
    return error.message || __("The request failed.");
  }
}

