"""
Appointment models for booking management
"""
import uuid
from django.db import models
from django.utils import timezone as django_timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Provider
from .patient_models import Patient
from .availability_models import AppointmentSlot


class Appointment(models.Model):
    """Model for actual appointment bookings"""
    
    APPOINTMENT_MODE_CHOICES = [
        ('in_person', 'In-Person'),
        ('video_call', 'Video Call'),
        ('home_visit', 'Home Visit'),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow Up'),
        ('emergency', 'Emergency'),
        ('telemedicine', 'Telemedicine'),
        ('routine_checkup', 'Routine Checkup'),
        ('specialist_consultation', 'Specialist Consultation'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Relationships
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='appointments'
    )
    provider = models.ForeignKey(
        Provider, 
        on_delete=models.CASCADE, 
        related_name='appointments'
    )
    appointment_slot = models.OneToOneField(
        AppointmentSlot,
        on_delete=models.CASCADE,
        related_name='appointment',
        null=True,
        blank=True
    )
    
    # Appointment Details
    appointment_mode = models.CharField(
        max_length=20, 
        choices=APPOINTMENT_MODE_CHOICES,
        default='in_person'
    )
    appointment_type = models.CharField(
        max_length=30, 
        choices=APPOINTMENT_TYPE_CHOICES,
        default='consultation'
    )
    
    # Scheduling Information
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(480)]
    )
    timezone = models.CharField(max_length=64, default='UTC')
    
    # Status and Payment
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Financial Information
    estimated_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True
    )
    actual_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Medical Information
    reason_for_visit = models.TextField(
        max_length=1000,
        help_text="Patient's reason for the appointment"
    )
    symptoms = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="Patient's symptoms (optional)"
    )
    medical_history_notes = models.TextField(
        max_length=2000,
        blank=True,
        null=True,
        help_text="Relevant medical history"
    )
    
    # Additional Information
    special_instructions = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Special instructions for the appointment"
    )
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    # Location Information (for in-person appointments)
    location_details = models.JSONField(
        blank=True,
        null=True,
        help_text="Location details for the appointment"
    )
    
    # Video Call Information (for telemedicine)
    video_call_link = models.URLField(
        blank=True,
        null=True,
        help_text="Video call link for telemedicine appointments"
    )
    video_call_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    # Reminders and Notifications
    reminder_sent = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(
        max_length=50,
        default='patient',
        help_text="Who created the appointment (patient, provider, admin)"
    )
    
    # Cancellation Information
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(
        max_length=500,
        blank=True,
        null=True
    )
    cancelled_by = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Who cancelled the appointment"
    )
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['patient', 'appointment_date']),
            models.Index(fields=['provider', 'appointment_date']),
            models.Index(fields=['status', 'appointment_date']),
            models.Index(fields=['appointment_number']),
            models.Index(fields=['payment_status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'appointment_date', 'appointment_time'],
                name='unique_provider_appointment_time',
                condition=models.Q(status__in=['scheduled', 'confirmed', 'in_progress'])
            )
        ]
    
    def clean(self):
        """Validate appointment data"""
        # Validate appointment slot if provided
        if self.appointment_slot:
            if self.appointment_slot.provider != self.provider:
                raise ValidationError("Appointment slot provider must match appointment provider")
            
            if self.appointment_slot.status != 'available':
                raise ValidationError("Cannot book an unavailable appointment slot")
        
        # Validate video call requirements
        if self.appointment_mode == 'video_call' and not self.video_call_link:
            raise ValidationError("Video call link is required for video call appointments")
        
        # Validate location for in-person appointments
        if self.appointment_mode == 'in_person' and not self.location_details:
            raise ValidationError("Location details are required for in-person appointments")
    
    def save(self, *args, **kwargs):
        # Generate appointment number if not provided
        if not self.appointment_number:
            self.appointment_number = self.generate_appointment_number()
        
        # Validate before making any changes
        self.full_clean()
        
        # Update appointment slot status if linked
        if self.appointment_slot and self.status in ['scheduled', 'confirmed']:
            self.appointment_slot.status = 'booked'
            self.appointment_slot.patient_id = self.patient.id
            self.appointment_slot.save()
        
        super().save(*args, **kwargs)
    
    def generate_appointment_number(self):
        """Generate unique appointment number"""
        import random
        import string
        
        while True:
            # Format: APT-YYYYMMDD-XXXX (e.g., APT-20250807-A1B2)
            date_str = django_timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            appointment_number = f"APT-{date_str}-{random_str}"
            
            if not Appointment.objects.filter(appointment_number=appointment_number).exists():
                return appointment_number
    
    def __str__(self):
        return f"Appointment {self.appointment_number} - {self.patient.first_name} {self.patient.last_name} with {self.provider.first_name} {self.provider.last_name}"
    
    @property
    def patient_full_name(self):
        """Get patient's full name"""
        return f"{self.patient.first_name} {self.patient.last_name}"
    
    @property
    def provider_full_name(self):
        """Get provider's full name"""
        return f"{self.provider.first_name} {self.provider.last_name}"
    
    @property
    def is_upcoming(self):
        """Check if appointment is upcoming"""
        from datetime import datetime, date
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime > django_timezone.now() and self.status in ['scheduled', 'confirmed']
    
    @property
    def can_be_cancelled(self):
        """Check if appointment can be cancelled"""
        return self.status in ['scheduled', 'confirmed'] and self.is_upcoming
    
    @property
    def can_be_rescheduled(self):
        """Check if appointment can be rescheduled"""
        return self.status in ['scheduled', 'confirmed'] and self.is_upcoming


class AppointmentHistory(models.Model):
    """Model to track appointment changes and history"""
    
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(max_length=500)
    performed_by = models.CharField(max_length=100)  # User who performed the action
    performed_at = models.DateTimeField(default=django_timezone.now)
    
    # Store previous values for tracking changes
    previous_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['appointment', 'performed_at']),
            models.Index(fields=['action', 'performed_at']),
        ]
    
    def __str__(self):
        return f"{self.appointment.appointment_number} - {self.action} at {self.performed_at}"
