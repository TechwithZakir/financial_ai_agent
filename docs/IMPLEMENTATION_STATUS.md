# Implementation status

## Implemented

- Provider-neutral AI contracts and dynamic model configuration
- OpenAI/OpenAI-compatible, Anthropic, Gemini, Qwen, and hosted provider adapters
- Capability/data-classification routing, retry, fallback, normalized errors, and usage logs
- Agent sessions/messages, rich response contract, tool registry, role checks, and approval workflow
- Local Frappe CRM canonical search/get/create/update tools
- Provider/CRM connection-test APIs
- PDF, DOCX, XLSX, CSV, TXT, and Markdown parsing with processing limits
- Structured financial extraction, confidence/warnings, and human validation
- Knowledge chunking, checksum indexing, source citations, and permission-aware keyword retrieval
- Native Desk assistant, document upload, queueing, and processing-status polling
- Workspace, roles, permissions, demo generator, sample fixtures, and unit tests

## Requires deployment-specific configuration or external services

- Live AI provider credentials and approved model IDs
- Salesforce Headless 360 adapter bridge to the separately installed `salesforce_mcp_ai` app
- Remote Frappe CRM credentials and field/object mappings
- OCR/vision processing for scanned images and image-only PDFs
- Production vector database selection and embedding migration/reindex policy
- SMTP/email account configuration for outbound email workflows
- Live provider/CRM load, failover, and security testing

These items cannot be truthfully marked operational without the target services, credentials, policies, and infrastructure. The app fails closed where an unimplemented connector or unavailable capability is selected.

