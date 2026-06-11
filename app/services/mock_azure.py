def azure_mapping():
    return {
        'Microsoft Entra ID': 'Mock users, roles, MFA, sign-in logs in PostgreSQL',
        'Azure SQL Database': 'Local PostgreSQL database',
        'Azure Functions': 'FastAPI scheduled/demo service layer',
        'Azure Key Vault': '.env environment variables',
        'Azure Monitor': 'Local audit_events table and console logging',
        'Azure OpenAI': 'Ollama demo models: gemma4:31b-cloud and qwen3-VL:235-cloud'
    }
