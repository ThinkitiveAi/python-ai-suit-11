"""
Custom Permission Classes for Patient and Provider APIs
"""

from rest_framework.permissions import BasePermission
from .patient_models import Patient
from .models import Provider

class IsPatient(BasePermission):
    """
    Permission class to check if the authenticated user is a patient
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is authenticated and is a patient
        """
        if not request.user or not hasattr(request.user, 'id'):
            return False
            
        return isinstance(request.user, Patient) and request.user.is_active

class IsProvider(BasePermission):
    """
    Permission class to check if the authenticated user is a provider
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is authenticated and is a provider
        """
        if not request.user or not hasattr(request.user, 'id'):
            return False
            
        return isinstance(request.user, Provider) and request.user.is_active

class IsVerifiedProvider(BasePermission):
    """
    Permission class to check if the authenticated user is a verified provider
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is authenticated, is a provider, and is verified
        """
        if not request.user or not hasattr(request.user, 'id'):
            return False
            
        return (isinstance(request.user, Provider) and 
                request.user.is_active and 
                request.user.verification_status == 'verified')

class IsPatientOwner(BasePermission):
    """
    Permission class to check if the patient can only access their own data
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the patient is accessing their own data
        """
        if not isinstance(request.user, Patient):
            return False
            
        # If the object is a Patient instance, check if it's the same user
        if isinstance(obj, Patient):
            return obj.id == request.user.id
            
        # If the object has a patient field, check if it belongs to the user
        if hasattr(obj, 'patient'):
            return obj.patient.id == request.user.id
            
        return False

class IsProviderOwner(BasePermission):
    """
    Permission class to check if the provider can only access their own data
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the provider is accessing their own data
        """
        if not isinstance(request.user, Provider):
            return False
            
        # If the object is a Provider instance, check if it's the same user
        if isinstance(obj, Provider):
            return obj.id == request.user.id
            
        # If the object has a provider field, check if it belongs to the user
        if hasattr(obj, 'provider'):
            return obj.provider.id == request.user.id
            
        return False
