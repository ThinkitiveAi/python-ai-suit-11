import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator, EmailValidator

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    last_name = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[1-9]\d{1,14}$',
                message="Enter a valid international phone number."
            )
        ]
    )
    password_hash = models.CharField(max_length=128)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    address = models.JSONField()
    emergency_contact = models.JSONField(blank=True, null=True)
    medical_history = models.JSONField(blank=True, null=True)
    insurance_info = models.JSONField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Login/session tracking fields
    login_count = models.PositiveIntegerField(default=0)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    last_failed_attempt = models.DateTimeField(blank=True, null=True)
    suspicious_activity_score = models.PositiveIntegerField(default=0)
    last_login = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class VerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"VerificationToken for {self.patient.email} (used={self.used})"
