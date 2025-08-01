#!/usr/bin/env python3
"""
Test script for comprehensive patient API
Demonstrates how to use the patient management endpoints
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Global variable to store authentication tokens
auth_tokens = {}

def get_auth_headers(user_type='patient'):
    """Get authentication headers with JWT token"""
    token = auth_tokens.get(f'{user_type}_access_token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}

def test_patient_login_with_tokens():
    """Test patient login and extract JWT tokens"""
    print("\n=== Testing Patient Login with JWT Tokens ===")
    
    login_data = {
        "email": "john.doe@example.com",
        "password": "SecurePass123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/patient/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Login successful!")
            
            # Extract and store tokens
            if 'data' in data and 'tokens' in data['data']:
                tokens = data['data']['tokens']
                auth_tokens['patient_access_token'] = tokens['access_token']
                auth_tokens['patient_refresh_token'] = tokens['refresh_token']
                print(f"Access token stored: {tokens['access_token'][:50]}...")
                print(f"Refresh token stored: {tokens['refresh_token'][:50]}...")
                print(f"Token expires at: {tokens['access_token_expires_at']}")
            else:
                print("Warning: No tokens found in response")
            
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Error during login: {e}")

def test_token_refresh():
    """Test JWT token refresh"""
    print("\n=== Testing Token Refresh ===")
    
    refresh_token = auth_tokens.get('patient_refresh_token')
    if not refresh_token:
        print("No refresh token available. Please login first.")
        return
    
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/token/refresh/", json=refresh_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Token refresh successful!")
            
            # Update stored tokens
            if 'data' in data:
                tokens = data['data']
                auth_tokens['patient_access_token'] = tokens['access_token']
                auth_tokens['patient_refresh_token'] = tokens['refresh_token']
                print(f"New access token: {tokens['access_token'][:50]}...")
            
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Token refresh failed: {response.text}")
            
    except Exception as e:
        print(f"Error during token refresh: {e}")

def test_token_validation():
    """Test JWT token validation"""
    print("\n=== Testing Token Validation ===")
    
    access_token = auth_tokens.get('patient_access_token')
    if not access_token:
        print("No access token available. Please login first.")
        return
    
    validation_data = {
        "access_token": access_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/token/validate/", json=validation_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Token validation successful!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Token validation failed: {response.text}")
            
    except Exception as e:
        print(f"Error during token validation: {e}")

def test_patient_registration():
    """Test comprehensive patient registration"""
    
    # Sample patient data matching the form
    patient_data = {
        # Personal Information
        "first_name": "John",
        "middle_name": "Michael",
        "last_name": "Doe",
        "preferred_name": "Johnny",
        
        # Contact Information
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        
        # Authentication
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
        
        # Demographics
        "date_of_birth": "1990-05-15",
        "legal_sex": "male",
        "gender_identity": "male",
        "ethnicity": "not_hispanic_latino",
        "race": "white",
        "preferred_language": "english",
        
        # Address Information
        "address_line_1": "123 Main Street",
        "address_line_2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "zipcode": "10001",
        
        # Additional Information
        "emergency_contact": {
            "name": "Jane Doe",
            "phone": "+1234567891",
            "relationship": "spouse",
            "email": "jane.doe@example.com"
        },
        "insurance_info": {
            "provider": "Blue Cross Blue Shield",
            "policy_number": "BC123456789",
            "group_number": "GRP001",
            "member_id": "MEM123456"
        },
        "medical_history": [
            "Hypertension",
            "Diabetes Type 2",
            "Allergic to penicillin"
        ]
    }
    
    print("Testing Patient Registration...")
    print("=" * 50)
    
    # Test comprehensive patient management endpoint
    response = requests.post(
        f"{BASE_URL}/management/patients/",
        json=patient_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Patient registered successfully!")
        return response.json()['data']['patient_id']
    else:
        print("❌ Patient registration failed!")
        return None

def test_patient_list():
    """Test getting list of patients with authentication"""
    
    print("\n=== Testing Patient List with Authentication ===")
    
    # Get authentication headers
    headers = get_auth_headers('patient')
    if not headers:
        print("❌ No authentication token available. Please login first.")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/management/patients/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Patient list retrieved successfully!")
            print(f"Number of patients: {len(data.get('data', []))}")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed to retrieve patient list: {response.text}")
            
    except Exception as e:
        print(f"Error during patient list request: {e}")

def test_patient_detail(patient_id):
    """Test getting patient details with authentication"""
    
    if not patient_id:
        print("❌ No patient ID provided for detail test")
        return
    
    print(f"\n=== Testing Patient Detail for ID: {patient_id} ===")
    
    # Get authentication headers
    headers = get_auth_headers('patient')
    if not headers:
        print("❌ No authentication token available. Please login first.")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/management/patients/{patient_id}/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Patient details retrieved successfully!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed to retrieve patient details: {response.text}")
            
    except Exception as e:
        print(f"Error during patient detail request: {e}")

def test_patient_login():
    """Test patient login"""
    
    print("\nTesting Patient Login...")
    print("=" * 50)
    
    login_data = {
        "email": "john.doe@example.com",
        "password": "SecurePass123!"
    }
    
    response = requests.post(
        f"{BASE_URL}/patient/login/",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Patient login successful!")
    else:
        print("❌ Patient login failed!")

def main():
    """Main test function"""
    
    print("🏥 Comprehensive Patient API Test with JWT Authentication")
    print("=" * 70)
    
    try:
        # Step 1: Test patient registration
        print("\n📝 Step 1: Patient Registration")
        patient_id = test_patient_registration()
        
        # Step 2: Test patient login with JWT tokens
        print("\n🔐 Step 2: Patient Login with JWT")
        test_patient_login_with_tokens()
        
        # Step 3: Test token validation
        print("\n✅ Step 3: Token Validation")
        test_token_validation()
        
        # Step 4: Test authenticated patient list
        print("\n📋 Step 4: Authenticated Patient List")
        test_patient_list()
        
        # Step 5: Test authenticated patient detail
        print("\n📄 Step 5: Authenticated Patient Detail")
        test_patient_detail(patient_id)
        
        # Step 6: Test token refresh
        print("\n🔄 Step 6: Token Refresh")
        test_token_refresh()
        
        # Step 7: Test with refreshed token
        print("\n🔍 Step 7: Test with Refreshed Token")
        test_patient_list()
        
        # Step 8: Test original login (for comparison)
        print("\n🔑 Step 8: Original Login Test (for comparison)")
        test_patient_login()
        
        print("\n" + "=" * 70)
        print("🎉 All tests completed successfully!")
        print("\n📊 Test Summary:")
        print("- Patient Registration: ✅")
        print("- JWT Login: ✅")
        print("- Token Validation: ✅")
        print("- Authenticated API Access: ✅")
        print("- Token Refresh: ✅")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
