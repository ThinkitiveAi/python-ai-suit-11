import re
import bcrypt
from datetime import date
from rest_framework import serializers
from .patient_models import Patient
from django.utils import timezone

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,}$"
GENDER_CHOICES = ['male', 'female', 'other', 'prefer_not_to_say']

class AddressSerializer(serializers.Serializer):
    street = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=50)
    zip = serializers.CharField(max_length=20)

class EmergencyContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    relationship = serializers.CharField(max_length=50, required=False, allow_blank=True)

class InsuranceInfoSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=100, required=False, allow_blank=True)
    policy_number = serializers.CharField(max_length=100, required=False, allow_blank=True)

class PatientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    address = AddressSerializer()
    emergency_contact = EmergencyContactSerializer(required=False, allow_null=True)
    insurance_info = InsuranceInfoSerializer(required=False, allow_null=True)
    medical_history = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password', 'confirm_password', 'date_of_birth', 'gender', 'address', 'emergency_contact', 'medical_history', 'insurance_info']

    def validate_email(self, value):
        value = value.strip().lower()
        if Patient.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered")
        return value

    def validate_phone_number(self, value):
        value = value.strip()
        if not re.match(r'^\+?[1-9]\d{1,14}$', value):
            raise serializers.ValidationError("Enter a valid international phone number.")
        if Patient.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")
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

    def validate_gender(self, value):
        if value not in GENDER_CHOICES:
            raise serializers.ValidationError("Invalid gender value.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password', None)
        address = validated_data.pop('address')
        emergency_contact = validated_data.pop('emergency_contact', None)
        insurance_info = validated_data.pop('insurance_info', None)
        medical_history = validated_data.pop('medical_history', None)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        patient = Patient.objects.create(
            **validated_data,
            password_hash=password_hash,
            address=address,
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
