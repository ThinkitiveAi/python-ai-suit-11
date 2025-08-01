import bcrypt
import uuid
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from ..patient_models import Patient
from ..patient_session_models import PatientSession
from ..utils.jwt_utils import generate_jwt_tokens
from ..utils.security_utils import (
    check_rate_limit, increment_failed_attempts, reset_failed_attempts,
    lock_account, is_account_locked, log_security_event
)

class PatientAuthService:
    @staticmethod
    def authenticate(identifier, password, ip_address, device_info, user_agent):
        # Accept either email or phone number
        try:
            if '@' in identifier:
                patient = Patient.objects.get(email__iexact=identifier.strip())
            else:
                patient = Patient.objects.get(phone_number=identifier.strip())
        except Patient.DoesNotExist:
            log_security_event(None, ip_address, 'login_failed', 'Identifier not found')
            return None, 'INVALID_CREDENTIALS', None

        # Check if account is locked
        if is_account_locked(patient):
            log_security_event(patient, ip_address, 'account_locked', 'Account is locked')
            return None, 'ACCOUNT_LOCKED', patient

        # Rate limit per IP
        if not check_rate_limit(ip_address):
            log_security_event(patient, ip_address, 'rate_limited', 'Too many attempts from IP')
            return None, 'RATE_LIMITED', patient

        # Password check
        if not bcrypt.checkpw(password.encode('utf-8'), patient.password_hash.encode('utf-8')):
            increment_failed_attempts(patient)
            log_security_event(patient, ip_address, 'login_failed', 'Invalid password')
            return None, 'INVALID_CREDENTIALS', patient

        # Pre-login checks
        if not patient.is_active:
            return None, 'ACCOUNT_INACTIVE', patient
        if not patient.email_verified:
            return None, 'EMAIL_NOT_VERIFIED', patient
        # Optionally: phone_verified

        reset_failed_attempts(patient)
        # Update login stats
        patient.last_login = timezone.now()
        patient.login_count += 1
        patient.save(update_fields=['last_login', 'login_count', 'failed_login_attempts', 'locked_until', 'last_failed_attempt'])

        # Session management (limit 3 concurrent sessions)
        PatientAuthService.cleanup_old_sessions(patient)
        # Device/IP logging and suspicious activity detection can be added here

        return patient, None, None

    @staticmethod
    def cleanup_old_sessions(patient):
        sessions = PatientSession.objects.filter(patient=patient, is_revoked=False).order_by('-created_at')
        if sessions.count() >= 3:
            for s in sessions[3:]:
                s.is_revoked = True
                s.save(update_fields=['is_revoked'])

    @staticmethod
    def create_session(patient, refresh_token, device_info, ip_address, user_agent, expires_at, location_info=None):
        from ..utils.security_utils import hash_token
        return PatientSession.objects.create(
            patient=patient,
            refresh_token_hash=hash_token(refresh_token),
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            last_used_at=timezone.now(),
            location_info=location_info,
        )
