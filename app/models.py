from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .database import Base

class Tenant(Base):
    __tablename__ = 'tenants'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    plan: Mapped[str] = mapped_column(String(50), default='demo')

class UserIdentity(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey('tenants.id'), default=1)
    display_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(180), unique=True)
    department: Mapped[str] = mapped_column(String(100))
    user_type: Mapped[str] = mapped_column(String(40), default='employee')
    account_status: Mapped[str] = mapped_column(String(40), default='active')
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    license_type: Mapped[str] = mapped_column(String(40), default='E3')
    last_login_days: Mapped[int] = mapped_column(Integer, default=1)
    risk_score: Mapped[int] = mapped_column(Integer, default=10)
    country: Mapped[str] = mapped_column(String(80), default='United States')

class RoleAssignment(Base):
    __tablename__ = 'role_assignments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_email: Mapped[str] = mapped_column(String(180))
    role_name: Mapped[str] = mapped_column(String(120))
    privileged: Mapped[bool] = mapped_column(Boolean, default=False)
    assigned_days_ago: Mapped[int] = mapped_column(Integer, default=1)

class SignInLog(Base):
    __tablename__ = 'sign_in_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_email: Mapped[str] = mapped_column(String(180))
    status: Mapped[str] = mapped_column(String(40))
    country: Mapped[str] = mapped_column(String(80))
    ip_address: Mapped[str] = mapped_column(String(60))
    risk_level: Mapped[str] = mapped_column(String(40), default='low')
    created_days_ago: Mapped[int] = mapped_column(Integer, default=0)

class KnowledgeDoc(Base):
    __tablename__ = 'knowledge_docs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(120), default='demo-policy')

class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100))
    user_email: Mapped[str] = mapped_column(String(180))
    severity: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
