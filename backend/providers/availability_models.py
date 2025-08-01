import uuid
from django.db import models
from django.utils import timezone
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
    timezone = models.CharField(max_length=64)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=16, choices=RECURRENCE_CHOICES, blank=True, null=True)
    recurrence_end_date = models.DateField(blank=True, null=True)
    slot_duration = models.PositiveIntegerField(default=30)
    break_duration = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='available')
    max_appointments_per_slot = models.PositiveIntegerField(default=1)
    current_appointments = models.PositiveIntegerField(default=0)
    appointment_type = models.CharField(max_length=16, choices=APPOINTMENT_TYPE_CHOICES, default='consultation')
    location = models.JSONField()
    pricing = models.JSONField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, max_length=500)
    special_requirements = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class AppointmentSlot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('blocked', 'Blocked'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='slots')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='slots')
    slot_start_time = models.DateTimeField()
    slot_end_time = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='available')
    patient_id = models.UUIDField(blank=True, null=True)
    appointment_type = models.CharField(max_length=16)
    booking_reference = models.CharField(max_length=64, unique=True)

class AvailabilityTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='availability_templates')
    template_name = models.CharField(max_length=100)
    schedule = models.JSONField()
    default_settings = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
