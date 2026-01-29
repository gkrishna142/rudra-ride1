# How to Test Zone API (Step by Step)

## The Error You're Seeing

```
{
    "detail": "Authentication credentials were not provided."
}
```

This is **CORRECT** - it means the API is working and protecting the endpoints! You just need to provide authentication.

---

## Quick Test (3 Steps)

### Step 1: Login and Get Token

**Using cURL (Command Line):**
```bash
curl -X POST http://localhost:8000/api/auth/admin-login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"your_admin_username\", \"password\": \"your_password\"}"
```

**Using Postman:**
1. Method: `POST`
2. URL: `http://localhost:8000/api/auth/admin-login/`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
    "username": "your_admin_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "message_type": "success",
    "user": {...},
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

**Copy the `access` token!**

---

### Step 2: Use Token to Access Zones

**Using cURL:**
```bash
curl -X GET http://localhost:8000/api/auth/zones/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Using Postman:**
1. Method: `GET`
2. URL: `http://localhost:8000/api/auth/zones/`
3. Headers:
   - `Authorization: Bearer YOUR_ACCESS_TOKEN_HERE`
   - `Content-Type: application/json`

**Replace `YOUR_ACCESS_TOKEN_HERE` with the token from Step 1!**

---

### Step 3: Create a Zone

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/zones/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Test Zone\", \"polygon\": \"POLYGON((77.2090 28.6139, 77.2290 28.6139, 77.2290 28.6339, 77.2090 28.6339, 77.2090 28.6139))\", \"surge_multiplier\": 1.5, \"is_active\": true}"
```

**Using Postman:**
1. Method: `POST`
2. URL: `http://localhost:8000/api/auth/zones/`
3. Headers:
   - `Authorization: Bearer YOUR_ACCESS_TOKEN_HERE`
   - `Content-Type: application/json`
4. Body (raw JSON):
```json
{
    "name": "Test Zone",
    "polygon": "POLYGON((77.2090 28.6139, 77.2290 28.6139, 77.2290 28.6339, 77.2090 28.6339, 77.2090 28.6139))",
    "surge_multiplier": 1.5,
    "is_active": true
}
```

---

## Complete Example (Copy-Paste Ready)

### Windows PowerShell:

```powershell
# Step 1: Login
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/admin-login/" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username": "your_admin_username", "password": "your_password"}'

# Get token
$token = $loginResponse.tokens.access
Write-Host "Token: $token"

# Step 2: Get zones
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
$zones = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/zones/" `
  -Method GET `
  -Headers $headers

Write-Host "Zones: $($zones | ConvertTo-Json -Depth 10)"
```

### Linux/Mac:

```bash
# Step 1: Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/admin-login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_admin_username", "password": "your_password"}' \
  | jq -r '.tokens.access')

echo "Token: $TOKEN"

# Step 2: Get zones
curl -X GET http://localhost:8000/api/auth/zones/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

---

## Testing in Browser (Limited)

Browsers can't easily add custom headers, so you'll get the authentication error. 

**Options:**
1. Use **Postman** (recommended)
2. Use **cURL** (command line)
3. Use browser extensions like **ModHeader** to add Authorization header
4. Use the Django admin panel at `/admin/` (no API needed)

---

## Common Issues

### Issue 1: "Authentication credentials were not provided"
**Solution:** Add the `Authorization: Bearer <token>` header

### Issue 2: "Invalid token" or "Token is invalid or expired"
**Solution:** 
- Token expired (valid for 1 hour)
- Get a new token by logging in again
- Or use refresh token: `POST /api/auth/admin/refresh/` with `{"refresh": "your_refresh_token"}`

### Issue 3: "Access denied. This account does not have admin privileges"
**Solution:** 
- User must have an `AdminProfile`
- Check in Django admin: `/admin/frontend/adminprofile/`
- Admin profile must be `is_active = True`

---

## Verify Your Admin User Exists

Run this in Django shell:
```bash
python manage.py shell
```

Then:
```python
from django.contrib.auth.models import User
from frontend.models import AdminProfile

# Check if user exists
user = User.objects.filter(username='your_admin_username').first()
if user:
    print(f"User found: {user.username}")
    try:
        admin = user.admin_profile
        print(f"Admin profile: {admin.name}, Active: {admin.is_active}, Role: {admin.role}")
    except:
        print("No admin profile - create one in Django admin")
else:
    print("User not found")
```

---

## Need Help?

1. Make sure server is running: `python manage.py runserver`
2. Check your admin credentials
3. Verify AdminProfile exists and is active
4. Use Postman or cURL (not browser directly)

