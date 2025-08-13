"""
Serializers for appointment booking and management
"""
from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, date
from .appointment_models import Appointment, AppointmentHistory
from .availability_models import AppointmentSlot,Availability
from .patient_models import Patient
from .models import Provider


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new appointments"""
    
    # Custom fields for frontend form
    patient_id = serializers.UUIDField(write_only=True)
    provider_id = serializers.UUIDField(write_only=True)
    appointment_slot_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    # Display fields
    patient_name = serializers.CharField(read_only=True, source='patient_full_name')
    provider_name = serializers.CharField(read_only=True, source='provider_full_name')
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'appointment_number',
            'patient_id',
            'provider_id',
            'appointment_slot_id',
            'patient_name',
            'provider_name',
            'appointment_mode',
            'appointment_type',
            'appointment_date',
            'appointment_time',
            'duration_minutes',
            'timezone',
            'estimated_amount',
            'currency',
            'reason_for_visit',
            'symptoms',
            'special_instructions',
            'emergency_contact_name',
            'emergency_contact_phone',
            'location_details',
            'video_call_link',
            'status',
            'payment_status',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'appointment_number',
            'patient_name',
            'provider_name',
            'status',
            'payment_status',
            'created_at',
        ]
    
    def validate_patient_id(self, value):
        """Validate patient exists and is active"""
        try:
            patient = Patient.objects.get(id=value, is_active=True)
            return value
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient not found or inactive")
    
    def validate_provider_id(self, value):
        """Validate provider exists and is active"""
        try:
            provider = Provider.objects.get(id=value, is_active=True)
            return value
        except Provider.DoesNotExist:
            raise serializers.ValidationError("Provider not found or inactive")
    
    def validate_appointment_slot_id(self, value):
        """Validate appointment slot if provided"""
        if value:
            try:
                slot = AppointmentSlot.objects.get(id=value)
                if slot.status != 'available':
                    raise serializers.ValidationError("Selected appointment slot is not available")
                return value
            except AppointmentSlot.DoesNotExist:
                raise serializers.ValidationError("Appointment slot not found")
        return value
    
    def validate_appointment_date(self, value):
        """Validate appointment date is not in the past"""
        if value < date.today():
            raise serializers.ValidationError("Appointment date cannot be in the past")
        return value
    
    def validate_estimated_amount(self, value):
        """Validate estimated amount is positive"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Estimated amount must be positive")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Validate appointment slot matches provider if provided
        if data.get('appointment_slot_id'):
            try:
                slot = AppointmentSlot.objects.get(id=data['appointment_slot_id'])
                if str(slot.provider.id) != str(data['provider_id']):
                    raise serializers.ValidationError({
                        'appointment_slot_id': 'Appointment slot provider must match selected provider'
                    })
                
                # Auto-fill appointment details from slot
                data['appointment_date'] = slot.slot_start_time.date()
                data['appointment_time'] = slot.slot_start_time.time()
                data['duration_minutes'] = int((slot.slot_end_time - slot.slot_start_time).total_seconds() / 60)
                
            except AppointmentSlot.DoesNotExist:
                raise serializers.ValidationError({
                    'appointment_slot_id': 'Appointment slot not found'
                })
        
        # Validate video call requirements
        if data.get('appointment_mode') == 'video_call' and not data.get('video_call_link'):
            raise serializers.ValidationError({
                'video_call_link': 'Video call link is required for video call appointments'
            })
        
        # Validate location requirements for in-person appointments
        if data.get('appointment_mode') == 'in_person' and not data.get('location_details'):
            raise serializers.ValidationError({
                'location_details': 'Location details are required for in-person appointments'
            })
        
        return data
    
    def create(self, validated_data):
        """Create new appointment"""
        # Extract foreign key IDs
        patient_id = validated_data.pop('patient_id')
        provider_id = validated_data.pop('provider_id')
        appointment_slot_id = validated_data.pop('appointment_slot_id', None)
        
        # Get related objects
        patient = Patient.objects.get(id=patient_id)
        provider = Provider.objects.get(id=provider_id)
        appointment_slot = None
        
        if appointment_slot_id:
            appointment_slot = AppointmentSlot.objects.get(id=appointment_slot_id)
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient,
            provider=provider,
            appointment_slot=appointment_slot,
            **validated_data
        )
        
        # Create history entry
        AppointmentHistory.objects.create(
            appointment=appointment,
            action='created',
            description=f'Appointment created for {patient.first_name} {patient.last_name}',
            performed_by=self.context.get('created_by', 'system'),
            new_values={
                'appointment_mode': appointment.appointment_mode,
                'appointment_type': appointment.appointment_type,
                'appointment_date': str(appointment.appointment_date),
                'appointment_time': str(appointment.appointment_time),
                'reason_for_visit': appointment.reason_for_visit,
            }
        )
        
        return appointment


class AppointmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing appointments"""
    
    patient_name = serializers.CharField(source='patient_full_name', read_only=True)
    provider_name = serializers.CharField(source='provider_full_name', read_only=True)
    patient_email = serializers.EmailField(source='patient.email', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone_number', read_only=True)
    provider_specialization = serializers.CharField(source='provider.specialization', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'appointment_number',
            'patient_name',
            'provider_name',
            'patient_email',
            'patient_phone',
            'provider_specialization',
            'appointment_mode',
            'appointment_type',
            'appointment_date',
            'appointment_time',
            'duration_minutes',
            'status',
            'payment_status',
            'estimated_amount',
            'currency',
            'reason_for_visit',
            'created_at',
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed appointment view"""
    
    patient_details = serializers.SerializerMethodField()
    provider_details = serializers.SerializerMethodField()
    appointment_slot_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = '__all__'
    
    def get_patient_details(self, obj):
        """Get patient details"""
        return {
            'id': obj.patient.id,
            'name': f"{obj.patient.first_name} {obj.patient.last_name}",
            'email': obj.patient.email,
            'phone': getattr(obj.patient, 'phone_number', ''),
            'age': getattr(obj.patient, 'age', None),
            'gender': getattr(obj.patient, 'gender', ''),
        }
    
    def get_provider_details(self, obj):
        """Get provider details"""
        return {
            'id': obj.provider.id,
            'name': f"{obj.provider.first_name} {obj.provider.last_name}",
            'email': obj.provider.email,
            'specialization': obj.provider.specialization,
            'phone': getattr(obj.provider, 'phone_number', ''),
        }
    
    def get_appointment_slot_details(self, obj):
        """Get appointment slot details if linked"""
        if obj.appointment_slot:
            return {
                'id': obj.appointment_slot.id,
                'slot_start_time': obj.appointment_slot.slot_start_time,
                'slot_end_time': obj.appointment_slot.slot_end_time,
                'status': obj.appointment_slot.status,
            }
        return None


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointments"""
    
    class Meta:
        model = Appointment
        fields = [
            'appointment_mode',
            'appointment_type',
            'appointment_date',
            'appointment_time',
            'duration_minutes',
            'estimated_amount',
            'reason_for_visit',
            'symptoms',
            'special_instructions',
            'emergency_contact_name',
            'emergency_contact_phone',
            'location_details',
            'video_call_link',
            'status',
        ]
    
    def validate_appointment_date(self, value):
        """Validate appointment date is not in the past"""
        if value < date.today():
            raise serializers.ValidationError("Appointment date cannot be in the past")
        return value
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            current_status = self.instance.status
            
            # Define allowed status transitions
            allowed_transitions = {
                'scheduled': ['confirmed', 'cancelled', 'rescheduled'],
                'confirmed': ['in_progress', 'cancelled', 'no_show', 'rescheduled'],
                'in_progress': ['completed', 'cancelled'],
                'completed': [],  # Cannot change from completed
                'cancelled': ['scheduled'],  # Can reschedule cancelled appointments
                'no_show': ['scheduled'],  # Can reschedule no-show appointments
                'rescheduled': ['scheduled', 'confirmed'],
            }
            
            if value != current_status and value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from '{current_status}' to '{value}'"
                )
        
        return value
    
    def update(self, instance, validated_data):
        """Update appointment with history tracking"""
        # Store previous values for history
        previous_values = {
            'status': instance.status,
            'appointment_date': str(instance.appointment_date),
            'appointment_time': str(instance.appointment_time),
            'reason_for_visit': instance.reason_for_visit,
        }
        
        # Update instance
        updated_instance = super().update(instance, validated_data)
        
        # Create history entry
        AppointmentHistory.objects.create(
            appointment=updated_instance,
            action='updated',
            description=f'Appointment updated',
            performed_by=self.context.get('updated_by', 'system'),
            previous_values=previous_values,
            new_values={
                'status': updated_instance.status,
                'appointment_date': str(updated_instance.appointment_date),
                'appointment_time': str(updated_instance.appointment_time),
                'reason_for_visit': updated_instance.reason_for_visit,
            }
        )
        
        return updated_instance


class AppointmentHistorySerializer(serializers.ModelSerializer):
    """Serializer for appointment history"""
    
    class Meta:
        model = AppointmentHistory
        fields = [
            'id',
            'action',
            'description',
            'performed_by',
            'performed_at',
            'previous_values',
            'new_values',
        ]


# Response Serializers for API documentation
class AppointmentCreateResponseSerializer(serializers.Serializer):
    """Response serializer for appointment creation"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = AppointmentDetailSerializer()


class AppointmentListResponseSerializer(serializers.Serializer):
    """Response serializer for appointment listing"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    count = serializers.IntegerField()
    data = AppointmentListSerializer(many=True)


class AppointmentErrorResponseSerializer(serializers.Serializer):
    """Response serializer for appointment errors"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    errors = serializers.DictField()
