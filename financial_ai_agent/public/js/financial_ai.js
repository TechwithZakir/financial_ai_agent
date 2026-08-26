(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const token = document.querySelector('meta[name="frappe-csrf-token"]')?.content || "";
  let session = null;
  const escapeHtml = (value) => { const node = document.createElement("div"); node.textContent = value ?? ""; return node.innerHTML; };
  function notice(text) { $("notice").textContent = text; $("notice").hidden = !text; }
  function add(role, text, metadata = {}) {
    $("messages").querySelector(".fai-empty")?.remove();
    const item = document.createElement("article"); item.className = `fai-message ${role}`;
    item.innerHTML = `<div class="fai-bubble">${escapeHtml(text).replace(/\n/g, "<br>")}</div>${metadata.model ? `<small>${escapeHtml(metadata.provider)} · ${escapeHtml(metadata.model)}</small>` : ""}`;
    $("messages").appendChild(item); item.scrollIntoView({ behavior: "smooth", block: "end" });
  }
  function errorText(error) {
    try { const rows = JSON.parse(error._server_messages || "[]"); if (rows.length) return JSON.parse(rows[0]).message; } catch (_) {}
    return error.message || "The request failed.";
  }
  async function send(text) {
    add("user", text); notice(""); $("send").disabled = true; $("message").disabled = true;
    const waiting = document.createElement("article"); waiting.className = "fai-message assistant waiting"; waiting.innerHTML = '<div class="fai-bubble">Analyzing securely…</div>'; $("messages").appendChild(waiting);
    try {
      const result = await frappe.call({ method: "financial_ai_agent.api.chat.chat", headers: {"X-Frappe-CSRF-Token": token}, args: { message: text, agent: $("agent").value, session } });
      waiting.remove(); session = result.message.session; const response = result.message.response;
      add("assistant", response.summary, response.metadata || {});
      if (response.actions?.length) notice("A proposed action is waiting for approval.");
    } catch (error) { waiting.remove(); add("assistant", errorText(error)); }
    finally { $("send").disabled = false; $("message").disabled = false; $("message").focus(); }
  }
  $("composer").addEventListener("submit", (event) => { event.preventDefault(); const text = $("message").value.trim(); if (text && $("agent").value) { $("message").value = ""; send(text); } });
  document.querySelectorAll(".fai-suggestions button").forEach((button) => button.addEventListener("click", () => send(button.textContent)));
  if (!$("agent").value) notice("No enabled AI Agent is configured. Ask an administrator to create one.");
})();

