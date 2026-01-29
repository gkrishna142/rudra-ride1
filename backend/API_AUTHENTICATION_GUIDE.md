# API Authentication Guide

## Overview
All `/api/auth/` endpoints (including zone management) require authentication using JWT (JSON Web Tokens).

## Step 1: Get Authentication Token

### Admin Login Endpoint
**POST** `/api/auth/admin-login/` or `/api/admin/login/`

**Request Body:**
```json
{
    "username": "your_admin_username",
    "password": "your_password"
}
```

**OR using email:**
```json
{
    "email": "admin@example.com",
    "password": "your_password"
}
```

**Response (Success):**
```json
{
    "message_type": "success",
    "user": {
        "id": 1,
        "name": "Admin User",
        "username": "admin",
        "email": "admin@example.com",
        "role": "superadmin",
        "is_superadmin": true,
        "is_active": true
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

**Save the `access` token** - you'll need it for all API requests.

---

## Step 2: Use Token in API Requests

### For pgAdmin / SQL Editor
pgAdmin doesn't directly support JWT authentication. Use a tool like:
- **Postman**
- **cURL** (command line)
- **HTTPie**
- **Thunder Client** (VS Code extension)
- **Insomnia**

### For Postman / API Testing Tools

1. **Set Authorization Header:**
   - Header Name: `Authorization`
   - Header Value: `Bearer <your_access_token>`
   
   Example:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

2. **Example Request:**
   ```
   GET http://your-server:8000/api/auth/zones/
   Headers:
     Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
     Content-Type: application/json
   ```

---

## Step 3: Testing Zone Endpoints

### List All Zones
```
GET /api/auth/zones/
Authorization: Bearer <your_access_token>
```

### Create Zone
```
POST /api/auth/zones/
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
    "name": "Downtown Zone",
    "polygon": "POLYGON((77.2090 28.6139, 77.2290 28.6139, 77.2290 28.6339, 77.2090 28.6339, 77.2090 28.6139))",
    "surge_multiplier": 1.5,
    "is_active": true
}
```

### Get Zone Details
```
GET /api/auth/zones/{id}/
Authorization: Bearer <your_access_token>
```

### Update Zone
```
PUT /api/auth/zones/{id}/
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
    "name": "Updated Zone Name",
    "polygon": "POLYGON((77.2090 28.6139, 77.2290 28.6139, 77.2290 28.6339, 77.2090 28.6339, 77.2090 28.6139))",
    "surge_multiplier": 2.0,
    "is_active": true
}
```

### Disable Zone
```
DELETE /api/auth/zones/{id}/
Authorization: Bearer <your_access_token>
```

---

## Token Expiration

- **Access Token**: Valid for 1 hour
- **Refresh Token**: Valid for 7 days

### Refresh Access Token

When your access token expires, use the refresh token to get a new one:

**POST** `/api/auth/admin/refresh/`

**Request Body:**
```json
{
    "refresh": "your_refresh_token"
}
```

**Response:**
```json
{
    "message_type": "success",
    "tokens": {
        "access": "new_access_token",
        "refresh": "new_refresh_token"
    }
}
```

---

## cURL Examples

### 1. Login and Get Token
```bash
curl -X POST http://localhost:8000/api/auth/admin-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

### 2. List Zones (using token from step 1)
```bash
curl -X GET http://localhost:8000/api/auth/zones/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### 3. Create Zone
```bash
curl -X POST http://localhost:8000/api/auth/zones/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Zone",
    "polygon": "POLYGON((77.2090 28.6139, 77.2290 28.6139, 77.2290 28.6339, 77.2090 28.6339, 77.2090 28.6139))",
    "surge_multiplier": 1.5,
    "is_active": true
  }'
```

---

## Troubleshooting

### Error: "Authentication credentials were not provided"
- **Solution**: Make sure you include the `Authorization` header with `Bearer <token>`

### Error: "Invalid token" or "Token is invalid or expired"
- **Solution**: Your access token has expired. Use the refresh token to get a new access token, or login again.

### Error: "Access denied. This account does not have admin privileges"
- **Solution**: The user account must have an active AdminProfile. Only admin users can access zone endpoints.

---

## Quick Test Script

Save this as `test_zones_api.py`:

```python
import requests

# Step 1: Login
login_url = "http://localhost:8000/api/auth/admin-login/"
login_data = {
    "username": "your_admin_username",
    "password": "your_password"
}

response = requests.post(login_url, json=login_data)
if response.status_code == 200:
    data = response.json()
    access_token = data['tokens']['access']
    print(f"Access Token: {access_token}")
    
    # Step 2: Use token to access zones
    zones_url = "http://localhost:8000/api/auth/zones/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    zones_response = requests.get(zones_url, headers=headers)
    print(f"Zones Response: {zones_response.json()}")
else:
    print(f"Login failed: {response.json()}")
```

Run with: `python test_zones_api.py`

