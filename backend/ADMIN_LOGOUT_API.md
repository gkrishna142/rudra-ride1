# Admin Logout API Documentation

## Overview
The admin logout endpoint allows admin users to securely log out by blacklisting their refresh token. Once a refresh token is blacklisted, it can no longer be used to generate new access tokens.

---

## Endpoint Details

**URL:** `/api/auth/admin/logout/`  
**Method:** `POST`  
**Authentication:** Not required (public endpoint)  
**Content-Type:** `application/json`

---

## Request Payload

### Required Fields
- `refresh` (string): The refresh token received during login

### Request Body Example
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5OTk5OTk5OSwiaWF0IjoxNjk5OTk5OTk5LCJqdGkiOiIxMjM0NTY3ODkwIiwidXNlcl9pZCI6MX0.abcdefghijklmnopqrstuvwxyz1234567890"
}
```

### cURL Example
```bash
curl -X POST http://localhost:8000/api/auth/admin/logout/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token_here"
  }'
```

### JavaScript/Fetch Example
```javascript
const logoutAdmin = async (refreshToken) => {
  try {
    const response = await fetch('http://localhost:8000/api/auth/admin/logout/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh: refreshToken
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Logout error:', error);
    throw error;
  }
};

// Usage
const refreshToken = localStorage.getItem('refresh_token');
await logoutAdmin(refreshToken);
```

### Python/Requests Example
```python
import requests

def logout_admin(refresh_token):
    url = "http://localhost:8000/api/auth/admin/logout/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "refresh": refresh_token
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Usage
refresh_token = "your_refresh_token_here"
result = logout_admin(refresh_token)
print(result)
```

---

## Response Payloads

### Success Response (200 OK)
```json
{
    "message_type": "success"
}
```

**Status Code:** `200 OK`

**Response Fields:**
- `message_type` (string): Always `"success"` on successful logout

---

### Error Responses

#### 1. Missing Refresh Token (400 Bad Request)
```json
{
    "message_type": "error",
    "error": "Refresh token is required"
}
```

**Status Code:** `400 Bad Request`

**When it occurs:**
- The `refresh` field is missing from the request body
- The `refresh` field is empty or null

---

#### 2. Invalid or Already Blacklisted Token (400 Bad Request)
```json
{
    "message_type": "error",
    "error": "Invalid refresh token or token already blacklisted"
}
```

**Status Code:** `400 Bad Request`

**When it occurs:**
- The refresh token is invalid or malformed
- The refresh token has already been blacklisted
- The refresh token has expired
- The refresh token doesn't exist in the system

---

## Complete Flow Example

### Step 1: Admin Login
```bash
POST /api/auth/admin-login/
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
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

### Step 2: Store Tokens
Store both `access` and `refresh` tokens securely (e.g., in localStorage, secure cookies, or state management).

### Step 3: Use Access Token for API Calls
```bash
GET /api/auth/zones/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Step 4: Logout (Blacklist Refresh Token)
```bash
POST /api/auth/admin/logout/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
    "message_type": "success"
}
```

### Step 5: After Logout
- The refresh token is now blacklisted
- You cannot use it to refresh the access token anymore
- The access token will remain valid until it expires (typically 5-15 minutes)
- To use the API again, you need to log in again to get new tokens

---

## Important Notes

1. **Token Blacklisting:** Once a refresh token is blacklisted, it cannot be used again. You must log in again to get new tokens.

2. **Access Token Validity:** Logging out does not immediately invalidate the access token. The access token will remain valid until it expires. If you need immediate invalidation, consider implementing token revocation on the server side.

3. **Multiple Logouts:** Attempting to logout with the same refresh token twice will result in an error (token already blacklisted).

4. **Security Best Practices:**
   - Always store tokens securely
   - Clear tokens from client storage after logout
   - Use HTTPS in production
   - Implement token refresh before access token expires

5. **Alternative Endpoints:**
   - Login: `/api/auth/admin-login/` or `/api/admin/login/`
   - Logout: `/api/auth/admin/logout/`
   - Refresh Token: `/api/auth/admin/refresh/`

---

## Testing with Postman

1. **Create a new POST request**
   - URL: `http://localhost:8000/api/auth/admin/logout/`

2. **Set Headers:**
   - `Content-Type`: `application/json`

3. **Set Body (raw JSON):**
   ```json
   {
       "refresh": "your_refresh_token_from_login"
   }
   ```

4. **Send Request**
   - Expected response: `200 OK` with `{"message_type": "success"}`

---

## Related Endpoints

- **Admin Login:** `POST /api/auth/admin-login/` - Get access and refresh tokens
- **Refresh Token:** `POST /api/auth/admin/refresh/` - Get new access token using refresh token
- **Admin Logout:** `POST /api/auth/admin/logout/` - Blacklist refresh token (this endpoint)

