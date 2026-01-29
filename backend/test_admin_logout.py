"""
Test script for Admin Logout API
This script tests the admin logout endpoint with your refresh token.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Change if your server is on a different host/port
LOGOUT_ENDPOINT = f"{BASE_URL}/api/auth/admin/logout/"

# Your refresh token
REFRESH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2NjU3MDkyMywiaWF0IjoxNzY2NDg0NTIzLCJqdGkiOiJiMGRmZjIxOWEzNjQ0MjdhYjgzYzNjNDIwNmI2OWNkMiIsInVzZXJfaWQiOiIxIn0.th-GyHGqccLLe7fFd2vvBUFoHh-CKxTVLLFZayTUXuU"

def test_admin_logout():
    """Test the admin logout endpoint"""
    print("=" * 60)
    print("Testing Admin Logout API")
    print("=" * 60)
    print(f"\nEndpoint: {LOGOUT_ENDPOINT}")
    print(f"Refresh Token: {REFRESH_TOKEN[:50]}...")
    print("\n" + "-" * 60)
    
    # Prepare request
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "refresh": REFRESH_TOKEN
    }
    
    try:
        print("\nSending POST request...")
        response = requests.post(
            LOGOUT_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            print(f"\nResponse Body:")
            print(json.dumps(response_data, indent=2))
            
            # Check if logout was successful
            if response.status_code == 200 and response_data.get('message_type') == 'success':
                print("\n✅ SUCCESS: Logout completed successfully!")
                print("   The refresh token has been blacklisted.")
            elif response_data.get('message_type') == 'error':
                print(f"\n❌ ERROR: {response_data.get('error', 'Unknown error')}")
            else:
                print(f"\n⚠️  Unexpected response format")
                
        except json.JSONDecodeError:
            print(f"\nResponse Body (not JSON):")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server.")
        print("   Make sure your Django server is running on", BASE_URL)
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out.")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_admin_logout()

