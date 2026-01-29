"""
Simple script to test Zone API endpoints with authentication
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "your_admin_username"  # Change this
ADMIN_PASSWORD = "your_password"  # Change this

def login():
    """Login and get access token"""
    url = f"{BASE_URL}/api/auth/admin-login/"
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    print("🔐 Logging in...")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        access_token = result['tokens']['access']
        print(f"✅ Login successful!")
        print(f"   User: {result['user']['name']} ({result['user']['role']})")
        return access_token
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def get_zones(access_token):
    """Get all zones"""
    url = f"{BASE_URL}/api/auth/zones/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("\n📋 Getting all zones...")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['count']} zones")
        print(json.dumps(result['data'], indent=2))
        return result['data']
    else:
        print(f"❌ Failed: {response.json()}")
        return None

def create_zone(access_token):
    """Create a new zone"""
    url = f"{BASE_URL}/api/auth/zones/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Example zone data
    zone_data = {
        "name": "Test Zone",
        "polygon": "POLYGON((77.2090 28.6139, 77.2290 28.6139, 77.2290 28.6339, 77.2090 28.6339, 77.2090 28.6139))",
        "surge_multiplier": 1.5,
        "is_active": True
    }
    
    print("\n➕ Creating zone...")
    response = requests.post(url, headers=headers, json=zone_data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Zone created successfully!")
        print(json.dumps(result['data'], indent=2))
        return result['data']['id']
    else:
        print(f"❌ Failed: {response.json()}")
        return None

def get_zone(access_token, zone_id):
    """Get zone by ID"""
    url = f"{BASE_URL}/api/auth/zones/{zone_id}/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 Getting zone {zone_id}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Zone details:")
        print(json.dumps(result['data'], indent=2))
        return result['data']
    else:
        print(f"❌ Failed: {response.json()}")
        return None

def update_zone(access_token, zone_id):
    """Update zone"""
    url = f"{BASE_URL}/api/auth/zones/{zone_id}/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "name": "Updated Test Zone",
        "surge_multiplier": 2.0
    }
    
    print(f"\n✏️  Updating zone {zone_id}...")
    response = requests.put(url, headers=headers, json=update_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Zone updated successfully!")
        print(json.dumps(result['data'], indent=2))
        return True
    else:
        print(f"❌ Failed: {response.json()}")
        return False

def disable_zone(access_token, zone_id):
    """Disable zone"""
    url = f"{BASE_URL}/api/auth/zones/{zone_id}/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🗑️  Disabling zone {zone_id}...")
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Zone disabled successfully!")
        print(json.dumps(result['data'], indent=2))
        return True
    else:
        print(f"❌ Failed: {response.json()}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Zone API Test Script")
    print("=" * 60)
    
    # Step 1: Login
    access_token = login()
    
    if not access_token:
        print("\n❌ Cannot proceed without access token. Please check your credentials.")
        exit(1)
    
    # Step 2: Test endpoints
    try:
        # Get all zones
        zones = get_zones(access_token)
        
        # Create a new zone
        new_zone_id = create_zone(access_token)
        
        if new_zone_id:
            # Get the new zone
            get_zone(access_token, new_zone_id)
            
            # Update the zone
            update_zone(access_token, new_zone_id)
            
            # Disable the zone (optional - comment out if you want to keep it)
            # disable_zone(access_token, new_zone_id)
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

