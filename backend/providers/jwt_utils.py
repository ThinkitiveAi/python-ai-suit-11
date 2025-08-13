"""
JWT Utilities for Patient and Provider Authentication
"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .patient_models import Patient
from .models import Provider

# JWT Configuration
JWT_SECRET_KEY = getattr(settings, 'SECRET_KEY', 'your-secret-key-here')
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_LIFETIME = timedelta(hours=24)  # 24 hours
JWT_REFRESH_TOKEN_LIFETIME = timedelta(days=7)   # 7 days

def generate_patient_tokens(patient):
    """
    Generate access and refresh tokens for a patient
    """
    now = timezone.now()
    
    # Access token payload
    access_payload = {
        'user_id': str(patient.id),
        'user_type': 'patient',
        'email': patient.email,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'iat': int(now.timestamp()),
        'exp': int((now + JWT_ACCESS_TOKEN_LIFETIME).timestamp()),
        'token_type': 'access'
    }
    
    # Refresh token payload
    refresh_payload = {
        'user_id': str(patient.id),
        'user_type': 'patient',
        'email': patient.email,
        'iat': int(now.timestamp()),
        'exp': int((now + JWT_REFRESH_TOKEN_LIFETIME).timestamp()),
        'token_type': 'refresh'
    }
    
    # Generate tokens
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'access_token_expires_at': (now + JWT_ACCESS_TOKEN_LIFETIME).isoformat(),
        'refresh_token_expires_at': (now + JWT_REFRESH_TOKEN_LIFETIME).isoformat(),
        'token_type': 'Bearer'
    }

def generate_provider_tokens(provider):
    """
    Generate access and refresh tokens for a provider
    """
    now = timezone.now()
    
    # Access token payload
    access_payload = {
        'user_id': str(provider.id),
        'user_type': 'provider',
        'email': provider.email,
        'first_name': provider.first_name,
        'last_name': provider.last_name,
        'specialization': provider.specialization,
        'verification_status': provider.verification_status,
        'iat': int(now.timestamp()),
        'exp': int((now + JWT_ACCESS_TOKEN_LIFETIME).timestamp()),
        'token_type': 'access'
    }
    
    # Refresh token payload
    refresh_payload = {
        'user_id': str(provider.id),
        'user_type': 'provider',
        'email': provider.email,
        'iat': int(now.timestamp()),
        'exp': int((now + JWT_REFRESH_TOKEN_LIFETIME).timestamp()),
        'token_type': 'refresh'
    }
    
    # Generate tokens
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'access_token_expires_at': (now + JWT_ACCESS_TOKEN_LIFETIME).isoformat(),
        'refresh_token_expires_at': (now + JWT_REFRESH_TOKEN_LIFETIME).isoformat(),
        'token_type': 'Bearer'
    }

def decode_token(token):
    """
    Decode and validate a JWT token
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def get_user_from_token(token):
    """
    Get user object from JWT token
    """
    try:
        payload = decode_token(token)
        user_id = payload.get('user_id')
        user_type = payload.get('user_type')
        
        if user_type == 'patient':
            return Patient.objects.get(id=user_id, is_active=True)
        elif user_type == 'provider':
            return Provider.objects.get(id=user_id, is_active=True)
        else:
            raise Exception("Invalid user type")
            
    except (Patient.DoesNotExist, Provider.DoesNotExist):
        raise Exception("User not found")
    except Exception as e:
        raise Exception(f"Token validation failed: {str(e)}")

def refresh_access_token(refresh_token):
    """
    Generate a new access token from a valid refresh token
    """
    try:
        payload = decode_token(refresh_token)
        
        if payload.get('token_type') != 'refresh':
            raise Exception("Invalid token type")
            
        user_id = payload.get('user_id')
        user_type = payload.get('user_type')
        
        if user_type == 'patient':
            user = Patient.objects.get(id=user_id, is_active=True)
            return generate_patient_tokens(user)
        elif user_type == 'provider':
            user = Provider.objects.get(id=user_id, is_active=True)
            return generate_provider_tokens(user)
        else:
            raise Exception("Invalid user type")
            
    except (Patient.DoesNotExist, Provider.DoesNotExist):
        raise Exception("User not found")
    except Exception as e:
        raise Exception(f"Token refresh failed: {str(e)}")
