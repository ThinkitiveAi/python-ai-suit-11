import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_jwt_tokens(patient, remember_me=False):
    now = datetime.utcnow()
    access_exp = now + timedelta(hours=4 if remember_me else 0.5)
    refresh_exp = now + timedelta(days=30 if remember_me else 7)
    payload = {
        'patient_id': str(patient.id),
        'email': patient.email,
        'role': 'patient',
        'email_verified': patient.email_verified,
        'phone_verified': patient.phone_verified,
        'exp': access_exp,
        'type': 'access',
    }
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    refresh_payload = {
        'patient_id': str(patient.id),
        'exp': refresh_exp,
        'type': 'refresh',
    }
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
    return access_token, refresh_token, int((access_exp - now).total_seconds()), int((refresh_exp - now).total_seconds())
