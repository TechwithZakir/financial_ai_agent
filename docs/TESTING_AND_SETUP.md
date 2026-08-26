# Financial AI Agent - setup and acceptance testing

## 1. Deploy the revision

```bash
cd ~/frappe-bench/apps/financial_ai_agent
git pull --ff-only origin main

cd ~/frappe-bench
bench setup requirements --python
bench --site YOUR_SITE migrate
bench --site YOUR_SITE clear-cache
bench build --app financial_ai_agent
bench restart
```

Verify the deployed commit with `git rev-parse --short HEAD` and inspect migration output for errors.

## 2. Choose an AI runtime

For production, create an AI Provider and AI Model in Desk using a valid provider credential and model ID. Do not place keys in source, site configuration exports, screenshots, or shell history.

For local synthetic testing with Ollama:

```bash
ollama pull qwen2.5:7b
ollama serve
bench --site YOUR_SITE execute financial_ai_agent.demo.generate_test_data
```

The generator is idempotent. It creates:

- Local Demo AI provider (`http://127.0.0.1:11434/v1`)
- Local Demo Financial Model (`qwen2.5:7b`)
- Local Frappe CRM Demo connector
- Financial Assistant Demo agent
- Demo Financial Policies knowledge base
- A synthetic CRM lead when Frappe CRM is installed
- Client Document records for the bundled synthetic sample files
- A synthetic policy Knowledge Document

Run the generator only on a development or demonstration site. All generated records are labelled synthetic.

## 3. Roles

Assign at least one of these roles to a test user:

- Financial AI User: chat, upload, and owned sessions/documents
- Financial AI Manager: configuration, connector tests, approvals, and logs
- Financial AI Compliance Reviewer: extraction and high-risk reviews
- System Manager: full administration

## 4. Open and configure the assistant

Open `/app/financial-ai-assistant`. The Agent selector lists enabled AI Agent records. If it is empty, confirm that the Agent and its linked Model and Provider are all enabled.

For local CRM:

1. Create a CRM Connector with type `Frappe CRM`.
2. Select `Local`, `Local Session`, and enable reads.
3. Enable create/update only when the approval workflow will be tested.
4. Click **Test Connection**.
5. Select that connector in the AI Agent's **Default CRM Connector** field.

## 5. Document tests

Use **Upload Document** on the assistant page and test the files under `sample_data/`.

Expected classifications:

| File | Expected behavior |
| --- | --- |
| `synthetic_financial_statements_2025.pdf` | Financial Statements; structured extraction; human review required |
| `synthetic_credit_application_summary.docx` | General Financial Document; narrative and table extraction |
| `synthetic_financial_test_pack.xlsx` | Financial Statements; spreadsheet text extraction |
| `synthetic_bank_statement.csv` | Bank Statement; transaction extraction |
| `synthetic_payslip.txt` | Payslip classification and payroll fields |
| `synthetic_credit_policy.md` | Knowledge indexing and citation search |

Images are accepted by the upload UI, but extraction requires a configured vision workflow. Password-protected PDFs, unsupported extensions, files over 25 MB, and spreadsheets over 100,000 cells must fail safely.

## 6. Knowledge test

1. Open **Synthetic SME Credit Policy** under Knowledge Documents.
2. Click **Index Document**.
3. Wait for status `Ready`.
4. Call `financial_ai_agent.api.knowledge.search` or ask the assistant about minimum SME documents.
5. Confirm the response cites the source document/chunk rather than inventing policy.

## 7. CRM and approval tests

Read test: ask `Find the Northstar Trading Demo lead.` The agent should use `crm.search` and respect Frappe permissions.

Write test: ask the agent to update the demo lead. The tool must create an AI Approval Request rather than executing immediately. A different manager/reviewer approves it, then uses **Execute Approved Action**. Repeated execution must return the stored result and not repeat the mutation.

## 8. Automated checks

```bash
bench --site YOUR_SITE run-tests --app financial_ai_agent
bench --site YOUR_SITE migrate
bench build --app financial_ai_agent
```

Also verify background workers are running, inspect failed RQ jobs, and exercise one live provider request with non-production credentials.

## 9. Production gate

Before production use:

- Replace the local demo provider/model with approved production configuration.
- Delete or disable synthetic demo records.
- Configure HTTPS, workers, Redis, backups, log retention, and secret rotation.
- Test role isolation with non-administrator accounts.
- Validate provider data-processing terms for financial data and PII.
- Complete live CRM and provider acceptance tests.
- Keep human review enabled for extracted financial data and CRM mutations.

