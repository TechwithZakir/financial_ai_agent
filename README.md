# Financial AI Agent

`financial_ai_agent` is a separate Frappe v15+ application for a provider-neutral financial-services AI platform. It does not modify the existing `salesforce_mcp_ai` app.

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

## Installation

```bash
cd ~/frappe-bench
bench get-app /path/to/financial_ai_agent
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

## Chat API

Call the whitelisted method `financial_ai_agent.api.chat.chat` with `message`, `agent`, and optional `session`, `model`, and `classification` values. API keys remain encrypted Password fields and are never returned to browser code.

## Verification

```bash
python -m compileall -q financial_ai_agent
bench --site development.localhost run-tests --app financial_ai_agent
```

Live provider and CRM connection tests require separately configured credentials. Automated unit tests do not call external services.
