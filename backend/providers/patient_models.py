import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator, EmailValidator

# Comprehensive choices for patient information
GENDER_IDENTITY_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('non_binary', 'Non-binary'),
    ('transgender_male', 'Transgender Male'),
    ('transgender_female', 'Transgender Female'),
    ('genderfluid', 'Genderfluid'),
    ('other', 'Other'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

LEGAL_SEX_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('intersex', 'Intersex'),
    ('unknown', 'Unknown'),
]

ETHNICITY_CHOICES = [
    ('hispanic_latino', 'Hispanic or Latino'),
    ('not_hispanic_latino', 'Not Hispanic or Latino'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

RACE_CHOICES = [
    ('american_indian_alaska_native', 'American Indian or Alaska Native'),
    ('asian', 'Asian'),
    ('black_african_american', 'Black or African American'),
    ('native_hawaiian_pacific_islander', 'Native Hawaiian or Other Pacific Islander'),
    ('white', 'White'),
    ('other', 'Other'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

LANGUAGE_CHOICES = [
    ('english', 'English'),
    ('spanish', 'Spanish'),
    ('french', 'French'),
    ('german', 'German'),
    ('chinese', 'Chinese'),
    ('hindi', 'Hindi'),
    ('arabic', 'Arabic'),
    ('portuguese', 'Portuguese'),
    ('russian', 'Russian'),
    ('japanese', 'Japanese'),
    ('other', 'Other'),
]

STATE_CHOICES = [
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
    ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
    ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
    ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
    ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
    ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
    ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
    ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
    ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'), ('WY', 'Wyoming'),
]

class Patient(models.Model):
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Personal Information
    first_name = models.CharField(
        max_length=50, 
        validators=[MinLengthValidator(2)],
        help_text="Patient's first name"
    )
    middle_name = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Patient's middle name (optional)"
    )
    last_name = models.CharField(
        max_length=50, 
        validators=[MinLengthValidator(2)],
        help_text="Patient's last name"
    )
    preferred_name = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Patient's preferred name (optional)"
    )
    
    # Contact Information
    email = models.EmailField(
        unique=True, 
        validators=[EmailValidator()],
        help_text="Patient's email address"
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?[1-9]\d{1,14}$',
                message="Enter a valid international phone number."
            )
        ],
        help_text="Patient's phone number"
    )
    
    # Authentication
    password_hash = models.CharField(max_length=128)
    
    # Demographics
    date_of_birth = models.DateField(
        default='1990-01-01',
        help_text="Patient's date of birth"
    )
    legal_sex = models.CharField(
        max_length=20, 
        choices=LEGAL_SEX_CHOICES,
        default='unknown',
        help_text="Legal sex as per official documents"
    )
    gender_identity = models.CharField(
        max_length=30, 
        choices=GENDER_IDENTITY_CHOICES,
        default='prefer_not_to_say',
        help_text="Patient's gender identity"
    )
    ethnicity = models.CharField(
        max_length=30, 
        choices=ETHNICITY_CHOICES,
        blank=True, 
        null=True,
        help_text="Patient's ethnicity"
    )
    race = models.CharField(
        max_length=50, 
        choices=RACE_CHOICES,
        blank=True, 
        null=True,
        help_text="Patient's race"
    )
    preferred_language = models.CharField(
        max_length=20, 
        choices=LANGUAGE_CHOICES,
        default='english',
        help_text="Patient's preferred language"
    )
    
    # Address Information
    address_line_1 = models.CharField(
        max_length=200,
        default='',
        help_text="Primary address line"
    )
    address_line_2 = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Secondary address line (optional)"
    )
    city = models.CharField(
        max_length=100,
        default='',
        help_text="City"
    )
    state = models.CharField(
        max_length=2,
        choices=STATE_CHOICES,
        default='NY',
        help_text="State"
    )
    zipcode = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{5}(-\d{4})?$',
                message="Enter a valid ZIP code (e.g., 12345 or 12345-6789)"
            )
        ],
        default='00000',
        help_text="ZIP code"
    )
    
    # Additional Information (JSON fields for flexibility)
    emergency_contact = models.JSONField(
        blank=True, 
        null=True,
        help_text="Emergency contact information"
    )
    medical_history = models.JSONField(
        blank=True, 
        null=True,
        help_text="Patient's medical history"
    )
    insurance_info = models.JSONField(
        blank=True, 
        null=True,
        help_text="Insurance information"
    )
    
    # Verification Status
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Account Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Login/session tracking fields
    login_count = models.PositiveIntegerField(default=0)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    last_failed_attempt = models.DateTimeField(blank=True, null=True)
    suspicious_activity_score = models.PositiveIntegerField(default=0)
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        """Return the patient's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Return the patient's preferred name or full name"""
        return self.preferred_name if self.preferred_name else self.full_name
    
    @property
    def full_address(self):
        """Return the patient's full address"""
        address_parts = [self.address_line_1]
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        address_parts.extend([self.city, self.state, self.zipcode])
        return ", ".join(address_parts)

class VerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"VerificationToken for {self.patient.email} (used={self.used})"
