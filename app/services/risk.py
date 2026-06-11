def risk_level(score: int) -> str:
    if score >= 85: return 'Critical'
    if score >= 70: return 'High'
    if score >= 45: return 'Medium'
    return 'Low'

def calculate_identity_risk(user, is_privileged=False):
    score = 10
    if not user.mfa_enabled: score += 25
    if user.last_login_days >= 90: score += 20
    if is_privileged: score += 20
    if user.account_status == 'terminated': score += 30
    if user.user_type == 'contractor': score += 8
    return min(score, 100)
