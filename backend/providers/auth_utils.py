import bcrypt
import jwt
import hashlib
from datetime import datetime, timedelta
from django.conf import settings
from .models import Provider, RefreshToken

JWT_SECRET = getattr(settings, 'SECRET_KEY', 'changeme')
JWT_ALGORITHM = 'HS256'

ACCESS_TOKEN_EXPIRES = 60 * 60  # 1 hour
REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 7  # 7 days
ACCESS_TOKEN_EXPIRES_REMEMBER = 60 * 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRES_REMEMBER = 60 * 60 * 24 * 30  # 30 days


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_access_token(provider, remember_me=False):
    exp = datetime.utcnow() + timedelta(seconds=(ACCESS_TOKEN_EXPIRES_REMEMBER if remember_me else ACCESS_TOKEN_EXPIRES))
    payload = {
        'provider_id': str(provider.id),
        'email': provider.email,
        'role': 'provider',
        'specialization': provider.specialization,
        'verification_status': provider.verification_status,
        'exp': exp,
        'type': 'access',
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM), exp

def create_refresh_token(provider, remember_me=False):
    exp = datetime.utcnow() + timedelta(seconds=(REFRESH_TOKEN_EXPIRES_REMEMBER if remember_me else REFRESH_TOKEN_EXPIRES))
    payload = {
        'provider_id': str(provider.id),
        'email': provider.email,
        'exp': exp,
        'type': 'refresh',
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # Store hashed token in DB
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    RefreshToken.objects.create(provider=provider, token_hash=token_hash, expires_at=exp)
    return token, exp

def verify_refresh_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get('type') != 'refresh':
            return None
        token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        qs = RefreshToken.objects.filter(token_hash=token_hash, is_revoked=False, expires_at__gt=datetime.utcnow())
        if not qs.exists():
            return None
        return payload
    except Exception:
        return None
