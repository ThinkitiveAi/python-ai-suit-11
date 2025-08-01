from django.utils import timezone
from datetime import timedelta
import hashlib
from ..patient_models import Patient
from ..patient_session_models import PatientSession

RATE_LIMIT = 3  # per 10 min per IP
RATE_LIMIT_WINDOW = timedelta(minutes=10)
LOCKOUT_THRESHOLD_1 = 3  # 1 hour lock
LOCKOUT_THRESHOLD_2 = 5  # 24 hour lock
LOCKOUT_DURATION_1 = timedelta(hours=1)
LOCKOUT_DURATION_2 = timedelta(hours=24)

_ip_attempts = {}

def check_rate_limit(ip):
    now = timezone.now()
    attempts = _ip_attempts.get(ip, [])
    attempts = [t for t in attempts if now - t < RATE_LIMIT_WINDOW]
    if len(attempts) >= RATE_LIMIT:
        return False
    attempts.append(now)
    _ip_attempts[ip] = attempts
    return True

def increment_failed_attempts(patient):
    now = timezone.now()
    patient.failed_login_attempts += 1
    patient.last_failed_attempt = now
    if patient.failed_login_attempts == LOCKOUT_THRESHOLD_1:
        patient.locked_until = now + LOCKOUT_DURATION_1
    elif patient.failed_login_attempts >= LOCKOUT_THRESHOLD_2:
        patient.locked_until = now + LOCKOUT_DURATION_2
    patient.save(update_fields=['failed_login_attempts', 'last_failed_attempt', 'locked_until'])

def reset_failed_attempts(patient):
    patient.failed_login_attempts = 0
    patient.locked_until = None
    patient.save(update_fields=['failed_login_attempts', 'locked_until'])

def is_account_locked(patient):
    if patient.locked_until and patient.locked_until > timezone.now():
        return True
    return False

def lock_account(patient, duration):
    patient.locked_until = timezone.now() + duration
    patient.save(update_fields=['locked_until'])

def hash_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

def log_security_event(patient, ip, event_type, message):
    # HIPAA-compliant: do not log PHI
    from ..models import SecurityLog
    SecurityLog.objects.create(
        patient=patient,
        ip_address=ip,
        event_type=event_type,
        message=message,
        timestamp=timezone.now(),
    )
