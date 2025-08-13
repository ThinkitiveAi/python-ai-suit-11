from rest_framework import serializers
from .models import Provider
from .patient_models import Patient


class ProviderDropdownSerializer(serializers.ModelSerializer):
    """
    Serializer for Provider dropdown data.
    Returns minimal information needed for dropdown display.
    """
    full_name = serializers.SerializerMethodField()
    display_text = serializers.SerializerMethodField()
    
    class Meta:
        model = Provider
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'full_name',
            'email', 
            'specialization',
            'verification_status',
            'display_text'
        ]
    
    def get_full_name(self, obj):
        """Return the provider's full name"""
        return f"{obj.first_name} {obj.last_name}"
    
    def get_display_text(self, obj):
        """Return formatted text for dropdown display"""
        return f"Dr. {obj.first_name} {obj.last_name} - {obj.specialization}"


class PatientDropdownSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient dropdown data.
    Returns minimal information needed for dropdown display.
    """
    full_name = serializers.SerializerMethodField()
    display_text = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'full_name',
            'email', 
            'phone_number',
            'date_of_birth',
            'age',
            'display_text'
        ]
    
    def get_full_name(self, obj):
        """Return the patient's full name"""
        if obj.middle_name:
            return f"{obj.first_name} {obj.middle_name} {obj.last_name}"
        return f"{obj.first_name} {obj.last_name}"
    
    def get_age(self, obj):
        """Calculate and return patient's age"""
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
    
    def get_display_text(self, obj):
        """Return formatted text for dropdown display"""
        age = self.get_age(obj)
        return f"{self.get_full_name(obj)} - {age} years old ({obj.email})"


class ProviderListResponseSerializer(serializers.Serializer):
    """Response serializer for provider list API"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = ProviderDropdownSerializer(many=True)
    count = serializers.IntegerField()


class PatientListResponseSerializer(serializers.Serializer):
    """Response serializer for patient list API"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = PatientDropdownSerializer(many=True)
    count = serializers.IntegerField()
