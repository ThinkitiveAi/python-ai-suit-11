#!/usr/bin/env python3
"""
Quick test script to verify patient login endpoint
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login_endpoint():
    """Test the patient login endpoint with different scenarios"""
    
    print("🔍 Testing Patient Login Endpoint")
    print("=" * 50)
    
    # Test 1: POST request to correct endpoint
    print("\n1. Testing POST to /api/v1/patient/login/")
    try:
        response = requests.post(
            f"{BASE_URL}/patient/login/",
            json={
                "email": "test@example.com",
                "password": "test123"
            },
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: GET request to same endpoint (should fail)
    print("\n2. Testing GET to /api/v1/patient/login/ (should fail)")
    try:
        response = requests.get(f"{BASE_URL}/patient/login/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: POST without trailing slash
    print("\n3. Testing POST to /api/v1/patient/login (without trailing slash)")
    try:
        response = requests.post(
            f"{BASE_URL}/patient/login",
            json={
                "email": "test@example.com", 
                "password": "test123"
            },
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Check available endpoints
    print("\n4. Testing available endpoints")
    endpoints_to_test = [
        "/api/v1/patient/",
        "/api/v1/patient/login/",
        "/api/v1/patient/register/",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.options(f"{BASE_URL.replace('/api/v1', '')}{endpoint}")
            print(f"{endpoint}: Status {response.status_code}, Methods: {response.headers.get('Allow', 'N/A')}")
        except Exception as e:
            print(f"{endpoint}: Error - {e}")

if __name__ == "__main__":
    test_login_endpoint()
