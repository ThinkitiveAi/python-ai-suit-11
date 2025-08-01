from django.contrib import admin
from .models import Provider, RefreshToken
from .patient_models import Patient, VerificationToken
from .patient_session_models import PatientSession


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
