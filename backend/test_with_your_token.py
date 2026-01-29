"""
Quick test using your actual token
Just replace YOUR_TOKEN with the token you received
"""
import requests
import json

# Your token from login
YOUR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY2Mzk5OTkxLCJpYXQiOjE3NjYzOTYzOTEsImp0aSI6IjExMTNhZWE2N2FmODRmYTZiNjBjZjc5MDJhZWJmZGJhIiwidXNlcl9pZCI6IjEifQ.taKjll-RM5WISv5EZneLgmp87ciag5gFimpRL95GTuo"

BASE_URL = "http://localhost:8000"

# Headers with your token
headers = {
    "Authorization": f"Bearer {YOUR_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("Testing Zone API with Your Token")
print("=" * 60)

# Test 1: Get all zones
print("\n1. Getting all zones...")
try:
    response = requests.get(f"{BASE_URL}/api/auth/zones/", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {data['count']} zones")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 2: Create a zone
print("\n2. Creating a new zone...")
zone_data = {
    "name": "Test Zone",
    "polygon": "POLYGON((77.2090 28.6139, 77.2290 28.6139, 77.2290 28.6339, 77.2090 28.6339, 77.2090 28.6139))",
    "surge_multiplier": 1.5,
    "is_active": True
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/zones/", headers=headers, json=zone_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Zone created successfully!")
        print(json.dumps(data, indent=2))
        zone_id = data['data']['id']
        
        # Test 3: Get the created zone
        print(f"\n3. Getting zone {zone_id}...")
        response = requests.get(f"{BASE_URL}/api/auth/zones/{zone_id}/", headers=headers)
        if response.status_code == 200:
            print(f"✅ Zone details retrieved!")
            print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)

