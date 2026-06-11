# EntraLens AI Identity Security Copilot
> AI Intent Detection + Natural Language to SQL Query Generation for Microsoft Entra ID Security Analytics.

## Overview

EntraLens is an AI-powered Identity Security Copilot designed for Microsoft Entra ID environments. The platform combines Identity Security Analytics, AI Intent Detection, Natural Language to SQL Query Generation, Voice Assistant capabilities, and PostgreSQL-based security investigations.

Users can ask questions in English or Bangla, and the AI automatically detects user intent, generates SQL queries, executes them against the EntraLens database, and returns real-time results.

---

## Problem Statement

Identity administrators often struggle to investigate security incidents, inactive users, MFA compliance issues, privileged accounts, and licensing information using manual database queries.

EntraLens simplifies this process by allowing administrators to interact with identity security data using natural language.

---

## Key Features

### Identity Security Dashboard

* Security KPI Cards
* User Risk Analytics
* Identity Security Monitoring
* User Statistics
* Security Investigation Output

### User Management

* Create User
* Edit User
* Delete User
* Refresh Users
* Auto Risk Score Calculation
* PostgreSQL Integration

### AI Intent Detection

The AI understands user intent from natural language input.

Examples:

**English**

* Show inactive users
* Show users without MFA
* Show high risk users
* Show finance department users

**Bangla**

* ফাইন্যান্স ডিপার্টমেন্টের সব ইউজার দেখাও
* MFA ছাড়া ইউজারগুলো দেখাও
* হাই রিস্ক ইউজারগুলো দেখাও

---

## Natural Language to SQL Query Generation

The platform converts user requests into SQL queries automatically.

Example:

User Input:

Show all users from Finance department

Generated SQL:

SELECT * FROM users
WHERE department = 'Finance';

Example:

User Input:

ফাইন্যান্স ডিপার্টমেন্টের ইউজারগুলো দেখাও

Generated SQL:

SELECT * FROM users
WHERE department = 'Finance';

The generated query is executed against the PostgreSQL database and results are displayed instantly.

---

## Voice to SQL

Users can also speak their requests.

Workflow:

Voice Input
→ Speech Recognition
→ Intent Detection
→ SQL Generation
→ Database Execution
→ Result Display

---

## System Architecture

User
↓
Web Dashboard
↓
AI Intent Detection Engine
↓
SQL Query Generator
↓
PostgreSQL Database
↓
Query Result Engine
↓
Dashboard Visualization

---

## Technology Stack

### Frontend

* HTML
* CSS
* JavaScript
* Chart.js

### Backend

* Python
* FastAPI

### Database

* PostgreSQL

### AI Components

* Intent Detection Engine
* SQL Query Generator
* Voice Recognition
* AI Security Assistant

---

## Database Schema

Main Users Table:

* id
* display_name
* email
* department
* mfa_enabled
* license_type
* last_login_days
* risk_score
* account_status

---

## Security Features

* Role Based Access Control (RBAC)
* Login Authentication
* User Session Management
* Identity Risk Monitoring
* Security Investigation Dashboard

---

## AI Workflow

1. User enters a question.
2. AI detects user intent.
3. Intent is converted into SQL.
4. SQL is executed on PostgreSQL.
5. Results are returned to the dashboard.
6. Security insights are displayed.

---

## Example Use Cases

### Inactive User Detection

Input:
Show inactive users

SQL:

SELECT *
FROM users
WHERE last_login_days > 90;

---

### Users Without MFA

Input:
Show users without MFA

SQL:

SELECT *
FROM users
WHERE mfa_enabled = false;

---

### High Risk Users

Input:
Show high risk users

SQL:

SELECT *
FROM users
WHERE risk_score > 70;

---

## Future Enhancements

* Real Microsoft Graph API Integration
* Microsoft Entra ID Live Data
* Azure OpenAI Integration
* Security Copilot Integration
* RAG Knowledge Base
* Multi-Agent AI Architecture
* Automated Security Recommendations

---

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
Author

Jasmin Doja

AI Engineer | Cloud Engineer

Project: EntraLens AI Identity Security Copilot
