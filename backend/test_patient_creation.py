#!/usr/bin/env python3
"""
Test script to verify patient creation functionality
"""
import os
import sys
import django
import json
from datetime import date

# Add the project directory to Python path
sys.path.append('/home/lnv220/Desktop/Demo Backend Project/Demo Backend project (Thinkitive)/python-ai-suit-11/backend')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from providers.patient_serializers import PatientRegistrationSerializer
from providers.patient_models import Patient

def test_patient_creation():
    """Test patient creation with valid data"""
    print("Testing patient creation...")
    
    # Sample patient data
    patient_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe.test@example.com',
        'phone_number': '+1234567890',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!',
        'date_of_birth': '1990-01-01',
        'legal_sex': 'male',
        'gender_identity': 'male',
        'address_line_1': '123 Main St',
        'city': 'New York',
        'state': 'NY',
        'zipcode': '10001',
        'preferred_language': 'english',
        'emergency_contact': {
            'name': 'Jane Doe',
            'phone': '+1234567891',
            'relationship': 'spouse',
            'email': 'jane.doe@example.com'
        },
        'insurance_info': {
            'provider': 'Blue Cross',
            'policy_number': 'BC123456',
            'member_id': 'M123456'
        },
        'medical_history': ['No known allergies', 'Regular checkups']
    }
    
    try:
        # Test serializer validation
        serializer = PatientRegistrationSerializer(data=patient_data)
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            
            # Test patient creation
            patient = serializer.save()
            print(f"✅ Patient created successfully: {patient.email}")
            print(f"   Patient ID: {patient.id}")
            print(f"   Full Name: {patient.full_name}")
            print(f"   Phone: {patient.phone_number}")
            print(f"   Email Verified: {patient.email_verified}")
            
            # Clean up - delete the test patient
            patient.delete()
            print("✅ Test patient cleaned up")
            
        else:
            print("❌ Serializer validation failed:")
            for field, errors in serializer.errors.items():
                print(f"   {field}: {errors}")
                
    except Exception as e:
        print(f"❌ Error during patient creation: {str(e)}")
        import traceback
        traceback.print_exc()

def test_jwt_token_generation():
    """Test JWT token generation"""
    print("\nTesting JWT token generation...")
    
    try:
        from providers.jwt_utils import generate_patient_tokens
        from providers.patient_models import Patient
        
        # Create a temporary patient for testing
        patient = Patient.objects.create(
            first_name='Test',
            last_name='User',
            email='test.jwt@example.com',
            phone_number='+1234567890',
            password_hash='dummy_hash',
            legal_sex='male',
            gender_identity='male',
            address_line_1='123 Test St',
            city='Test City',
            state='NY',
            zipcode='10001'
        )
        
        # Generate tokens
        tokens = generate_patient_tokens(patient)
        print("✅ JWT tokens generated successfully")
        print(f"   Access token length: {len(tokens['access_token'])}")
        print(f"   Refresh token length: {len(tokens['refresh_token'])}")
        print(f"   Token type: {tokens['token_type']}")
        
        # Clean up
        patient.delete()
        print("✅ Test patient cleaned up")
        
    except Exception as e:
        print(f"❌ Error during JWT token generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🧪 Running Patient Creation Tests\n")
    test_patient_creation()
    test_jwt_token_generation()
    print("\n✅ All tests completed!")
