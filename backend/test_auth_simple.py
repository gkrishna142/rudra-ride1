"""
Quick authentication test - Run this to verify your setup works
"""
import requests
import sys

# Change these to your admin credentials
ADMIN_USERNAME = "admin"  # Change this
ADMIN_PASSWORD = "admin123"  # Change this
BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Testing Zone API Authentication")
print("=" * 60)

# Step 1: Login
print("\n1. Logging in...")
login_url = f"{BASE_URL}/api/auth/admin-login/"
login_data = {
    "username": ADMIN_USERNAME,
    "password": ADMIN_PASSWORD
}

try:
    response = requests.post(login_url, json=login_data, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        access_token = data['tokens']['access']
        print(f"✅ Login successful!")
        print(f"   User: {data['user']['name']} ({data['user']['role']})")
        print(f"\n   Access Token (first 50 chars): {access_token[:50]}...")
        
        # Step 2: Test zones endpoint with token
        print("\n2. Testing zones endpoint with token...")
        zones_url = f"{BASE_URL}/api/auth/zones/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        zones_response = requests.get(zones_url, headers=headers, timeout=10)
        
        if zones_response.status_code == 200:
            zones_data = zones_response.json()
            print(f"✅ Zones endpoint works!")
            print(f"   Found {zones_data['count']} zones")
        else:
            print(f"❌ Zones endpoint failed: {zones_response.status_code}")
            print(f"   Response: {zones_response.json()}")
            
        # Step 3: Test without token (should fail)
        print("\n3. Testing zones endpoint WITHOUT token (should fail)...")
        no_auth_response = requests.get(zones_url, timeout=10)
        
        if no_auth_response.status_code == 401:
            print("✅ Correctly rejected request without token")
            print(f"   Error: {no_auth_response.json()}")
        else:
            print(f"⚠️  Unexpected response: {no_auth_response.status_code}")
            
    else:
        print(f"❌ Login failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("\n   Please check:")
        print("   1. Server is running (python manage.py runserver)")
        print("   2. Username and password are correct")
        print("   3. User has an AdminProfile")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server!")
    print("   Make sure the Django server is running:")
    print("   python manage.py runserver")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)

