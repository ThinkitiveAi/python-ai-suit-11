import re
import bcrypt
from django.utils import timezone
from rest_framework import serializers
from .models import Provider

PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\d]).{8,}$'

class ClinicAddressSerializer(serializers.Serializer):
    street = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=50)
    zip = serializers.CharField(max_length=20)

class ProviderRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    clinic_address = ClinicAddressSerializer()

    class Meta:
        model = Provider
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'password', 'confirm_password', 'specialization', 'license_number',
            'years_of_experience', 'clinic_address',
            'license_document_url'
        ]

    def validate_email(self, value):
        value = value.strip().lower()
        if Provider.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_phone_number(self, value):
        value = value.strip()
        if Provider.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered.")
        return value

    def validate_license_number(self, value):
        value = value.strip().upper()
        if Provider.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("License number already registered.")
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError("License must be alphanumeric.")
        return value

    def validate_password(self, value):
        if not re.match(PASSWORD_REGEX, value):
            raise serializers.ValidationError(
                "Password must have 8+ chars, uppercase, lowercase, number, special char."
            )
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password', None)
        address = validated_data.pop('clinic_address')
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        provider = Provider.objects.create(
            **validated_data,
            password_hash=password_hash,
            clinic_address=address,
            verification_status='verified',  # Auto-verify for demo
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        return provider


class ProviderLoginSerializer(serializers.Serializer):
    """Serializer for provider login"""
    email = serializers.EmailField(
        help_text="Provider's email address",
        required=True
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Provider's password",
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        fields = ['email', 'password']


class ProviderRegistrationResponseSerializer(serializers.Serializer):
    """Response serializer for provider registration"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(child=serializers.CharField())


class ProviderLoginResponseSerializer(serializers.Serializer):
    """Response serializer for provider login"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(child=serializers.CharField())


class ErrorResponseSerializer(serializers.Serializer):
    """Error response serializer"""
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()
    errors = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))
