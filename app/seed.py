from .database import Base, engine, SessionLocal
from .models import Tenant, UserIdentity, RoleAssignment, SignInLog, KnowledgeDoc, AuditEvent

USERS = [
 ('John Doe','john.doe@acme.com','Finance','employee','active',False,'E5',120,95,'United States'),
 ('Admin Service','admin.service@acme.com','IT','service','active',False,'E5',68,90,'United States'),
 ('Sarah Jones','sarah.jones@acme.com','HR','employee','active',True,'E3',12,85,'United States'),
 ('Michael Brown','michael.brown@acme.com','Sales','employee','active',False,'E5',95,78,'Canada'),
 ('Emily Davis','emily.davis@acme.com','Marketing','contractor','active',True,'E3',40,65,'United States'),
 ('David Wilson','david.wilson@acme.com','IT','employee','active',True,'E5',2,55,'Germany'),
 ('Jane Smith','jane.smith@acme.com','Security','employee','active',True,'E5',5,60,'United States'),
 ('Mark Taylor','mark.taylor@acme.com','Operations','employee','active',False,'E3',7,72,'United States'),
 ('Former User','former.user@acme.com','Finance','employee','terminated',False,'E5',210,88,'United States'),
 ('Lisa Contractor','lisa.contractor@acme.com','External','contractor','active',False,'E3',101,74,'India'),
]
ROLES = [
 ('john.doe@acme.com','Global Administrator',True,400),
 ('admin.service@acme.com','Privileged Role Administrator',True,250),
 ('jane.smith@acme.com','Security Administrator',True,32),
 ('david.wilson@acme.com','User Administrator',True,12),
 ('sarah.jones@acme.com','Reports Reader',False,20),
]
LOGS = [
 ('admin.service@acme.com','failed','Russia','185.24.10.5','high',0),
 ('david.wilson@acme.com','failed','Germany','80.20.10.9','medium',0),
 ('jane.smith@acme.com','success','United States','172.16.2.3','medium',0),
 ('mark.taylor@acme.com','success','United States','10.1.2.3','high',0),
 ('lisa.contractor@acme.com','failed','India','117.12.2.5','medium',1),
]
DOCS = [
 ('MFA Policy','All privileged and employee accounts must use multi-factor authentication. Accounts without MFA should be remediated within 7 days.','security-policy'),
 ('Inactive Account Policy','Accounts inactive for more than 90 days must be reviewed. Accounts inactive for 180 days should be disabled unless business justification exists.','iam-policy'),
 ('Privileged Access Standard','Global Administrators and Privileged Role Administrators must be reviewed monthly and should not use daily work accounts for privileged access.','governance'),
 ('License Optimization Rule','E5 licenses assigned to users inactive for 60 days should be reviewed for cost optimization.','finops'),
 ('Orphan Account Control','Terminated employees with active accounts are critical security findings and require immediate disablement.','audit'),
]

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(Tenant).first():
            db.add(Tenant(id=1, name='Acme Demo Tenant', plan='enterprise-demo'))
        if not db.query(UserIdentity).first():
            for u in USERS:
                db.add(UserIdentity(tenant_id=1, display_name=u[0], email=u[1], department=u[2], user_type=u[3], account_status=u[4], mfa_enabled=u[5], license_type=u[6], last_login_days=u[7], risk_score=u[8], country=u[9]))
        if not db.query(RoleAssignment).first():
            for r in ROLES:
                db.add(RoleAssignment(user_email=r[0], role_name=r[1], privileged=r[2], assigned_days_ago=r[3]))
        if not db.query(SignInLog).first():
            for l in LOGS:
                db.add(SignInLog(user_email=l[0], status=l[1], country=l[2], ip_address=l[3], risk_level=l[4], created_days_ago=l[5]))
        if not db.query(KnowledgeDoc).first():
            for d in DOCS:
                db.add(KnowledgeDoc(title=d[0], content=d[1], source=d[2]))
        db.add(AuditEvent(event_type='demo_seed', user_email='system@entralens.local', severity='info', description='Demo data initialized'))
        db.commit()
    finally:
        db.close()

if __name__ == '__main__':
    seed()
    print('EntraLens demo database seeded.')
