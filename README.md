# Financial AI Agent

Project Summary

This project delivers a production-ready, enterprise-focused **AI Agent Platform built on Frappe Framework** for financial services and other data-intensive business operations.

The platform is designed to automate client interactions, financial document analysis, internal knowledge retrieval, lead qualification, CRM operations, follow-up activities, and repetitive back-office processes through a secure and extensible agentic AI architecture.

Unlike a traditional chatbot, the system combines **AI reasoning, Retrieval-Augmented Generation (RAG), structured document intelligence, tool calling, workflow automation, CRM integrations, human approvals, and auditability** within a single Frappe application.

The platform initially integrates with:

* **Frappe CRM**
* **Salesforce Headless 360 / Salesforce Hosted MCP**

Its CRM integration layer is provider-independent, allowing future connectors such as HubSpot, Zoho CRM, Microsoft Dynamics 365, and custom CRM platforms to be added without redesigning the AI core.

The AI model layer is also fully provider-independent. Organizations can configure and route workloads across:

* OpenAI
* Anthropic Claude
* Google Gemini
* Alibaba Cloud Qwen
* Private or hosted OpenAI-compatible AI services
* Self-hosted AI platforms such as vLLM or other enterprise inference gateways

Different models can be assigned to different workloads, such as reasoning, document analysis, tool calling, vision, fast-response tasks, and embeddings. Provider fallback, capability routing, token usage tracking, and sensitive-data policies are incorporated into the architecture.

The application supports intelligent processing of financial and business documents including PDFs, spreadsheets, scanned documents, bank statements, payslips, financial statements, and other uploaded files. AI performs classification and structured extraction, while deterministic Python logic is used for financial calculations, validation, scoring, ratios, and other operations where accuracy is critical.

An integrated RAG engine enables users to securely query internal policies, procedures, product documentation, compliance guidelines, and organizational knowledge. Responses can include traceable source references rather than relying only on general model knowledge.

The agent can securely interact with connected CRM systems through a controlled tool registry. Typical capabilities include searching leads, accounts, contacts, and opportunities, reviewing client activity, preparing CRM notes, qualifying leads, creating follow-up tasks, and proposing record updates. Sensitive or higher-risk operations can require explicit human approval before execution.

A key feature of the platform is its **structured rich-response framework**. AI responses are not limited to plain text. The interface can dynamically render:

* KPI cards
* Responsive tables
* Bar, line, pie, and other supported charts
* Financial summaries
* CRM record cards
* Status indicators
* Alerts
* Recommendations
* Knowledge citations
* Timelines
* Approval requests
* Interactive action buttons

The responsive AI Assistant interface is designed for desktop, tablet, and mobile use within Frappe Desk.

Security and governance are fundamental to the platform. The architecture includes role-based permissions, encrypted credentials, provider-level data policies, controlled tool execution, prompt-injection defenses, per-user/session isolation, audit logs, correlation IDs, approval workflows, and protection against unauthorized CRM or financial actions.

The system is designed as a reusable AI platform rather than a customer-specific automation script. Frappe provides the application, workflow, permissions, configuration, background processing, audit, and user-management foundation, while AI providers, CRM providers, vector databases, and external services operate through modular adapters.

The result is a scalable foundation for building secure AI-powered business automation across financial services and, later, industries such as manufacturing, healthcare, real estate, professional services, nonprofit organizations, and enterprise operations.

The core architectural principle is:

**Frappe as the AI Platform → Provider-independent AI Models → Intelligent Agents and RAG → Controlled Tool Execution → Multi-CRM Integrations → Human Governance → Rich Business UI.**

The project is intended for full production deployment, with emphasis on reliability, security, maintainability, extensibility, automated testing, background processing, monitoring, migration safety, and minimal post-deployment debugging.

## Implemented architecture

- Dynamic AI Provider and AI Model records; no model identifiers in routing logic
- OpenAI/OpenAI-compatible, Anthropic, Gemini, Alibaba Qwen, and hosted-provider adapters
- Capability and sensitive-data policy routing with controlled retry and fallback
- Normalized requests, responses, tool calls, token usage, and provider exceptions
- AI Agent, session, message, approval, usage, knowledge, chunk, and CRM connector records
- Permission-aware local Frappe CRM provider interface
- Server-only tool registry with role checks and risk-based approval gates
- Session chat API with ownership enforcement, audit correlation IDs, and safe errors
- Prompt-injection detection, secret redaction, rich response blocks, RAG chunking/citations
- Decimal-based financial calculations for ratios and cash-flow summaries
- Background parsing for PDF, DOCX, XLSX, CSV, TXT, and Markdown documents
- Structured financial extraction with confidence, warnings, and mandatory human review
- Knowledge ingestion with checksums, source chunks, citations, and permission-aware search
- Approval decision and idempotent execution endpoints with separation of duties
- Native Desk assistant at `/app/financial-ai-assistant`, plus the `/financial-ai` web route

## Installation

```bash
cd ~/frappe-bench
bench get-app https://github.com/TechwithZakir/financial_ai_agent.git
bench --site yoursite install-app financial_ai_agent
bench --site yoursite migrate
bench build --app financial_ai_agent
bench restart
```

After pulling an update, synchronize DocTypes and Desk metadata:

```bash
bench --site yoursite migrate
bench --site yoursite clear-cache
bench build --app financial_ai_agent
bench restart
```

If the app was installed from a package created before `MANIFEST.in` was added, update/reinstall
the app package first, then run the commands above. Do not manually create the Module Def; Frappe
creates and synchronizes it from `modules.txt` during installation/migration.

Assign `Financial AI User` to users, `Financial AI Manager` to platform administrators, and `Financial AI Compliance Reviewer` to approval reviewers. Configure an **AI Provider**, one or more **AI Model** records, and an enabled **AI Agent** before calling the chat API.

## Standalone Salesforce Hosted MCP connection

This app owns its Salesforce OAuth 2.0 PKCE connection and does not require
`salesforce_mcp_ai`. Configure a **CRM Connector** with CRM Type **Salesforce
Headless 360**, the Salesforce login and Hosted MCP URLs, the External Client
App Consumer Key, and the optional client secret.

Register this callback URL in the Salesforce External Client App:

`https://<your-frappe-site>/api/method/financial_ai_agent.api.salesforce.salesforce_callback`

Financial AI users can then select that connector and use **Connect Salesforce**
in the assistant. Access and refresh tokens are stored in encrypted Password
fields on a per-user connection record.

## Chat API

Call the whitelisted method `financial_ai_agent.api.chat.chat` with `message`, `agent`, and optional `session`, `model`, and `classification` values. API keys remain encrypted Password fields and are never returned to browser code.

## Verification

```bash
python -m compileall -q financial_ai_agent
bench --site development.localhost run-tests --app financial_ai_agent
```

Live provider and CRM connection tests require separately configured credentials. Automated unit tests do not call external services.

For complete demo setup, sample-file expectations, and acceptance tests, see
[`docs/TESTING_AND_SETUP.md`](docs/TESTING_AND_SETUP.md). Current implementation coverage and
deployment-dependent items are documented in [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md).
