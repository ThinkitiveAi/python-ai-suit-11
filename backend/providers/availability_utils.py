"""
Utility functions for availability management
"""
import pytz
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.core.exceptions import ValidationError
from .availability_models import Availability, AppointmentSlot


class AvailabilityManager:
    """Manager class for availability operations"""
    
    @staticmethod
    def validate_timezone(timezone_str):
        """Validate if timezone string is valid"""
        try:
            pytz.timezone(timezone_str)
            return True
        except pytz.UnknownTimeZoneError:
            return False
    
    @staticmethod
    def convert_to_utc(date_obj, time_obj, timezone_str):
        """Convert local date/time to UTC"""
        if not AvailabilityManager.validate_timezone(timezone_str):
            raise ValidationError(f"Invalid timezone: {timezone_str}")
        
        local_tz = pytz.timezone(timezone_str)
        local_dt = datetime.combine(date_obj, time_obj)
        localized_dt = local_tz.localize(local_dt)
        return localized_dt.astimezone(pytz.UTC)
    
    @staticmethod
    def convert_from_utc(utc_datetime, timezone_str):
        """Convert UTC datetime to local timezone"""
        if not AvailabilityManager.validate_timezone(timezone_str):
            raise ValidationError(f"Invalid timezone: {timezone_str}")
        
        local_tz = pytz.timezone(timezone_str)
        return utc_datetime.astimezone(local_tz)
    
    @staticmethod
    def check_slot_conflicts(provider, start_datetime, end_datetime, exclude_slot_id=None):
        """Check for conflicting appointment slots"""
        conflicts = AppointmentSlot.objects.filter(
            provider=provider,
            slot_start_time__lt=end_datetime,
            slot_end_time__gt=start_datetime,
            status__in=['available', 'booked']
        )
        
        if exclude_slot_id:
            conflicts = conflicts.exclude(id=exclude_slot_id)
        
        return conflicts.exists()
    
    @staticmethod
    def generate_recurring_dates(start_date, pattern, end_date):
        """Generate list of dates based on recurrence pattern"""
        dates = [start_date]
        current_date = start_date
        
        while current_date < end_date:
            if pattern == 'daily':
                current_date += timedelta(days=1)
            elif pattern == 'weekly':
                current_date += timedelta(weeks=1)
            elif pattern == 'monthly':
                # Handle month increment properly
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    try:
                        current_date = current_date.replace(month=current_date.month + 1)
                    except ValueError:
                        # Handle cases like Jan 31 -> Feb 31 (doesn't exist)
                        if current_date.month == 12:
                            current_date = current_date.replace(year=current_date.year + 1, month=1, day=28)
                        else:
                            current_date = current_date.replace(month=current_date.month + 1, day=28)
            else:
                break
            
            if current_date <= end_date:
                dates.append(current_date)
        
        return dates


class SlotGenerator:
    """Generator class for appointment slots"""
    
    def __init__(self, availability):
        self.availability = availability
    
    def generate_slots(self):
        """Generate all slots for the availability"""
        dates = self._get_dates_to_process()
        total_slots = 0
        
        for date in dates:
            slots_created = self._generate_slots_for_date(date)
            total_slots += slots_created
        
        return total_slots
    
    def _get_dates_to_process(self):
        """Get list of dates to process based on recurrence"""
        if not self.availability.is_recurring or not self.availability.recurrence_end_date:
            return [self.availability.date]
        
        return AvailabilityManager.generate_recurring_dates(
            self.availability.date,
            self.availability.recurrence_pattern,
            self.availability.recurrence_end_date
        )
    
    def _generate_slots_for_date(self, date):
        """Generate slots for a specific date"""
        slots_created = 0
        current_time = self.availability.start_time
        slot_duration = timedelta(minutes=self.availability.slot_duration)
        break_duration = timedelta(minutes=self.availability.break_duration)
        
        while True:
            # Calculate slot times
            slot_start_dt = datetime.combine(date, current_time)
            slot_end_dt = slot_start_dt + slot_duration
            
            # Check if slot fits within availability window
            if slot_end_dt.time() > self.availability.end_time:
                break
            
            # Convert to UTC for storage
            try:
                slot_start_utc = AvailabilityManager.convert_to_utc(
                    date, current_time, self.availability.timezone
                )
                slot_end_utc = AvailabilityManager.convert_to_utc(
                    date, slot_end_dt.time(), self.availability.timezone
                )
            except ValidationError:
                # Skip if timezone conversion fails
                break
            
            # Check for conflicts
            if not AvailabilityManager.check_slot_conflicts(
                self.availability.provider, slot_start_utc, slot_end_utc
            ):
                # Create the slot
                AppointmentSlot.objects.create(
                    availability=self.availability,
                    provider=self.availability.provider,
                    slot_start_time=slot_start_utc,
                    slot_end_time=slot_end_utc,
                    appointment_type=self.availability.appointment_type,
                    status='available'
                )
                slots_created += 1
            
            # Move to next slot time
            next_slot_start = slot_end_dt + break_duration
            current_time = next_slot_start.time()
            
            # Prevent infinite loop
            if next_slot_start.time() >= self.availability.end_time:
                break
        
        return slots_created


class AvailabilityValidator:
    """Validator class for availability data"""
    
    @staticmethod
    def validate_time_range(start_time, end_time):
        """Validate that end time is after start time"""
        if start_time >= end_time:
            raise ValidationError("End time must be after start time")
    
    @staticmethod
    def validate_slot_duration(start_time, end_time, slot_duration, break_duration):
        """Validate slot duration against total availability time"""
        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = datetime.combine(datetime.today(), end_time)
        total_minutes = int((end_dt - start_dt).total_seconds() / 60)
        
        # Validate individual slot duration
        if slot_duration < 15:
            raise ValidationError("Minimum slot duration is 15 minutes")
        
        if slot_duration > 240:  # 4 hours max per slot
            raise ValidationError("Maximum slot duration is 4 hours (240 minutes)")
        
        # Validate break duration
        if break_duration < 0:
            raise ValidationError("Break duration cannot be negative")
        
        if break_duration > 120:  # 2 hours max break
            raise ValidationError("Maximum break duration is 2 hours (120 minutes)")
        
        # Check if at least one slot can fit in the availability window
        minimum_time_needed = slot_duration
        if minimum_time_needed > total_minutes:
            raise ValidationError(
                f"Slot duration ({slot_duration} minutes) cannot exceed total availability time ({total_minutes} minutes)"
            )
    
    @staticmethod
    def validate_recurrence(is_recurring, recurrence_pattern, start_date, end_date):
        """Validate recurrence settings"""
        if is_recurring:
            if not recurrence_pattern:
                raise ValidationError("Recurrence pattern is required for recurring availability")
            
            if recurrence_pattern not in ['daily', 'weekly', 'monthly']:
                raise ValidationError("Invalid recurrence pattern")
            
            if end_date and end_date <= start_date:
                raise ValidationError("Recurrence end date must be after start date")
    
    @staticmethod
    def validate_pricing(pricing_data):
        """Validate pricing information"""
        if not pricing_data:
            return
        
        if 'base_fee' in pricing_data:
            try:
                fee = float(pricing_data['base_fee'])
                if fee < 0:
                    raise ValidationError("Base fee cannot be negative")
                if fee > 10000:
                    raise ValidationError("Base fee seems too high")
            except (ValueError, TypeError):
                raise ValidationError("Invalid base fee format")
        
        if 'currency' in pricing_data:
            valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'INR']
            if pricing_data['currency'] not in valid_currencies:
                raise ValidationError(f"Unsupported currency. Supported: {', '.join(valid_currencies)}")
    
    @staticmethod
    def validate_location(location_data):
        """Validate location information"""
        if not location_data or not isinstance(location_data, dict):
            raise ValidationError("Location data is required")
        
        location_type = location_data.get('type')
        if not location_type:
            raise ValidationError("Location type is required")
        
        valid_types = ['clinic', 'hospital', 'telemedicine', 'home_visit']
        if location_type not in valid_types:
            raise ValidationError(f"Invalid location type. Valid types: {', '.join(valid_types)}")
        
        # Physical locations require address
        if location_type in ['clinic', 'hospital'] and not location_data.get('address'):
            raise ValidationError(f"{location_type.title()} location requires an address")


def handle_daylight_saving_transition(local_datetime, timezone_str):
    """Handle daylight saving time transitions"""
    try:
        tz = pytz.timezone(timezone_str)
        # This will handle ambiguous times during DST transitions
        return tz.localize(local_datetime, is_dst=None)
    except pytz.AmbiguousTimeError:
        # During fall-back, choose the first occurrence (standard time)
        return tz.localize(local_datetime, is_dst=False)
    except pytz.NonExistentTimeError:
        # During spring-forward, adjust to the next valid time
        return tz.localize(local_datetime + timedelta(hours=1), is_dst=True)


def get_provider_timezone(provider):
    """Get provider's default timezone from their profile or clinic address"""
    # This could be enhanced to get timezone from provider profile
    # For now, return a default based on clinic address or UTC
    if hasattr(provider, 'timezone') and provider.timezone:
        return provider.timezone
    
    # Could parse timezone from clinic address here
    # For now, return UTC as default
    return 'UTC'


def calculate_slot_statistics(provider, start_date, end_date):
    """Calculate availability statistics for a provider"""
    slots = AppointmentSlot.objects.filter(
        provider=provider,
        slot_start_time__date__gte=start_date,
        slot_start_time__date__lte=end_date
    )
    
    total_slots = slots.count()
    available_slots = slots.filter(status='available').count()
    booked_slots = slots.filter(status='booked').count()
    cancelled_slots = slots.filter(status='cancelled').count()
    blocked_slots = slots.filter(status='blocked').count()
    
    return {
        'total_slots': total_slots,
        'available_slots': available_slots,
        'booked_slots': booked_slots,
        'cancelled_slots': cancelled_slots,
        'blocked_slots': blocked_slots,
        'utilization_rate': (booked_slots / total_slots * 100) if total_slots > 0 else 0
    }
