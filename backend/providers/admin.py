from django.contrib import admin
from .models import Provider, RefreshToken
from .patient_models import Patient, VerificationToken
from .patient_session_models import PatientSession
from .appointment_models import Appointment, AppointmentHistory
from .availability_models import Availability, AppointmentSlot


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'specialization', 'verification_status', 'is_active', 'created_at')
    list_filter = ('verification_status', 'is_active', 'specialization', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'license_number')
    readonly_fields = ('id', 'created_at', 'updated_at', 'password_hash')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Professional Information', {
            'fields': ('specialization', 'license_number', 'years_of_experience', 'clinic_address')
        }),
        ('Verification', {
            'fields': ('verification_status', 'license_document_url')
        }),
        ('Account Status', {
            'fields': ('is_active', 'last_login', 'login_count', 'failed_login_attempts', 'locked_until')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('provider', 'expires_at', 'is_revoked', 'created_at', 'last_used_at')
    list_filter = ('is_revoked', 'created_at', 'expires_at')
    search_fields = ('provider__email', 'provider__first_name', 'provider__last_name')
    readonly_fields = ('id', 'token_hash', 'created_at')
    ordering = ('-created_at',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name', 'email', 'date_of_birth', 'legal_sex', 'gender_identity', 'email_verified', 'phone_verified', 'is_active')
    list_filter = ('legal_sex', 'gender_identity', 'ethnicity', 'race', 'preferred_language', 'email_verified', 'phone_verified', 'is_active', 'created_at')
    search_fields = ('first_name', 'middle_name', 'last_name', 'preferred_name', 'email', 'phone_number')
    readonly_fields = ('id', 'created_at', 'updated_at', 'password_hash')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'preferred_name', 'email', 'phone_number', 'date_of_birth')
        }),
        ('Demographics', {
            'fields': ('legal_sex', 'gender_identity', 'ethnicity', 'race', 'preferred_language')
        }),
        ('Address Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'zipcode')
        }),
        ('Additional Information', {
            'fields': ('emergency_contact', 'insurance_info', 'medical_history')
        }),
        ('Verification Status', {
            'fields': ('email_verified', 'phone_verified')
        }),
        ('Account Status', {
            'fields': ('is_active', 'last_login', 'login_count', 'failed_login_attempts', 'locked_until')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('patient', 'expires_at', 'used', 'created_at')
    list_filter = ('used', 'created_at', 'expires_at')
    search_fields = ('patient__email', 'patient__first_name', 'patient__last_name')
    readonly_fields = ('id', 'token', 'created_at')
    ordering = ('-created_at',)


@admin.register(PatientSession)
class PatientSessionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'ip_address', 'expires_at', 'is_revoked', 'created_at')
    list_filter = ('is_revoked', 'created_at', 'expires_at')
    search_fields = ('patient__email', 'patient__first_name', 'patient__last_name', 'ip_address')
    readonly_fields = ('id', 'refresh_token_hash', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Session Information', {
            'fields': ('patient', 'expires_at', 'is_revoked')
        }),
        ('Device & Location', {
            'fields': ('ip_address', 'user_agent', 'device_info', 'location_info')
        }),
        ('System Information', {
            'fields': ('id', 'refresh_token_hash', 'created_at', 'last_used_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_number', 'patient', 'provider', 'appointment_date', 'appointment_time', 'appointment_mode', 'status', 'payment_status', 'created_at')
    list_filter = ('appointment_mode', 'appointment_type', 'status', 'payment_status', 'appointment_date', 'created_at')
    search_fields = ('appointment_number', 'patient__first_name', 'patient__last_name', 'provider__first_name', 'provider__last_name', 'reason_for_visit')
    readonly_fields = ('id', 'appointment_number', 'created_at', 'updated_at')
    ordering = ('-appointment_date', '-appointment_time')
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('appointment_number', 'patient', 'provider', 'appointment_slot')
        }),
        ('Scheduling', {
            'fields': ('appointment_date', 'appointment_time', 'duration_minutes', 'timezone', 'appointment_mode', 'appointment_type')
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_status', 'estimated_amount', 'actual_amount', 'currency')
        }),
        ('Medical Information', {
            'fields': ('reason_for_visit', 'symptoms', 'medical_history_notes')
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'emergency_contact_name', 'emergency_contact_phone', 'location_details', 'video_call_link')
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancellation_reason', 'cancelled_by'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'action', 'performed_by', 'performed_at')
    list_filter = ('action', 'performed_at')
    search_fields = ('appointment__appointment_number', 'performed_by', 'description')
    readonly_fields = ('id', 'performed_at')
    ordering = ('-performed_at',)


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('provider', 'date', 'start_time', 'end_time', 'appointment_type', 'status', 'is_recurring')
    list_filter = ('status', 'appointment_type', 'is_recurring', 'recurrence_pattern', 'date', 'created_at')
    search_fields = ('provider__first_name', 'provider__last_name', 'notes')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-date', 'start_time')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('provider', 'date', 'start_time', 'end_time', 'timezone')
        }),
        ('Slot Configuration', {
            'fields': ('slot_duration', 'break_duration', 'max_appointments_per_slot', 'appointment_type')
        }),
        ('Recurrence', {
            'fields': ('is_recurring', 'recurrence_pattern', 'recurrence_end_date')
        }),
        ('Status & Settings', {
            'fields': ('status', 'location', 'pricing', 'special_requirements')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ('provider', 'slot_start_time', 'slot_end_time', 'appointment_type', 'status', 'patient_id')
    list_filter = ('status', 'appointment_type', 'slot_start_time', 'created_at')
    search_fields = ('provider__first_name', 'provider__last_name', 'booking_reference')
    readonly_fields = ('id', 'booking_reference', 'created_at', 'updated_at')
    ordering = ('-slot_start_time',)
