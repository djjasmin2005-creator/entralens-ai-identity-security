from fastapi import FastAPI, Depends, Request, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import io, csv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .database import get_db, Base, engine
from .models import UserIdentity, RoleAssignment, SignInLog, AuditEvent
from .seed import seed
from .services.ai import classify_intent, generate_answer, vision_demo
from .services.mock_azure import azure_mapping
from .services.risk import risk_level

import os
import requests
from sqlalchemy import text
TEXT_MODEL = os.getenv("OLLAMA_TEXT_MODEL", "gemma4:31b-cloud")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

ALLOWED_ROLES = [
    "Security Analyst",
    "IAM Engineer",
    "SOC Team",
    "Azure Cloud Engineer",
    "IT Administrator",
    "Compliance Team",
    "Enterprise Security Manager",
    "Global Administrator",
]

DEMO_USERS = {
    "secadmin": {"password": "password1230", "role": "Global Administrator"},
    "itadmin": {"password": "password1230", "role": "IT Administrator"},
    "security": {"password": "password1230", "role": "Security Analyst"},
    "iam": {"password": "password1230", "role": "IAM Engineer"},
    "soc": {"password": "password1230", "role": "SOC Team"},
    "azure": {"password": "password1230", "role": "Azure Cloud Engineer"},
    "compliance": {"password": "password1230", "role": "Compliance Team"},
    "manager": {"password": "password1230", "role": "Enterprise Security Manager"},
    "billing": {"password": "password1230", "role": "Billing Administrator"},
    "vmoperator": {"password": "password1230", "role": "VM Operator"},
}


def require_role(role: str, feature: str = "dashboard"):
    if role in ALLOWED_ROLES:
        return True

    if role == "Billing Administrator" and feature in [
        "license-optimization",
        "orphan-accounts",
        "inactive-users",
    ]:
        return True

    return False
def build_user_record(user):
    return {
        "name": user.display_name,
        "email": user.email,
        "department": user.department,
        "mfa": user.mfa_enabled,
        "license": user.license_type,
        "last_login_days": user.last_login_days,
        "risk_score": user.risk_score,
        "status": user.account_status,
    }


def get_identity_data(db: Session, feature: str):
    q = db.query(UserIdentity)

    if feature in ["inactive-users", "inactive_users"]:
        rows = q.filter(UserIdentity.last_login_days >= 90).all()
        title = "Inactive User Detection"

    elif feature in ["mfa-compliance", "mfa_compliance"]:
        rows = q.filter(UserIdentity.mfa_enabled == False).all()
        title = "MFA Compliance Check"

    elif feature in ["license-optimization", "license_optimization"]:
        rows = q.filter(
            UserIdentity.license_type == "E5",
            UserIdentity.last_login_days >= 60
        ).all()
        title = "License Optimization"

    elif feature in ["orphan-accounts", "orphan_accounts"]:
        rows = q.filter(UserIdentity.account_status == "terminated").all()
        title = "Orphan Account Detection"

    elif feature in ["identity-governance", "identity_governance"]:
        rows = q.filter(UserIdentity.risk_score >= 70).all()
        title = "Identity Governance Review"

    elif feature in ["conditional-access", "conditional_access_investigation"]:
        rows = q.filter(UserIdentity.risk_score >= 60).all()
        title = "Conditional Access Investigation"

    elif feature in ["privileged-monitoring", "privileged_monitoring"]:
        privileged_emails = [
            r.user_email for r in db.query(RoleAssignment)
            .filter(RoleAssignment.privileged == True)
            .all()
        ]
        rows = q.filter(UserIdentity.email.in_(privileged_emails)).all()
        title = "Privileged Account Monitoring"

    else:
        rows = q.order_by(UserIdentity.risk_score.desc()).limit(20).all()
        title = "Security Summary"

    records = [build_user_record(user) for user in rows]

    return {
        "title": title,
        "count": len(records),
        "records": records,
        "emails": [r["email"] for r in records],
    }
app = FastAPI(title='EntraLens Demo API', version='1.0.0')
app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')

@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)
    seed()

@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get('/api/health')
def health():
    return {'status': 'ok', 'app': 'EntraLens', 'mode': 'full-demo'}

@app.get('/api/azure/mock-map')
def mock_map():
    return azure_mapping()

@app.get('/api/dashboard')
def dashboard(db: Session = Depends(get_db)):
    total = db.query(UserIdentity).count()
    inactive = db.query(UserIdentity).filter(UserIdentity.last_login_days >= 90).count()
    no_mfa = db.query(UserIdentity).filter(UserIdentity.mfa_enabled == False).count()
    privileged = db.query(RoleAssignment).filter(RoleAssignment.privileged == True).count()
    active = db.query(UserIdentity).filter(UserIdentity.account_status == 'active').count()
    orphan = db.query(UserIdentity).filter(UserIdentity.account_status == 'terminated').count()
    avg_risk = int(db.query(func.avg(UserIdentity.risk_score)).scalar() or 0)
    risky = db.query(UserIdentity).order_by(UserIdentity.risk_score.desc()).limit(5).all()
    alerts = db.query(SignInLog).filter(SignInLog.risk_level.in_(['high','medium'])).limit(5).all()
    return {
        'cards': {'total_users': total, 'active_users': active, 'inactive_users': inactive, 'users_without_mfa': no_mfa, 'privileged_accounts': privileged, 'risk_score': avg_risk},
        'ai_summary': [f'{inactive} inactive users found. Consider cleanup.', f'{no_mfa} users are not MFA enabled.', f'{privileged} privileged accounts detected.', f'{orphan} orphan accounts require attention.', 'License optimization can save estimated 18% costs.'],
        'top_risky_users': [{'email': u.email, 'risk_score': u.risk_score, 'risk_level': risk_level(u.risk_score), 'issues': (0 if u.mfa_enabled else 1) + (1 if u.last_login_days>=90 else 0)} for u in risky],
        'issues_distribution': {'Inactive Users': inactive, 'MFA Not Enabled': no_mfa, 'Orphan Accounts': orphan, 'Privileged Accounts': privileged, 'Others': 3},
        'recent_alerts': [{'title': 'Unusual sign-in activity detected', 'user': a.user_email, 'severity': a.risk_level, 'time': f'{a.created_days_ago}d ago'} for a in alerts],
        'trend': [70,66,67,72,78,73,74,79,86,83,79,72,68,68,70,77,75,70,66,69,72,68,72]
    }

@app.get("/api/identity/{feature}")
def identity_feature(feature: str, db: Session = Depends(get_db)):
    data = get_identity_data(db, feature)

    return {
        "title": data["title"],
        "count": data["count"],
        "records": data["records"],
        "summary": f"{data['title']} completed. {data['count']} matching records were found."
    }
@app.get('/api/roles/global-admins')
def global_admins(db: Session = Depends(get_db)):
    rows = db.query(RoleAssignment).filter(RoleAssignment.role_name.like('%Administrator%')).all()
    return [{'email': r.user_email, 'role': r.role_name, 'privileged': r.privileged, 'assigned_days_ago': r.assigned_days_ago} for r in rows]
@app.post("/api/login")
def login(payload: dict):
    username = payload.get("username", "").lower()
    password = payload.get("password", "")

    user = DEMO_USERS.get(username)

    if not user or user["password"] != password:
        return {
            "success": False,
            "message": "Invalid username or password."
        }

    if not require_role(user["role"]):
        return {
            "success": False,
            "message": f"Access denied. {user['role']} is not allowed to access EntraLens dashboard."
        }

    return {
        "success": True,
        "username": username,
        "role": user["role"],
        "message": "Login successful."
    }
@app.post("/api/chat")
def chat(payload: dict, db: Session = Depends(get_db)):
    question = payload.get("message", "")
    allowed_keywords = [
        "mfa", "inactive", "user", "users", "login", "sign-in", "admin",
        "administrator", "privileged", "license", "orphan", "terminated",
        "access", "identity", "governance", "risk", "soc", "alert",
        "security", "conditional", "review", "entra", "password"
    ]

    if not any(word in question.lower() for word in allowed_keywords):
        return {
            "answer": "Sorry, it is an invalid question. Please ask a question related to identity security, MFA, users, access, risk, license, or SOC investigation.",
            "count": 0,
            "sources": []
        }
    intent = classify_intent(question)

    if intent == "mfa_compliance":
        result = get_identity_data(db, "mfa-compliance")
        data = {"count": result["count"], "records": result["emails"]}

    elif intent == "inactive_users":
        result = get_identity_data(db, "inactive-users")
        data = {"count": result["count"], "records": result["emails"]}

    elif intent == "license_optimization":
        result = get_identity_data(db, "license-optimization")
        data = {"count": result["count"], "records": result["emails"]}

    elif intent == "orphan_accounts":
        result = get_identity_data(db, "orphan-accounts")
        data = {"count": result["count"], "records": result["emails"]}

    elif intent == "privileged_monitoring":
        result = get_identity_data(db, "privileged-monitoring")
        data = {"count": result["count"], "records": result["emails"]}

    elif intent == "conditional_access_investigation":
        result = get_identity_data(db, "conditional-access")
        data = {"count": result["count"], "records": result["emails"]}

    elif intent == "global_admin_audit":
        rows = db.query(RoleAssignment).filter(
            RoleAssignment.role_name.like("%Administrator%")
        ).all()
        data = {
            "count": len(rows),
            "records": [r.user_email for r in rows]
        }

    elif intent == "access_review":
        result = get_identity_data(db, "identity-governance")
        data = {"count": result["count"], "records": result["emails"]}

    elif intent == "soc_investigation":
        result = get_identity_data(db, "identity-governance")
        data = {"count": result["count"], "records": result["emails"]}

    else:
        result = get_identity_data(db, "security-summary")
        data = {"count": result["count"], "records": result["emails"]}

    ai = generate_answer(db, question, data)

    return {
        "answer": ai["answer"],
        "count": data["count"],
        "sources": ai.get("sources", [])
    }
from sqlalchemy import text

@app.post("/api/sql/run")
def run_sql(payload: dict, db: Session = Depends(get_db)):
    query = payload.get("query", "").strip()

    if not query.lower().startswith("select"):
        return {
            "success": False,
            "message": "Only SELECT queries are allowed for security.",
            "rows": []
        }

    try:
        result = db.execute(text(query))
        rows = [dict(row._mapping) for row in result]
        return {
            "success": True,
            "message": f"{len(rows)} rows returned.",
            "rows": rows
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "rows": []
        }

@app.post("/api/sql/ai-generate")
def ai_generate_sql(payload: dict):
    question = payload.get("question", "").strip()

    if not question:
        return {
            "success": False,
            "message": "Please enter a question.",
            "sql": ""
        }

    schema_context = """
Database: entralens_db

Table: users
Columns:
id, tenant_id, display_name, email, department, user_type,
mfa_enabled, license_type, last_login_days, risk_score, account_status

Table: role_assignments
Columns:
id, user_email, role_name, privileged, assigned_date

Table: sign_in_logs
Columns:
id, user_email, login_time, ip_address, country, status

Table: audit_events
Columns:
id, event_type, user_email, description, created_at
"""

    prompt = f"""
You are EntraLens bilingual AI SQL generator.

The user may ask in English, Bengali, or mixed Bangla-English.
Understand the user's intent and generate ONE safe PostgreSQL SELECT query.

Rules:
- Return SQL only.
- No markdown.
- No explanation.
- Only SELECT queries are allowed.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, REVOKE.
- Use only the tables and columns in the schema.
- For text comparison, always use LOWER(column) = LOWER('value').
- For department search, use users.department.
- For MFA disabled, use mfa_enabled = false.
- For inactive users, use last_login_days >= 90.
- For terminated/orphan accounts, use account_status = 'terminated'.
- For high risk users, use risk_score >= 70.
- For privileged accounts, use role_assignments.privileged = true.

Bangla examples:
Finance department-er user dekhao
→ SELECT * FROM users WHERE LOWER(department) = LOWER('Finance');

ফাইন্যান্স ডিপার্টমেন্টের ইউজার দেখাও
→ SELECT * FROM users WHERE LOWER(department) = LOWER('Finance');

MFA enable na thaka user dekhao
→ SELECT * FROM users WHERE mfa_enabled = false;

যেসব user 90 দিনের বেশি login করে নাই দেখাও
→ SELECT * FROM users WHERE last_login_days >= 90;

High risk user কারা
→ SELECT * FROM users WHERE risk_score >= 70 ORDER BY risk_score DESC;

Schema:
{schema_context}

User question:
{question}
"""

    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": TEXT_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=25
        )

        if r.ok:
            sql = r.json().get("response", "").strip()
        else:
            sql = ""

    except Exception:
        sql = ""

    if not sql:
        sql = fallback_bilingual_sql(question)

    sql = clean_sql(sql)

    unsafe_words = [
        "insert", "update", "delete", "drop", "alter",
        "truncate", "create", "grant", "revoke"
    ]

    sql_lower = sql.lower()

    if any(word in sql_lower for word in unsafe_words):
        return {
            "success": False,
            "message": "Unsafe SQL blocked. Only SELECT queries are allowed.",
            "sql": ""
        }

    if not sql_lower.startswith("select"):
        return {
            "success": False,
            "message": "Only SELECT queries are allowed.",
            "sql": ""
        }

    return {
        "success": True,
        "intent": question,
        "sql": sql
    }
def clean_sql(sql: str):
    sql = sql.strip()
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    if ";" not in sql:
        sql += ";"

    return sql


def fallback_bilingual_sql(question: str):
    q = question.lower()

    finance_words = ["finance", "ফাইন্যান্স"]
    it_words = ["it", "আইটি"]
    hr_words = ["hr", "এইচআর"]
    marketing_words = ["marketing", "মার্কেটিং"]
    security_words = ["security", "সিকিউরিটি"]

    if any(w in q for w in finance_words):
        return "SELECT * FROM users WHERE LOWER(department) = LOWER('Finance');"

    if any(w in q for w in it_words):
        return "SELECT * FROM users WHERE LOWER(department) = LOWER('IT');"

    if any(w in q for w in hr_words):
        return "SELECT * FROM users WHERE LOWER(department) = LOWER('HR');"

    if any(w in q for w in marketing_words):
        return "SELECT * FROM users WHERE LOWER(department) = LOWER('Marketing');"

    if any(w in q for w in security_words):
        return "SELECT * FROM users WHERE LOWER(department) = LOWER('Security');"

    if "mfa" in q or "এমএফএ" in q:
        return "SELECT * FROM users WHERE mfa_enabled = false;"

    if "inactive" in q or "ইনঅ্যাকটিভ" in q or "login" in q or "লগইন" in q:
        return "SELECT * FROM users WHERE last_login_days >= 90 ORDER BY last_login_days DESC;"

    if "license" in q or "লাইসেন্স" in q:
        return "SELECT * FROM users WHERE license_type = 'E5' AND last_login_days >= 60;"

    if "orphan" in q or "terminated" in q or "টার্মিনেটেড" in q:
        return "SELECT * FROM users WHERE account_status = 'terminated';"

    if "risk" in q or "রিস্ক" in q:
        return "SELECT * FROM users WHERE risk_score >= 70 ORDER BY risk_score DESC;"

    if "privileged" in q or "প্রিভিলেজ" in q:
        return "SELECT * FROM role_assignments WHERE privileged = true;"

    if "all user" in q or "সব user" in q or "সব ইউজার" in q:
        return "SELECT * FROM users ORDER BY id ASC;"

    return "SELECT 'Invalid question for EntraLens database' AS message;"


@app.get("/api/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(UserIdentity).order_by(UserIdentity.risk_score.desc()).all()

    return [
        {
            "id": u.id,
            "name": u.display_name,
            "email": u.email,
            "department": u.department,
            "mfa": u.mfa_enabled,
            "license": u.license_type,
            "last_login_days": u.last_login_days,
            "risk_score": u.risk_score,
            "status": u.account_status,
        }
        for u in users
    ]


@app.post("/api/users")
def create_user(payload: dict, db: Session = Depends(get_db)):
    role = payload.get("role", "")

    if not require_role(role):
        return {"success": False, "message": "Access denied."}

    user = UserIdentity(
        display_name=payload.get("name"),
        email=payload.get("email"),
        department=payload.get("department", "IT"),
        mfa_enabled=payload.get("mfa", False),
        license_type=payload.get("license", "E3"),
        last_login_days=int(payload.get("last_login_days", 0)),
        risk_score=int(payload.get("risk_score", 50)),
        account_status=payload.get("status", "active"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"success": True, "message": "User created successfully.", "id": user.id}


@app.put("/api/users/{user_id}")
def update_user(user_id: int, payload: dict, db: Session = Depends(get_db)):
    role = payload.get("role", "")

    if not require_role(role):
        return {"success": False, "message": "Access denied."}

    user = db.query(UserIdentity).filter(UserIdentity.id == user_id).first()

    if not user:
        return {"success": False, "message": "User not found."}

    user.display_name = payload.get("name", user.display_name)
    user.email = payload.get("email", user.email)
    user.department = payload.get("department") or user.department
    user.mfa_enabled = payload.get("mfa", user.mfa_enabled)
    user.license_type = payload.get("license", user.license_type)
    user.last_login_days = int(
        payload.get("last_login_days") or user.last_login_days
    )

    user.risk_score = int(
        payload.get("risk_score") or user.risk_score
    )
    user.account_status = payload.get("status", user.account_status)

    db.commit()

    return {"success": True, "message": "User updated successfully."}


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, role: str, db: Session = Depends(get_db)):
    if not require_role(role):
        return {"success": False, "message": "Access denied."}

    user = db.query(UserIdentity).filter(UserIdentity.id == user_id).first()

    if not user:
        return {"success": False, "message": "User not found."}

    db.delete(user)
    db.commit()

    return {"success": True, "message": "User deleted successfully."}
@app.post('/api/vision/analyze')
def vision(file: UploadFile = File(...)):
    return vision_demo(file.filename)

@app.get('/api/reports/export.csv')
def export_csv(db: Session = Depends(get_db)):
    buf = io.StringIO(); writer = csv.writer(buf)
    writer.writerow(['email','department','mfa_enabled','license','last_login_days','risk_score','status'])
    for u in db.query(UserIdentity).all(): writer.writerow([u.email,u.department,u.mfa_enabled,u.license_type,u.last_login_days,u.risk_score,u.account_status])
    return StreamingResponse(iter([buf.getvalue()]), media_type='text/csv', headers={'Content-Disposition':'attachment; filename=entralens_identity_report.csv'})

@app.get('/api/reports/export.pdf')
def export_pdf(db: Session = Depends(get_db)):
    buffer = io.BytesIO(); doc = SimpleDocTemplate(buffer); styles = getSampleStyleSheet(); story=[]
    story.append(Paragraph('EntraLens Identity Security Report', styles['Title'])); story.append(Spacer(1,12))
    for u in db.query(UserIdentity).order_by(UserIdentity.risk_score.desc()).limit(10).all():
        story.append(Paragraph(f'{u.email} | Risk: {u.risk_score} | MFA: {u.mfa_enabled} | Last Login: {u.last_login_days} days', styles['BodyText']))
    doc.build(story); buffer.seek(0)
    return StreamingResponse(buffer, media_type='application/pdf', headers={'Content-Disposition':'attachment; filename=entralens_identity_report.pdf'})
