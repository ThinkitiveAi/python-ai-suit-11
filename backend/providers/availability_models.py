import uuid
from django.db import models
from django.utils import timezone as django_timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import pytz
from .models import Provider

class Availability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('blocked', 'Blocked'),
        ('maintenance', 'Maintenance'),
    ]
    RECURRENCE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow Up'),
        ('emergency', 'Emergency'),
        ('telemedicine', 'Telemedicine'),
    ]
    LOCATION_TYPE_CHOICES = [
        ('clinic', 'Clinic'),
        ('hospital', 'Hospital'),
        ('telemedicine', 'Telemedicine'),
        ('home_visit', 'Home Visit'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    timezone = models.CharField(max_length=64, default='UTC')
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=16, choices=RECURRENCE_CHOICES, blank=True, null=True)
    recurrence_end_date = models.DateField(blank=True, null=True)
    slot_duration = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(480)]  # 15 min to 8 hours
    )
    break_duration = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(60)]  # 0 to 60 minutes
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='available')
    max_appointments_per_slot = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    current_appointments = models.PositiveIntegerField(default=0)
    appointment_type = models.CharField(max_length=16, choices=APPOINTMENT_TYPE_CHOICES, default='consultation')
    location = models.JSONField()
    pricing = models.JSONField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, max_length=500)
    special_requirements = models.JSONField(blank=True, null=True, default=list)
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['provider', 'date']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['provider', 'status']),
        ]

    def clean(self):
        """Validate the availability data"""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError('End time must be after start time')
        
        if self.is_recurring and not self.recurrence_pattern:
            raise ValidationError('Recurrence pattern is required for recurring availability')
        
        if self.is_recurring and self.recurrence_end_date and self.recurrence_end_date <= self.date:
            raise ValidationError('Recurrence end date must be after the start date')
        
        if self.current_appointments > self.max_appointments_per_slot:
            raise ValidationError('Current appointments cannot exceed maximum appointments per slot')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider.first_name} {self.provider.last_name} - {self.date} {self.start_time}-{self.end_time}"

    def get_local_datetime(self, time_field):
        """Convert time to provider's timezone"""
        provider_tz = pytz.timezone(self.timezone)
        dt = datetime.combine(self.date, time_field)
        return provider_tz.localize(dt)

    def get_utc_datetime(self, time_field):
        """Convert time to UTC"""
        local_dt = self.get_local_datetime(time_field)
        return local_dt.astimezone(pytz.UTC)

    @property
    def duration_minutes(self):
        """Calculate total duration in minutes"""
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)

    @property
    def total_slots(self):
        """Calculate total number of slots available"""
        if self.slot_duration <= 0:
            return 0
        return self.duration_minutes // (self.slot_duration + self.break_duration)

class AppointmentSlot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('blocked', 'Blocked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='slots')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='appointment_slots')
    slot_start_time = models.DateTimeField()  # Stored in UTC
    slot_end_time = models.DateTimeField()    # Stored in UTC
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='available')
    patient_id = models.UUIDField(blank=True, null=True)
    appointment_type = models.CharField(max_length=16)
    booking_reference = models.CharField(max_length=64, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['slot_start_time']
        indexes = [
            models.Index(fields=['provider', 'slot_start_time']),
            models.Index(fields=['status', 'slot_start_time']),
            models.Index(fields=['booking_reference']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'slot_start_time'],
                name='unique_provider_slot_time'
            )
        ]

    def clean(self):
        """Validate slot data"""
        if self.slot_start_time and self.slot_end_time:
            if self.slot_start_time >= self.slot_end_time:
                raise ValidationError('Slot end time must be after start time')

    def save(self, *args, **kwargs):
        if not self.booking_reference and self.status == 'booked':
            self.booking_reference = f"BOOK-{uuid.uuid4().hex[:8].upper()}"
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Slot {self.id} - {self.provider.first_name} {self.provider.last_name} ({self.status})"

    def get_local_start_time(self, timezone_str=None):
        """Get slot start time in specified timezone or provider's timezone"""
        tz = pytz.timezone(timezone_str or self.availability.timezone)
        return self.slot_start_time.astimezone(tz)

    def get_local_end_time(self, timezone_str=None):
        """Get slot end time in specified timezone or provider's timezone"""
        tz = pytz.timezone(timezone_str or self.availability.timezone)
        return self.slot_end_time.astimezone(tz)

class AvailabilityTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='availability_templates')
    template_name = models.CharField(max_length=100)
    schedule = models.JSONField()
    default_settings = models.JSONField()
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
