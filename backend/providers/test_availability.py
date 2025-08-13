"""
Unit tests for Provider Availability Management
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, date, time, timedelta
import pytz
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch

from .models import Provider
from .availability_models import Availability, AppointmentSlot
from .availability_utils import (
    AvailabilityManager, SlotGenerator, AvailabilityValidator,
    handle_daylight_saving_transition, calculate_slot_statistics
)
from .availability_serializers import AvailabilityCreateSerializer


class AvailabilityManagerTestCase(TestCase):
    """Test cases for AvailabilityManager utility class"""
    
    def test_validate_timezone_valid(self):
        """Test timezone validation with valid timezone"""
        self.assertTrue(AvailabilityManager.validate_timezone('America/New_York'))
        self.assertTrue(AvailabilityManager.validate_timezone('UTC'))
        self.assertTrue(AvailabilityManager.validate_timezone('Europe/London'))
    
    def test_validate_timezone_invalid(self):
        """Test timezone validation with invalid timezone"""
        self.assertFalse(AvailabilityManager.validate_timezone('Invalid/Timezone'))
        self.assertFalse(AvailabilityManager.validate_timezone(''))
        self.assertFalse(AvailabilityManager.validate_timezone('Not_A_Timezone'))
    
    def test_convert_to_utc(self):
        """Test conversion from local time to UTC"""
        test_date = date(2024, 2, 15)
        test_time = time(14, 30)  # 2:30 PM
        
        # EST is UTC-5
        utc_datetime = AvailabilityManager.convert_to_utc(
            test_date, test_time, 'America/New_York'
        )
        
        # Should be 7:30 PM UTC (2:30 PM EST + 5 hours)
        expected_utc = datetime(2024, 2, 15, 19, 30, tzinfo=pytz.UTC)
        self.assertEqual(utc_datetime, expected_utc)
    
    def test_convert_from_utc(self):
        """Test conversion from UTC to local time"""
        utc_datetime = datetime(2024, 2, 15, 19, 30, tzinfo=pytz.UTC)
        
        local_datetime = AvailabilityManager.convert_from_utc(
            utc_datetime, 'America/New_York'
        )
        
        # Should be 2:30 PM EST
        est_tz = pytz.timezone('America/New_York')
        expected_local = est_tz.localize(datetime(2024, 2, 15, 14, 30))
        self.assertEqual(local_datetime, expected_local)
    
    def test_generate_recurring_dates_daily(self):
        """Test daily recurrence date generation"""
        start_date = date(2024, 2, 15)
        end_date = date(2024, 2, 18)
        
        dates = AvailabilityManager.generate_recurring_dates(
            start_date, 'daily', end_date
        )
        
        expected_dates = [
            date(2024, 2, 15),
            date(2024, 2, 16),
            date(2024, 2, 17),
            date(2024, 2, 18)
        ]
        self.assertEqual(dates, expected_dates)
    
    def test_generate_recurring_dates_weekly(self):
        """Test weekly recurrence date generation"""
        start_date = date(2024, 2, 15)
        end_date = date(2024, 3, 1)
        
        dates = AvailabilityManager.generate_recurring_dates(
            start_date, 'weekly', end_date
        )
        
        expected_dates = [
            date(2024, 2, 15),
            date(2024, 2, 22),
            date(2024, 2, 29)
        ]
        self.assertEqual(dates, expected_dates)
    
    def test_generate_recurring_dates_monthly(self):
        """Test monthly recurrence date generation"""
        start_date = date(2024, 1, 15)
        end_date = date(2024, 4, 1)
        
        dates = AvailabilityManager.generate_recurring_dates(
            start_date, 'monthly', end_date
        )
        
        expected_dates = [
            date(2024, 1, 15),
            date(2024, 2, 15),
            date(2024, 3, 15)
        ]
        self.assertEqual(dates, expected_dates)


class AvailabilityValidatorTestCase(TestCase):
    """Test cases for AvailabilityValidator utility class"""
    
    def test_validate_time_range_valid(self):
        """Test valid time range validation"""
        start_time = time(9, 0)
        end_time = time(17, 0)
        
        # Should not raise exception
        try:
            AvailabilityValidator.validate_time_range(start_time, end_time)
        except Exception:
            self.fail("validate_time_range raised exception for valid times")
    
    def test_validate_time_range_invalid(self):
        """Test invalid time range validation"""
        start_time = time(17, 0)
        end_time = time(9, 0)
        
        with self.assertRaises(Exception):
            AvailabilityValidator.validate_time_range(start_time, end_time)
    
    def test_validate_slot_duration_valid(self):
        """Test valid slot duration validation"""
        start_time = time(9, 0)
        end_time = time(17, 0)  # 8 hours = 480 minutes
        slot_duration = 30
        break_duration = 15
        
        # Should not raise exception
        try:
            AvailabilityValidator.validate_slot_duration(
                start_time, end_time, slot_duration, break_duration
            )
        except Exception:
            self.fail("validate_slot_duration raised exception for valid duration")
    
    def test_validate_slot_duration_too_long(self):
        """Test slot duration that exceeds available time"""
        start_time = time(9, 0)
        end_time = time(10, 0)  # 1 hour = 60 minutes
        slot_duration = 90  # 90 minutes > 60 minutes available
        break_duration = 0
        
        with self.assertRaises(Exception):
            AvailabilityValidator.validate_slot_duration(
                start_time, end_time, slot_duration, break_duration
            )
    
    def test_validate_pricing_valid(self):
        """Test valid pricing validation"""
        pricing_data = {
            'base_fee': 150.00,
            'insurance_accepted': True,
            'currency': 'USD'
        }
        
        try:
            AvailabilityValidator.validate_pricing(pricing_data)
        except Exception:
            self.fail("validate_pricing raised exception for valid pricing")
    
    def test_validate_pricing_negative_fee(self):
        """Test pricing validation with negative fee"""
        pricing_data = {
            'base_fee': -50.00,
            'currency': 'USD'
        }
        
        with self.assertRaises(Exception):
            AvailabilityValidator.validate_pricing(pricing_data)
    
    def test_validate_location_valid(self):
        """Test valid location validation"""
        location_data = {
            'type': 'clinic',
            'address': '123 Medical Center Dr, New York, NY',
            'room_number': 'Room 205'
        }
        
        try:
            AvailabilityValidator.validate_location(location_data)
        except Exception:
            self.fail("validate_location raised exception for valid location")
    
    def test_validate_location_missing_address(self):
        """Test location validation with missing address for physical location"""
        location_data = {
            'type': 'clinic'
            # Missing address
        }
        
        with self.assertRaises(Exception):
            AvailabilityValidator.validate_location(location_data)


class ProviderAvailabilityModelTestCase(TestCase):
    """Test cases for Availability and AppointmentSlot models"""
    
    def setUp(self):
        """Set up test data"""
        self.provider = Provider.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone_number='+1234567890',
            password_hash='hashed_password',
            specialization='Cardiology',
            license_number='LIC123456',
            years_of_experience=10,
            clinic_address={'address': '123 Medical Center Dr, New York, NY'}
        )
    
    def test_availability_creation(self):
        """Test creating an availability record"""
        availability = Availability.objects.create(
            provider=self.provider,
            date=date(2024, 2, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            timezone='America/New_York',
            slot_duration=30,
            appointment_type='consultation',
            location={
                'type': 'clinic',
                'address': '123 Medical Center Dr',
                'room_number': 'Room 205'
            },
            pricing={
                'base_fee': 150.00,
                'insurance_accepted': True,
                'currency': 'USD'
            }
        )
        
        self.assertEqual(availability.provider, self.provider)
        self.assertEqual(availability.date, date(2024, 2, 15))
        self.assertEqual(availability.duration_minutes, 480)  # 8 hours
        self.assertEqual(availability.total_slots, 10)  # 480 / (30 + 15) = 10.67, floor to 10
    
    def test_appointment_slot_creation(self):
        """Test creating an appointment slot"""
        availability = Availability.objects.create(
            provider=self.provider,
            date=date(2024, 2, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            timezone='America/New_York',
            slot_duration=30,
            appointment_type='consultation',
            location={'type': 'clinic', 'address': '123 Medical Center Dr'}
        )
        
        slot_start = datetime(2024, 2, 15, 14, 0, tzinfo=pytz.UTC)  # 2 PM UTC
        slot_end = datetime(2024, 2, 15, 14, 30, tzinfo=pytz.UTC)   # 2:30 PM UTC
        
        slot = AppointmentSlot.objects.create(
            availability=availability,
            provider=self.provider,
            slot_start_time=slot_start,
            slot_end_time=slot_end,
            appointment_type='consultation',
            status='available'
        )
        
        self.assertEqual(slot.provider, self.provider)
        self.assertEqual(slot.availability, availability)
        self.assertEqual(slot.status, 'available')
        
        # Test timezone conversion
        local_start = slot.get_local_start_time()
        self.assertEqual(local_start.hour, 9)  # Should be 9 AM EST (14 UTC - 5)


class SlotGeneratorTestCase(TestCase):
    """Test cases for SlotGenerator utility class"""
    
    def setUp(self):
        """Set up test data"""
        self.provider = Provider.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            phone_number='+1234567891',
            password_hash='hashed_password',
            specialization='Dermatology',
            license_number='LIC123457',
            years_of_experience=8,
            clinic_address={'address': '456 Health Plaza, Boston, MA'}
        )
        
        self.availability = Availability.objects.create(
            provider=self.provider,
            date=date(2024, 2, 15),
            start_time=time(9, 0),
            end_time=time(12, 0),  # 3 hours
            timezone='America/New_York',
            slot_duration=30,
            break_duration=15,
            appointment_type='consultation',
            location={'type': 'clinic', 'address': '456 Health Plaza'}
        )
    
    def test_slot_generation_single_date(self):
        """Test slot generation for a single date"""
        generator = SlotGenerator(self.availability)
        slots_created = generator.generate_slots()
        
        # 3 hours = 180 minutes, slot + break = 45 minutes
        # 180 / 45 = 4 slots
        self.assertEqual(slots_created, 4)
        
        # Verify slots were created in database
        slots = AppointmentSlot.objects.filter(availability=self.availability)
        self.assertEqual(slots.count(), 4)
        
        # Verify first slot timing
        first_slot = slots.first()
        local_start = first_slot.get_local_start_time()
        self.assertEqual(local_start.hour, 9)
        self.assertEqual(local_start.minute, 0)
    
    def test_slot_generation_recurring(self):
        """Test slot generation for recurring availability"""
        self.availability.is_recurring = True
        self.availability.recurrence_pattern = 'daily'
        self.availability.recurrence_end_date = date(2024, 2, 17)  # 3 days total
        self.availability.save()
        
        generator = SlotGenerator(self.availability)
        slots_created = generator.generate_slots()
        
        # 4 slots per day × 3 days = 12 slots
        self.assertEqual(slots_created, 12)
        
        # Verify slots were created for all dates
        slots = AppointmentSlot.objects.filter(availability=self.availability)
        self.assertEqual(slots.count(), 12)


class ProviderAvailabilityAPITestCase(APITestCase):
    """Test cases for Provider Availability API endpoints"""
    
    def setUp(self):
        """Set up test data and authentication"""
        self.provider = Provider.objects.create(
            first_name='Test',
            last_name='Provider',
            email='test.provider@example.com',
            phone_number='+1234567892',
            password_hash='hashed_password',
            specialization='General Medicine',
            license_number='LIC123458',
            years_of_experience=5,
            clinic_address={'address': '789 Care Center, Chicago, IL'}
        )
        
        self.client = APIClient()
        # Mock authentication - in real implementation, use proper JWT token
        self.client.force_authenticate(user=self.provider)
    
    def test_create_availability_success(self):
        """Test successful availability creation via API"""
        data = {
            'date': '2024-02-15',
            'start_time': '09:00',
            'end_time': '17:00',
            'timezone': 'America/Chicago',
            'slot_duration': 30,
            'break_duration': 15,
            'appointment_type': 'consultation',
            'location': {
                'type': 'clinic',
                'address': '789 Care Center, Chicago, IL',
                'room_number': 'Room 101'
            },
            'pricing': {
                'base_fee': 125.00,
                'insurance_accepted': True,
                'currency': 'USD'
            },
            'notes': 'Standard consultation slots'
        }
        
        response = self.client.post('/api/v1/provider/availability', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('availability_id', response.data['data'])
        self.assertGreater(response.data['data']['slots_created'], 0)
    
    def test_create_availability_invalid_timezone(self):
        """Test availability creation with invalid timezone"""
        data = {
            'date': '2024-02-15',
            'start_time': '09:00',
            'end_time': '17:00',
            'timezone': 'Invalid/Timezone',
            'slot_duration': 30,
            'appointment_type': 'consultation',
            'location': {
                'type': 'clinic',
                'address': '789 Care Center'
            }
        }
        
        response = self.client.post('/api/v1/provider/availability', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_create_availability_invalid_time_range(self):
        """Test availability creation with invalid time range"""
        data = {
            'date': '2024-02-15',
            'start_time': '17:00',  # End before start
            'end_time': '09:00',
            'timezone': 'America/Chicago',
            'slot_duration': 30,
            'appointment_type': 'consultation',
            'location': {
                'type': 'clinic',
                'address': '789 Care Center'
            }
        }
        
        response = self.client.post('/api/v1/provider/availability', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_get_provider_availability(self):
        """Test retrieving provider availability"""
        # Create some availability first
        availability = Availability.objects.create(
            provider=self.provider,
            date=date(2024, 2, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            timezone='America/Chicago',
            slot_duration=30,
            appointment_type='consultation',
            location={'type': 'clinic', 'address': '789 Care Center'}
        )
        
        # Create a slot
        AppointmentSlot.objects.create(
            availability=availability,
            provider=self.provider,
            slot_start_time=datetime(2024, 2, 15, 15, 0, tzinfo=pytz.UTC),
            slot_end_time=datetime(2024, 2, 15, 15, 30, tzinfo=pytz.UTC),
            appointment_type='consultation',
            status='available'
        )
        
        response = self.client.get(
            f'/api/v1/provider/{self.provider.id}/availability',
            {'start_date': '2024-02-15', 'end_date': '2024-02-15'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['availability']), 1)
    
    def test_availability_search_public(self):
        """Test public availability search endpoint"""
        # Create availability and slots
        availability = Availability.objects.create(
            provider=self.provider,
            date=date(2024, 2, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            timezone='America/Chicago',
            slot_duration=30,
            appointment_type='consultation',
            location={'type': 'clinic', 'address': '789 Care Center, Chicago, IL'},
            pricing={'base_fee': 125.00, 'insurance_accepted': True, 'currency': 'USD'}
        )
        
        AppointmentSlot.objects.create(
            availability=availability,
            provider=self.provider,
            slot_start_time=datetime(2024, 2, 15, 15, 0, tzinfo=pytz.UTC),
            slot_end_time=datetime(2024, 2, 15, 15, 30, tzinfo=pytz.UTC),
            appointment_type='consultation',
            status='available'
        )
        
        # Test search without authentication (public endpoint)
        client = APIClient()  # No authentication
        response = client.get('/api/v1/availability/search', {
            'date': '2024-02-15',
            'specialization': 'General Medicine'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreater(response.data['data']['total_results'], 0)


class DaylightSavingTestCase(TestCase):
    """Test cases for daylight saving time transitions"""
    
    def test_spring_forward_transition(self):
        """Test handling of spring forward DST transition"""
        # 2024 DST starts March 10, 2:00 AM becomes 3:00 AM
        non_existent_time = datetime(2024, 3, 10, 2, 30)
        
        result = handle_daylight_saving_transition(
            non_existent_time, 'America/New_York'
        )
        
        # Should be adjusted to 3:30 AM EDT
        self.assertEqual(result.hour, 3)
        self.assertEqual(result.minute, 30)
    
    def test_fall_back_transition(self):
        """Test handling of fall back DST transition"""
        # 2024 DST ends November 3, 2:00 AM becomes 1:00 AM
        ambiguous_time = datetime(2024, 11, 3, 1, 30)
        
        result = handle_daylight_saving_transition(
            ambiguous_time, 'America/New_York'
        )
        
        # Should choose standard time (first occurrence)
        self.assertFalse(result.dst())


class StatisticsTestCase(TestCase):
    """Test cases for availability statistics"""
    
    def setUp(self):
        """Set up test data"""
        self.provider = Provider.objects.create(
            first_name='Stats',
            last_name='Provider',
            email='stats.provider@example.com',
            phone_number='+1234567893',
            password_hash='hashed_password',
            specialization='Statistics',
            license_number='LIC123459',
            years_of_experience=3,
            clinic_address={'address': '999 Stats Center'}
        )
        
        # Create availability
        availability = Availability.objects.create(
            provider=self.provider,
            date=date(2024, 2, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            timezone='UTC',
            slot_duration=60,
            appointment_type='consultation',
            location={'type': 'clinic', 'address': '999 Stats Center'}
        )
        
        # Create slots with different statuses
        base_time = datetime(2024, 2, 15, 9, 0, tzinfo=pytz.UTC)
        statuses = ['available', 'available', 'booked', 'cancelled', 'blocked']
        
        for i, status in enumerate(statuses):
            AppointmentSlot.objects.create(
                availability=availability,
                provider=self.provider,
                slot_start_time=base_time + timedelta(hours=i),
                slot_end_time=base_time + timedelta(hours=i+1),
                appointment_type='consultation',
                status=status
            )
    
    def test_calculate_slot_statistics(self):
        """Test slot statistics calculation"""
        stats = calculate_slot_statistics(
            self.provider,
            date(2024, 2, 15),
            date(2024, 2, 15)
        )
        
        self.assertEqual(stats['total_slots'], 5)
        self.assertEqual(stats['available_slots'], 2)
        self.assertEqual(stats['booked_slots'], 1)
        self.assertEqual(stats['cancelled_slots'], 1)
        self.assertEqual(stats['blocked_slots'], 1)
        self.assertEqual(stats['utilization_rate'], 20.0)  # 1 booked out of 5 total


if __name__ == '__main__':
    # Run tests with: python manage.py test providers.test_availability
    pass
