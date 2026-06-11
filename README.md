# EntraLens

**AI-Powered Identity Security Analytics SaaS Platform**

EntraLens is a full-demo enterprise AI SaaS application for Identity Security Analytics. It simulates Microsoft Entra ID, Azure SQL Database, Azure Functions, Azure Key Vault, Azure Monitor, Azure OpenAI, RAG knowledge base, Vision AI, natural-language SQL-style analytics, and AI tool/function calling.

## Features

- Inactive User Detection
- MFA Compliance Check
- Global Administrator Audit
- Privileged Account Monitoring
- License Optimization
- Orphan Account Detection
- Conditional Access Investigation
- Identity Governance Review
- Access Review Assistant
- SOC Investigation Dashboard
- AI Risk Scoring Engine
- AI Security Summary Dashboard
- RAG Knowledge Base
- Natural Language to SQL Query Generation pattern
- Vision AI Security Analysis
- Tool Calling & AI Agent Workflow
- Multi-Tenant SaaS Architecture demo
- Role-Based Access Control design
- Reporting & Export System: CSV and PDF

## Full Demo Mode: Azure Service Mapping

| Demo Component | Production Azure Equivalent |
|---|---|
| Mock users, MFA, roles, sign-in logs | Microsoft Entra ID / Microsoft Graph API |
| Local PostgreSQL | Azure SQL Database |
| FastAPI service tools | Azure Functions |
| `.env` secrets | Azure Key Vault |
| Audit table + console logs | Azure Monitor |
| Ollama models | Azure OpenAI / Azure AI Foundry |

## Required Versions

- Python 3.13
- PostgreSQL
- Ollama optional for AI responses

## Database Settings

Default database URL:

```env
DATABASE_URL=postgresql+psycopg://postgres:password1230@localhost:5432/entralens_db
```

Database password requested for this demo: `password1230`

## Setup Step by Step

### 1. Create PostgreSQL database

Open pgAdmin or psql and create:

```sql
CREATE DATABASE entralens_db;
```

### 2. Open project folder

```bash
cd EntraLens
```

### 3. Create virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
source .venv/Scripts/activate
```

### 4. Install packages

```bash
pip install -r requirements.txt
```

### 5. Create `.env`

Copy `.env.example` to `.env`.

```bash
cp .env.example .env
```

For Windows PowerShell:

```powershell
copy .env.example .env
```

### 6. Seed demo data

```bash
python -m app.seed
```

### 7. Run app

```bash
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Ollama Models

This project is configured for:

```env
OLLAMA_TEXT_MODEL=gemma4:31b-cloud
OLLAMA_VISION_MODEL=qwen3-VL:235-cloud
```

If Ollama or cloud models are not available, the app automatically uses demo fallback responses so your dashboard still works.

## API Endpoints

- `GET /` - Dashboard UI
- `GET /api/dashboard` - Dashboard metrics
- `POST /api/chat` - AI chatbot + intent + tool calling
- `GET /api/identity/inactive-users`
- `GET /api/identity/mfa-compliance`
- `GET /api/identity/license-optimization`
- `GET /api/identity/orphan-accounts`
- `GET /api/roles/global-admins`
- `POST /api/vision/analyze` - Vision AI demo
- `GET /api/reports/export.csv`
- `GET /api/reports/export.pdf`

## GitHub Upload Steps

I cannot upload this project to your GitHub without your GitHub login/token. You should upload it from your computer:

```bash
git init
git add .
git commit -m "Initial commit - EntraLens AI Identity Security SaaS"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/entralens.git
git push -u origin main
```

To let your friend or examiner view it, make the GitHub repository Public or add them as a Collaborator.

## Suggested Repository Name

```text
entralens-ai-identity-security-saas
```

## Demo Login Concept

Current version is full demo mode. Recommended roles:

- Super Admin
- Security Analyst
- IAM Engineer
- SOC Analyst
- Auditor
- Read-only Viewer

## Project Status

This is a portfolio/exam-ready demo foundation. It is intentionally designed to avoid Azure billing while still showing Azure production architecture knowledge.
