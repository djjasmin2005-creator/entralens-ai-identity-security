import os
import requests
from .rag import retrieve_knowledge

TEXT_MODEL = os.getenv("OLLAMA_TEXT_MODEL", "gemma4:31b-cloud")
VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "qwen3-VL:235-cloud")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def classify_intent(q: str):
    text = q.lower()
    if "mfa" in text:
        return "mfa_compliance"
    if "inactive" in text or "not logged" in text or "dormant" in text:
        return "inactive_users"
    if "global admin" in text or "administrator" in text:
        return "global_admin_audit"
    if "privileged" in text or "privilege" in text:
        return "privileged_monitoring"
    if "license" in text or "cost" in text:
        return "license_optimization"
    if "orphan" in text or "terminated" in text or "left" in text:
        return "orphan_accounts"
    if "failed" in text or "sign-in" in text or "conditional" in text or "outside" in text:
        return "conditional_access_investigation"
    if "access review" in text or "contractor" in text:
        return "access_review"
    if "soc" in text or "alert" in text or "suspicious" in text:
        return "soc_investigation"
    return "security_summary"


def generate_answer(db, question, data):
    docs = retrieve_knowledge(db, question)
    intent = classify_intent(question)

    answer = premium_enterprise_answer(intent, data)

    return {
        "answer": answer,
        "model": TEXT_MODEL,
        "sources": [d.title for d in docs],
    }


def premium_enterprise_answer(intent, data):
    count = data.get("count", 0)

    if intent == "mfa_compliance":
        return f"""🔐 MFA Compliance Analysis

There are currently {count} users using Multi-Factor Authentication (MFA).

Status: Healthy
Risk Level: Low

Recommended Action:
Continue periodic MFA compliance reviews and ensure all privileged accounts remain protected."""

    if intent == "inactive_users":
        return f"""👤 Inactive User Detection

There are currently {count} inactive user accounts in the identity environment.

Status: Attention Required
Risk Level: Medium

Recommended Action:
Review inactive accounts, disable unnecessary access, and document cleanup decisions."""

    if intent == "global_admin_audit":
        return f"""🛡️ Global Administrator Audit

There are currently {count} Global Administrator accounts detected.

Status: Requires Review
Risk Level: High

Recommended Action:
Verify all Global Administrator accounts, remove unnecessary privileges, and enforce MFA."""

    if intent == "privileged_monitoring":
        return f"""🔑 Privileged Account Monitoring

There are currently {count} privileged accounts identified.

Status: Monitoring Required
Risk Level: High

Recommended Action:
Review privileged access regularly and apply least-privilege access controls."""

    if intent == "license_optimization":
        return f"""💳 License Optimization Analysis

There are currently {count} license-related records requiring review.

Status: Optimization Opportunity
Risk Level: Low

Recommended Action:
Review unused or inactive licenses to reduce unnecessary cloud subscription costs."""

    if intent == "orphan_accounts":
        return f"""⚠️ Orphan Account Detection

There are currently {count} orphan or terminated-user accounts requiring attention.

Status: Immediate Review Required
Risk Level: High

Recommended Action:
Disable or remove orphan accounts after verification with HR or identity governance records."""

    if intent == "conditional_access_investigation":
        return f"""🌐 Conditional Access Investigation

There are currently {count} conditional access or sign-in related events detected.

Status: Investigation Required
Risk Level: Medium

Recommended Action:
Review failed sign-ins, location anomalies, and policy enforcement results."""

    if intent == "access_review":
        return f"""📋 Access Review Summary

There are currently {count} access review records found.

Status: Review Required
Risk Level: Medium

Recommended Action:
Validate user access, remove unnecessary permissions, and complete access review documentation."""

    if intent == "soc_investigation":
        return f"""🚨 SOC Investigation Summary

There are currently {count} security operation records detected.

Status: Active Monitoring
Risk Level: Medium

Recommended Action:
Prioritize high-risk alerts and escalate suspicious identity activity for investigation."""

    return f"""🤖 AI Security Summary

There are currently {count} matching identity security records.

Status: Review Recommended
Risk Level: Medium

Recommended Action:
Review the detected records and apply the appropriate identity security controls."""


def fallback_answer(question, data):
    count = data.get("count", 0)
    return f"""🤖 AI Security Summary

There are currently {count} matching identity security records.

Recommended Action:
Review high-risk users first, enforce MFA, clean inactive or orphan accounts, and document access review decisions."""


def vision_demo(filename: str):
    return {
        "model": VISION_MODEL,
        "summary": f"Demo Vision AI analyzed {filename}. It appears to be an identity/security related image or report.",
        "detected_items": ["risk metric", "security alert", "user/account information"],
        "recommended_action": "Attach this analysis to the SOC investigation report and validate extracted details.",
    }