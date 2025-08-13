from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta, time
import pytz
from .availability_models import Availability, AppointmentSlot, AvailabilityTemplate
from .models import Provider
from .availability_utils import (
    AvailabilityManager, SlotGenerator, AvailabilityValidator
)


class LocationSerializer(serializers.Serializer):
    """Serializer for location data"""
    type = serializers.ChoiceField(choices=[
        ('clinic', 'Clinic'),
        ('hospital', 'Hospital'),
        ('telemedicine', 'Telemedicine'),
        ('home_visit', 'Home Visit')
    ])
    address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    room_number = serializers.CharField(max_length=50, required=False, allow_blank=True)


class PricingSerializer(serializers.Serializer):
    """Serializer for pricing data"""
    base_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    insurance_accepted = serializers.BooleanField(default=True)
    currency = serializers.CharField(max_length=3, default='USD')


class AvailabilityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating availability slots"""
    location = LocationSerializer()
    pricing = PricingSerializer(required=False)
    special_requirements = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )

    class Meta:
        model = Availability
        fields = [
            'date', 'start_time', 'end_time', 'timezone', 'slot_duration',
            'break_duration', 'is_recurring', 'recurrence_pattern',
            'recurrence_end_date', 'appointment_type', 'location', 'pricing',
            'special_requirements', 'notes', 'max_appointments_per_slot'
        ]

    def validate(self, data):
        """Validate the availability data using utility validators"""
        # Validate time range
        AvailabilityValidator.validate_time_range(data['start_time'], data['end_time'])
        
        # Validate timezone
        if not AvailabilityManager.validate_timezone(data['timezone']):
            raise serializers.ValidationError("Invalid timezone")
        
        # Validate slot duration
        AvailabilityValidator.validate_slot_duration(
            data['start_time'], data['end_time'],
            data['slot_duration'], data.get('break_duration', 0)
        )
        
        # Validate recurrence settings
        AvailabilityValidator.validate_recurrence(
            data.get('is_recurring', False),
            data.get('recurrence_pattern'),
            data['date'],
            data.get('recurrence_end_date')
        )
        
        # Validate pricing
        if 'pricing' in data:
            AvailabilityValidator.validate_pricing(data['pricing'])
        
        # Validate location
        AvailabilityValidator.validate_location(data['location'])
        
        return data

    def create(self, validated_data):
        """Create availability and generate slots using utility classes"""
        import json
        from decimal import Decimal
        
        # Extract provider from context (passed from view)
        provider = self.context.get('provider') or self.context['request'].user
        validated_data['provider'] = provider
        
        # Handle nested serializers - convert to JSON format for database storage
        location_data = validated_data.pop('location', None)
        pricing_data = validated_data.pop('pricing', None)
        
        # Convert location data to JSON if present
        if location_data:
            # Ensure location data is JSON serializable
            validated_data['location'] = dict(location_data)
        
        # Convert pricing data to JSON if present
        if pricing_data:
            # Convert Decimal to string for JSON serialization
            pricing_dict = dict(pricing_data)
            if 'base_fee' in pricing_dict and isinstance(pricing_dict['base_fee'], Decimal):
                pricing_dict['base_fee'] = str(pricing_dict['base_fee'])
            validated_data['pricing'] = pricing_dict
        
        # Create the availability instance
        availability = Availability.objects.create(**validated_data)
        
        # Generate appointment slots using SlotGenerator
        generator = SlotGenerator(availability)
        slots_created = generator.generate_slots()
        
        # Store slots count for response
        availability._slots_created = slots_created
        
        return availability


class AppointmentSlotSerializer(serializers.ModelSerializer):
    """Serializer for appointment slots"""
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    pricing = serializers.SerializerMethodField()
    
    class Meta:
        model = AppointmentSlot
        fields = [
            'id', 'start_time', 'end_time', 'status', 'appointment_type',
            'location', 'pricing', 'booking_reference'
        ]
    
    def get_start_time(self, obj):
        """Get start time in provider's timezone"""
        local_time = obj.get_local_start_time()
        return local_time.strftime('%H:%M')
    
    def get_end_time(self, obj):
        """Get end time in provider's timezone"""
        local_time = obj.get_local_end_time()
        return local_time.strftime('%H:%M')
    
    def get_location(self, obj):
        """Get location from availability"""
        return obj.availability.location
    
    def get_pricing(self, obj):
        """Get pricing from availability"""
        return obj.availability.pricing


class AvailabilityDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed availability view"""
    slots = AppointmentSlotSerializer(many=True, read_only=True)
    location = LocationSerializer(read_only=True)
    pricing = PricingSerializer(read_only=True)
    
    class Meta:
        model = Availability
        fields = [
            'id', 'date', 'start_time', 'end_time', 'timezone', 'slot_duration',
            'break_duration', 'is_recurring', 'recurrence_pattern',
            'recurrence_end_date', 'status', 'max_appointments_per_slot',
            'current_appointments', 'appointment_type', 'location', 'pricing',
            'notes', 'special_requirements', 'created_at', 'updated_at', 'slots'
        ]


class ProviderAvailabilitySerializer(serializers.Serializer):
    """Serializer for provider availability response"""
    date = serializers.DateField()
    slots = AppointmentSlotSerializer(many=True)


class AvailabilityUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating availability slots"""
    pricing = PricingSerializer(required=False)
    
    class Meta:
        model = AppointmentSlot
        fields = ['status', 'booking_reference']
        read_only_fields = ['id', 'availability', 'provider', 'slot_start_time', 'slot_end_time']

    def update(self, instance, validated_data):
        """Update slot with validation"""
        # Don't allow status change if slot is booked
        if instance.status == 'booked' and validated_data.get('status') != 'booked':
            if not self.context.get('force_update', False):
                raise serializers.ValidationError("Cannot change status of booked slot without force update")
        
        return super().update(instance, validated_data)


class ProviderSearchSerializer(serializers.Serializer):
    """Serializer for provider information in search results"""
    id = serializers.UUIDField()
    name = serializers.SerializerMethodField()
    specialization = serializers.CharField()
    years_of_experience = serializers.IntegerField()
    rating = serializers.SerializerMethodField()
    clinic_address = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return f"Dr. {obj.first_name} {obj.last_name}"
    
    def get_rating(self, obj):
        # TODO: Implement rating calculation based on reviews
        return 4.5  # Placeholder
    
    def get_clinic_address(self, obj):
        if obj.clinic_address and isinstance(obj.clinic_address, dict):
            return obj.clinic_address.get('address', '')
        return ''


class AvailabilitySearchSerializer(serializers.Serializer):
    """Serializer for availability search results"""
    provider = ProviderSearchSerializer()
    available_slots = AppointmentSlotSerializer(many=True)


class SlotSearchSerializer(serializers.Serializer):
    """Serializer for individual slot in search results"""
    slot_id = serializers.UUIDField(source='id')
    date = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    appointment_type = serializers.CharField()
    location = serializers.SerializerMethodField()
    pricing = serializers.SerializerMethodField()
    special_requirements = serializers.SerializerMethodField()
    
    def get_date(self, obj):
        local_start = obj.get_local_start_time()
        return local_start.strftime('%Y-%m-%d')
    
    def get_start_time(self, obj):
        local_start = obj.get_local_start_time()
        return local_start.strftime('%H:%M')
    
    def get_end_time(self, obj):
        local_end = obj.get_local_end_time()
        return local_end.strftime('%H:%M')
    
    def get_location(self, obj):
        return obj.availability.location
    
    def get_pricing(self, obj):
        return obj.availability.pricing
    
    def get_special_requirements(self, obj):
        return obj.availability.special_requirements or []


class AvailabilitySearchResponseSerializer(serializers.Serializer):
    """Serializer for search response"""
    provider = ProviderSearchSerializer()
    available_slots = SlotSearchSerializer(many=True)


class AllProviderAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for all provider availability data"""
    provider = ProviderSearchSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    pricing = PricingSerializer(read_only=True)
    slots_count = serializers.SerializerMethodField()
    available_slots_count = serializers.SerializerMethodField()
    booked_slots_count = serializers.SerializerMethodField()
    local_start_time = serializers.SerializerMethodField()
    local_end_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Availability
        fields = [
            'id', 'provider', 'date', 'start_time', 'end_time', 'local_start_time', 'local_end_time',
            'timezone', 'slot_duration', 'break_duration', 'is_recurring', 'recurrence_pattern',
            'recurrence_end_date', 'status', 'appointment_type', 'location', 'pricing',
            'max_appointments_per_slot', 'current_appointments', 'notes', 'special_requirements',
            'slots_count', 'available_slots_count', 'booked_slots_count', 'created_at', 'updated_at'
        ]
    
    def get_slots_count(self, obj):
        """Get total number of slots for this availability"""
        return obj.slots.count() if hasattr(obj, 'slots') else 0
    
    def get_available_slots_count(self, obj):
        """Get number of available slots"""
        return obj.slots.filter(status='available').count() if hasattr(obj, 'slots') else 0
    
    def get_booked_slots_count(self, obj):
        """Get number of booked slots"""
        return obj.slots.filter(status='booked').count() if hasattr(obj, 'slots') else 0
    
    def get_local_start_time(self, obj):
        """Get start time in provider's timezone"""
        if obj.timezone:
            try:
                provider_tz = pytz.timezone(obj.timezone)
                # Combine date and time, then localize
                naive_datetime = datetime.combine(obj.date, obj.start_time)
                utc_datetime = pytz.UTC.localize(naive_datetime)
                local_datetime = utc_datetime.astimezone(provider_tz)
                return local_datetime.strftime('%H:%M')
            except:
                pass
        return obj.start_time.strftime('%H:%M')
    
    def get_local_end_time(self, obj):
        """Get end time in provider's timezone"""
        if obj.timezone:
            try:
                provider_tz = pytz.timezone(obj.timezone)
                # Combine date and time, then localize
                naive_datetime = datetime.combine(obj.date, obj.end_time)
                utc_datetime = pytz.UTC.localize(naive_datetime)
                local_datetime = utc_datetime.astimezone(provider_tz)
                return local_datetime.strftime('%H:%M')
            except:
                pass
        return obj.end_time.strftime('%H:%M')
