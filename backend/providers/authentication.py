"""
Custom JWT Authentication for Patients and Providers
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from .jwt_utils import get_user_from_token

class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication for both patients and providers
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
            
        try:
            # Check if the header starts with 'Bearer '
            if not auth_header.startswith('Bearer '):
                return None
                
            # Extract the token
            token = auth_header.split(' ')[1]
            
            # Get user from token
            user = get_user_from_token(token)
            
            return (user, token)
            
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'Bearer'

class PatientAuthentication(JWTAuthentication):
    """
    JWT authentication specifically for patients
    """
    
    def authenticate(self, request):
        result = super().authenticate(request)
        
        if result is None:
            return None
            
        user, token = result
        
        # Check if user is a patient
        if not hasattr(user, 'email') or not hasattr(user, 'first_name'):
            raise AuthenticationFailed('Invalid user type')
            
        # Additional patient-specific checks can be added here
        from .patient_models import Patient
        if not isinstance(user, Patient):
            raise AuthenticationFailed('Patient authentication required')
            
        return (user, token)

class ProviderAuthentication(JWTAuthentication):
    """
    JWT authentication specifically for providers
    """
    
    def authenticate(self, request):
        result = super().authenticate(request)
        
        if result is None:
            return None
            
        user, token = result
        
        # Check if user is a provider
        if not hasattr(user, 'specialization'):
            raise AuthenticationFailed('Invalid user type')
            
        # Additional provider-specific checks can be added here
        from .models import Provider
        if not isinstance(user, Provider):
            raise AuthenticationFailed('Provider authentication required')
            
        return (user, token)
