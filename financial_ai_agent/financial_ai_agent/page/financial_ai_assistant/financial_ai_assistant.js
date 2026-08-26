frappe.pages["financial-ai-assistant"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Financial AI Assistant"), single_column: true });
  const stylesheet = "/assets/financial_ai_agent/css/financial_ai.css?v=20260826-crm-workspace-2";
  const existing = document.querySelector('link[data-financial-ai-styles]');
  if (existing) {
    new FinancialAIDeskPage(page);
    return;
  }
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = stylesheet;
  link.dataset.financialAiStyles = "true";
  link.onload = () => new FinancialAIDeskPage(page);
  link.onerror = () => frappe.msgprint(__("Financial AI Assistant styles could not be loaded."));
  document.head.appendChild(link);
};

class FinancialAIDeskPage {
  constructor(page) {
    this.page = page; this.session = null; this.busy = false; this.connectors = []; this.logs = [];
    this.render(); this.bind(); this.load_agents(); this.load_connectors();
  }
  escape(value) { return frappe.utils.escape_html(value == null ? "" : String(value)); }
  render() {
    this.page.main.addClass("fai-desk-page").html(`
      <main class="fai-shell">
        <header class="fai-header"><div><span class="fai-eyebrow">${__("FINANCIAL INTELLIGENCE")}</span><h1>${__("Financial AI Assistant")}</h1><p>${__("Analyze documents, search knowledge, and execute controlled CRM workflows.")}</p></div>
          <div class="fai-header-actions"><button id="fai-upload" class="fai-upload" type="button">${__("Upload Document")}</button><label>${__("Agent")}<select id="fai-agent"><option value="">${__("Loading agents…")}</option></select></label></div></header>
        <section id="fai-notice" class="fai-notice" hidden></section>
        <div class="fai-workspace-grid">
          <aside class="fai-sidebar">
            <section class="fai-side-card"><div class="fai-card-heading"><div><span class="fai-card-kicker">${__("INTEGRATION")}</span><h3>${__("CRM Connection")}</h3></div><span id="fai-crm-dot" class="fai-status-dot"></span></div>
              <label class="fai-field">${__("CRM Connector")}<select id="fai-connector"><option value="">${__("Loading connectors…")}</option></select></label>
              <div id="fai-connector-detail" class="fai-connector-detail">${__("Choose an enabled connector.")}</div><button id="fai-connect-action" class="fai-primary-action" type="button" disabled>${__("Select CRM")}</button>
            </section>
            <section class="fai-side-card"><div class="fai-card-heading"><h3>${__("Operation Stages")}</h3><span id="fai-stage-count" class="fai-count">0</span></div><ol id="fai-stages" class="fai-stages"><li class="muted">${__("Stages appear when an AI request runs.")}</li></ol></section>
            <section class="fai-side-card fai-log-card"><div class="fai-card-heading"><h3>${__("Activity Log")}</h3><button id="fai-clear-log" class="fai-text-button">${__("Clear")}</button></div><div id="fai-log" class="fai-log"><div class="muted">${__("No activity yet.")}</div></div></section>
          </aside>
          <section class="fai-chat-panel"><section id="fai-document-status" class="fai-document-status" hidden></section>
            <section id="fai-messages" class="fai-messages" aria-live="polite"><div class="fai-empty"><h2>${__("How can I help?")}</h2><p>${__("Ask a financial question or choose a prompt below.")}</p><div class="fai-suggestions"><button>${__("Summarize the latest client financial position.")}</button><button>${__("Identify missing documents for this application.")}</button><button>${__("Search our knowledge base for the relevant policy.")}</button></div></div></section>
            <form id="fai-composer" class="fai-composer"><textarea id="fai-message" rows="2" maxlength="20000" placeholder="${__("Ask the financial assistant…")}" required></textarea><button id="fai-send" type="submit">${__("Send")}</button></form>
            <p class="fai-disclaimer">${__("AI output requires professional review. Sensitive actions are approval-controlled.")}</p></section>
        </div>
      </main>`);
    this.root = this.page.main;
  }
  bind() {
    this.root.find("#fai-composer").on("submit", (event) => { event.preventDefault(); const input=this.root.find("#fai-message"); const text=input.val().trim(); if(text){input.val("");this.send(text);} });
    this.root.find(".fai-suggestions button").on("click", (event) => this.send(event.currentTarget.textContent));
    this.root.find("#fai-agent").on("change", () => { this.session=null; this.log(__("Agent changed"),"info",this.root.find("#fai-agent").val()); });
    this.root.find("#fai-connector").on("change", () => this.connector_changed());
    this.root.find("#fai-connect-action").on("click", () => this.connector_action());
    this.root.find("#fai-upload").on("click", () => this.upload_document());
    this.root.find("#fai-clear-log").on("click", () => { this.logs=[]; this.render_logs(); });
  }
  async load_agents() {
    try { const {message}=await frappe.call("financial_ai_agent.api.chat.available_agents"); const select=this.root.find("#fai-agent").empty(); message.forEach((agent)=>select.append(`<option value="${this.escape(agent.name)}">${this.escape(agent.name)}</option>`)); if(!message.length)this.notice(__("No enabled AI Agent exists. Configure one in the workspace.")); this.log(__("Agents loaded"),"success",__("{0} enabled",[message.length])); }
    catch(error){this.notice(this.error_text(error));this.log(__("Agent loading failed"),"error",this.error_text(error));}
  }
  async load_connectors() {
    try { const {message}=await frappe.call("financial_ai_agent.api.crm.available_connectors"); this.connectors=message; const select=this.root.find("#fai-connector").empty().append(`<option value="">${__("Select CRM…")}</option>`); message.forEach((item)=>select.append(`<option value="${this.escape(item.name)}">${this.escape(item.connector_name)} · ${this.escape(item.crm_type)}</option>`)); const preferred=message.find((item)=>item.is_default)||message[0]; if(preferred)select.val(preferred.name); await this.connector_changed(); this.log(__("CRM connectors loaded"),"success",__("{0} available",[message.length])); }
    catch(error){this.log(__("CRM loading failed"),"error",this.error_text(error));}
  }
  selected_connector() { return this.connectors.find((item)=>item.name===this.root.find("#fai-connector").val()); }
  async connector_changed() {
    const connector=this.selected_connector(),button=this.root.find("#fai-connect-action"),detail=this.root.find("#fai-connector-detail"); this.salesforce=null; this.root.find("#fai-crm-dot").removeClass("connected");
    if(!connector){detail.text(__("Choose an enabled connector."));button.text(__("Select CRM")).prop("disabled",true);return;}
    detail.html(`<strong>${this.escape(connector.crm_type)}</strong><span>${this.escape(connector.mode)} · ${connector.read_enabled?__("Read enabled"):__("Read disabled")} · ${connector.update_enabled?__("Updates enabled"):__("Updates disabled")}</span>`); button.prop("disabled",false);
    if(connector.crm_type==="Salesforce Headless 360") { button.text(__("Checking Salesforce…")).prop("disabled",true); try { const {message}=await frappe.call("financial_ai_agent.api.crm.salesforce_status"); this.salesforce=message; button.prop("disabled",!message.installed).text(message.connected?__("Disconnect Salesforce"):__("Connect Salesforce")); this.root.find("#fai-crm-dot").toggleClass("connected",Boolean(message.connected)); detail.append(`<span>${this.escape(message.connected?(message.salesforce_username||__("OAuth connected")):(message.message||__("OAuth connection required")))}</span>`); } catch(error){button.text(__("Salesforce Unavailable"));this.log(__("Salesforce status failed"),"error",this.error_text(error));} }
    else button.text(__("Test {0}",[connector.crm_type])); this.log(__("CRM selected"),"info",`${connector.connector_name} · ${connector.crm_type}`);
  }
  async connector_action() {
    const connector=this.selected_connector(); if(!connector)return;
    if(connector.crm_type==="Salesforce Headless 360") { if(this.salesforce?.connected){frappe.confirm(__("Disconnect your Salesforce account?"),async()=>{await frappe.call("financial_ai_agent.api.crm.disconnect_salesforce");this.log(__("Salesforce disconnected"),"info");this.connector_changed();});return;} try { const {message}=await frappe.call("financial_ai_agent.api.crm.start_salesforce_oauth"); this.log(__("Starting Salesforce OAuth"),"pending"); window.location.assign(message.authorization_url); } catch(error){this.notice(this.error_text(error));this.log(__("Salesforce connection failed"),"error",this.error_text(error));} return; }
    try { this.log(__("Testing CRM connection"),"pending",connector.connector_name); const {message}=await frappe.call("financial_ai_agent.api.crm.test_connection",{connector:connector.name}); this.root.find("#fai-crm-dot").toggleClass("connected",Boolean(message.ok)); this.log(__("CRM connection test"),message.ok?"success":"error",message.ok?__("Connection successful"):__("Connection unavailable")); }
    catch(error){this.log(__("CRM connection test failed"),"error",this.error_text(error));this.notice(this.error_text(error));}
  }
  upload_document() { new frappe.ui.FileUploader({allow_multiple:false,restrictions:{allowed_file_types:[".pdf",".docx",".xlsx",".csv",".txt",".md",".png",".jpg",".jpeg"],max_file_size:25*1024*1024},on_success:async(file)=>{try{this.log(__("File uploaded"),"success",file.file_name);const {message}=await frappe.call("financial_ai_agent.api.documents.create_and_queue",{file_url:file.file_url});this.document_status(__("Uploaded and queued: {0}",[file.file_name]));this.poll_document(message.document);}catch(error){this.document_status(this.error_text(error),true);this.log(__("Document queue failed"),"error",this.error_text(error));}}}); }
  async poll_document(name){for(let attempt=0;attempt<90;attempt+=1){await new Promise((resolve)=>setTimeout(resolve,3000));try{const {message}=await frappe.call("financial_ai_agent.api.documents.get_status",{document:name});this.document_status(__("Document {0}: {1} / {2}",[name,message.processing_status,message.extraction_status]));if(["Completed","Failed"].includes(message.processing_status)){this.log(__("Document processing finished"),message.processing_status==="Completed"?"success":"error",message.processing_status);if(message.processing_status==="Completed")this.root.find("#fai-message").val(__("Analyze uploaded document {0} and summarize the findings.",[name]));return;}}catch(error){this.document_status(this.error_text(error),true);return;}}}
  async send(text){const agent=this.root.find("#fai-agent").val();if(this.busy||!agent){this.notice(__("Select or configure an enabled AI Agent first."));return;}this.add_message("user",text);this.set_busy(true);this.notice("");this.render_stages(["Request submitted"]);this.log(__("AI request started"),"pending",agent);const waiting=$(`<article class="fai-message assistant waiting"><div class="fai-bubble">${__("Analyzing securely…")}</div></article>`).appendTo(this.root.find("#fai-messages"));try{const {message}=await frappe.call("financial_ai_agent.api.chat.chat",{message:text,agent,session:this.session,crm_connector:this.root.find("#fai-connector").val()||null});waiting.remove();this.session=message.session;this.add_message("assistant",message.response.summary,message.response.metadata||{});this.render_stages(message.response.metadata?.stages||["Response completed"]);this.log(__("AI request completed"),"success",`${message.response.metadata?.provider||""} · ${message.response.metadata?.duration_ms||0}ms`);if(message.response.actions?.length)this.notice(__("A proposed action is waiting for approval."));}catch(error){waiting.remove();this.add_message("assistant",this.error_text(error));this.render_stages(["Request submitted","Operation failed"],true);this.log(__("AI request failed"),"error",this.error_text(error));}finally{this.set_busy(false);}}
  render_stages(stages,failed=false){this.root.find("#fai-stage-count").text(stages.length);this.root.find("#fai-stages").html(stages.map((stage,index)=>`<li class="${failed&&index===stages.length-1?"failed":"complete"}"><span>${index+1}</span>${this.escape(stage)}</li>`).join(""));}
  log(message,status="info",detail=""){this.logs.push({time:new Date().toLocaleTimeString(),message,status,detail});if(this.logs.length>80)this.logs.shift();this.render_logs();}
  render_logs(){const target=this.root.find("#fai-log");if(!this.logs.length){target.html(`<div class="muted">${__("No activity yet.")}</div>`);return;}target.html(this.logs.map((item)=>`<div class="fai-log-row ${item.status}"><time>${this.escape(item.time)}</time><div><strong>${this.escape(item.message)}</strong>${item.detail?`<span>${this.escape(item.detail)}</span>`:""}</div></div>`).join(""));target[0].scrollTop=target[0].scrollHeight;}
  add_message(role,text,metadata={}){this.root.find(".fai-empty").remove();const detail=metadata.model?`<small>${this.escape(metadata.provider)} · ${this.escape(metadata.model)}</small>`:"";this.root.find("#fai-messages").append(`<article class="fai-message ${role}"><div class="fai-bubble">${this.escape(text).replace(/\n/g,"<br>")}</div>${detail}</article>`);const messages=this.root.find("#fai-messages")[0];messages.scrollTop=messages.scrollHeight;}
  set_busy(value){this.busy=value;this.root.find("#fai-send,#fai-message,#fai-agent,#fai-connector,.fai-suggestions button").prop("disabled",value);}
  document_status(text,is_error=false){this.root.find("#fai-document-status").text(text).prop("hidden",!text).toggleClass("error",is_error);}
  notice(text){this.root.find("#fai-notice").text(text).prop("hidden",!text);}
  error_text(error){try{const rows=JSON.parse(error._server_messages||"[]");if(rows.length)return JSON.parse(rows[0]).message;}catch(_){}return error.message||__("The request failed.");}
}
