app_name = "financial_ai_agent"
app_title = "Financial AI Agent"
app_publisher = "Financial AI Agent contributors"
app_description = "Provider-neutral financial services AI agent platform"
app_email = "support@example.com"
app_license = "MIT"
required_apps = ["frappe"]

after_install = "financial_ai_agent.install.after_install"
after_migrate = "financial_ai_agent.install.after_migrate"

fixtures = [
    {
        "dt": "Role",
        "filters": [["name", "in", [
            "Financial AI User", "Financial AI Manager", "Financial AI Compliance Reviewer"
        ]]],
    }
]

permission_query_conditions = {
    "AI Agent Session": "financial_ai_agent.permissions.session_query",
    "AI Message": "financial_ai_agent.permissions.message_query",
    "AI Approval Request": "financial_ai_agent.permissions.approval_query",
    "AI Usage Log": "financial_ai_agent.permissions.usage_query",
    "Client Document": "financial_ai_agent.permissions.client_document_query",
    "Financial AI Salesforce Connection": "financial_ai_agent.permissions.salesforce_connection_query",
}

has_permission = {
    "AI Agent Session": "financial_ai_agent.permissions.session_permission",
    "AI Message": "financial_ai_agent.permissions.message_permission",
    "AI Approval Request": "financial_ai_agent.permissions.approval_permission",
    "AI Usage Log": "financial_ai_agent.permissions.usage_permission",
    "Client Document": "financial_ai_agent.permissions.client_document_permission",
    "Financial AI Salesforce Connection": "financial_ai_agent.permissions.salesforce_connection_permission",
}
