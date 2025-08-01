import re
import bcrypt
from datetime import date
from rest_framework import serializers
from .patient_models import (
    Patient, 
    GENDER_IDENTITY_CHOICES, 
    LEGAL_SEX_CHOICES, 
    ETHNICITY_CHOICES, 
    RACE_CHOICES, 
    LANGUAGE_CHOICES, 
    STATE_CHOICES
)
from django.utils import timezone

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,}$"

class EmergencyContactSerializer(serializers.Serializer):
    """Serializer for emergency contact information"""
    name = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Emergency contact's full name"
    )
    phone = serializers.CharField(
        max_length=20, 
        required=False, 
        allow_blank=True,
        help_text="Emergency contact's phone number"
    )
    relationship = serializers.CharField(
        max_length=50, 
        required=False, 
        allow_blank=True,
        help_text="Relationship to patient"
    )
    email = serializers.EmailField(
        required=False, 
        allow_blank=True,
        help_text="Emergency contact's email address"
    )

class InsuranceInfoSerializer(serializers.Serializer):
    """Serializer for insurance information"""
    provider = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Insurance provider name"
    )
    policy_number = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Insurance policy number"
    )
    group_number = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Insurance group number"
    )
    member_id = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Insurance member ID"
    )

class PatientRegistrationSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for patient registration"""
    
    # Authentication fields
    password = serializers.CharField(
        write_only=True,
        help_text="Patient's password (8+ chars, uppercase, lowercase, number, special char)",
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        help_text="Confirm password",
        style={'input_type': 'password'}
    )
    
    # Nested serializers for complex data
    emergency_contact = EmergencyContactSerializer(
        required=False, 
        allow_null=True,
        help_text="Emergency contact information"
    )
    insurance_info = InsuranceInfoSerializer(
        required=False, 
        allow_null=True,
        help_text="Insurance information"
    )
    medical_history = serializers.ListField(
        child=serializers.CharField(), 
        required=False, 
        allow_null=True,
        help_text="List of medical conditions/history"
    )
    
    # Choice field validations
    legal_sex = serializers.ChoiceField(
        choices=LEGAL_SEX_CHOICES,
        help_text="Legal sex as per official documents"
    )
    gender_identity = serializers.ChoiceField(
        choices=GENDER_IDENTITY_CHOICES,
        help_text="Patient's gender identity"
    )
    ethnicity = serializers.ChoiceField(
        choices=ETHNICITY_CHOICES,
        required=False,
        allow_null=True,
        help_text="Patient's ethnicity"
    )
    race = serializers.ChoiceField(
        choices=RACE_CHOICES,
        required=False,
        allow_null=True,
        help_text="Patient's race"
    )
    preferred_language = serializers.ChoiceField(
        choices=LANGUAGE_CHOICES,
        default='english',
        help_text="Patient's preferred language"
    )
    state = serializers.ChoiceField(
        choices=STATE_CHOICES,
        help_text="State"
    )

    class Meta:
        model = Patient
        fields = [
            # Personal Information
            'first_name', 'middle_name', 'last_name', 'preferred_name',
            # Contact Information
            'email', 'phone_number',
            # Authentication
            'password', 'confirm_password',
            # Demographics
            'date_of_birth', 'legal_sex', 'gender_identity', 'ethnicity', 'race', 'preferred_language',
            # Address
            'address_line_1', 'address_line_2', 'city', 'state', 'zipcode',
            # Additional Information
            'emergency_contact', 'medical_history', 'insurance_info'
        ]
        extra_kwargs = {
            'first_name': {'help_text': "Patient's first name"},
            'middle_name': {'help_text': "Patient's middle name (optional)"},
            'last_name': {'help_text': "Patient's last name"},
            'preferred_name': {'help_text': "Patient's preferred name (optional)"},
            'email': {'help_text': "Patient's email address"},
            'phone_number': {'help_text': "Patient's phone number"},
            'date_of_birth': {'help_text': "Patient's date of birth (YYYY-MM-DD)"},
            'address_line_1': {'help_text': "Primary address line"},
            'address_line_2': {'help_text': "Secondary address line (optional)"},
            'city': {'help_text': "City"},
            'zipcode': {'help_text': "ZIP code (e.g., 12345 or 12345-6789)"},
        }

    def validate_email(self, value):
        value = value.strip().lower()
        if Patient.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered")
        return value

    def validate_phone_number(self, value):
        value = value.strip()
        if not re.match(r'^\+?[1-9]\d{1,14}$', value):
            raise serializers.ValidationError("Enter a valid international phone number.")
        # Note: Removed unique constraint for phone_number in model
        return value

    def validate_password(self, value):
        if not re.match(PASSWORD_REGEX, value):
            raise serializers.ValidationError(
                "Password must have 8+ chars, uppercase, lowercase, number, special char."
            )
        return value

    def validate_date_of_birth(self, value):
        today = date.today()
        if value >= today:
            raise serializers.ValidationError("Date of birth must be in the past.")
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 13:
            raise serializers.ValidationError("Must be at least 13 years old.")
        return value

    def validate_legal_sex(self, value):
        """Validate legal sex choice"""
        valid_choices = [choice[0] for choice in LEGAL_SEX_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Invalid legal sex. Must be one of: {valid_choices}")
        return value
    
    def validate_gender_identity(self, value):
        """Validate gender identity choice"""
        valid_choices = [choice[0] for choice in GENDER_IDENTITY_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Invalid gender identity. Must be one of: {valid_choices}")
        return value
    
    def validate_zipcode(self, value):
        """Validate ZIP code format"""
        if not re.match(r'^\d{5}(-\d{4})?$', value):
            raise serializers.ValidationError("Enter a valid ZIP code (e.g., 12345 or 12345-6789)")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """Create a new patient with comprehensive information"""
        password = validated_data.pop('password')
        validated_data.pop('confirm_password', None)
        
        # Extract nested data
        emergency_contact = validated_data.pop('emergency_contact', None)
        insurance_info = validated_data.pop('insurance_info', None)
        medical_history = validated_data.pop('medical_history', None)
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        # Create patient with all comprehensive fields
        patient = Patient.objects.create(
            **validated_data,
            password_hash=password_hash,
            emergency_contact=emergency_contact,
            insurance_info=insurance_info,
            medical_history=medical_history,
            email_verified=True,   # Auto-verify for demo
            phone_verified=True,   # Auto-verify for demo
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        return patient


class PatientLoginSerializer(serializers.Serializer):
    """Serializer for patient login"""
    email = serializers.EmailField(
        help_text="Patient's email address",
        required=True
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Patient's password",
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        fields = ['email', 'password']


class PatientRegistrationResponseSerializer(serializers.Serializer):
    """Response serializer for patient registration"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(child=serializers.CharField())


class PatientLoginResponseSerializer(serializers.Serializer):
    """Response serializer for patient login"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(child=serializers.CharField())


class PatientErrorResponseSerializer(serializers.Serializer):
    """Error response serializer for patient endpoints"""
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()
    errors = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))
