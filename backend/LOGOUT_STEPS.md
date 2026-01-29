# Step-by-Step: Admin Logout

## Why You're Getting "Token Already Blacklisted"

Your refresh token was already blacklisted. This happens when:
- You already logged out with this token
- You used the `/api/auth/admin/refresh/` endpoint (token rotation blacklists the old token)
- The token was used in a previous test

## Solution: Get a Fresh Token

### Step 1: Login Again

**Request:**
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/auth/admin-login/`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
      "username": "your_username",
      "password": "your_password"
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
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  ← COPY THIS!
    }
}
```

### Step 2: Copy the Refresh Token

Copy the `refresh` token value from the response (the long JWT string).

### Step 3: Use It for Logout

**Request:**
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/auth/admin/logout/`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
      "refresh": "paste_the_refresh_token_from_step_1_here"
  }
  ```

**Expected Success Response:**
```json
{
    "message_type": "success",
    "message": "Successfully logged out. Token has been blacklisted."
}
```

## Important Notes

1. **Always use the LATEST refresh token** - If you use `/api/auth/admin/refresh/`, the old refresh token is automatically blacklisted. Use the NEW one.

2. **One token = One logout** - Each refresh token can only be used for logout once.

3. **Token expires in 24 hours** - If your token expired, you need to login again.

## Quick Test in Postman

1. Create a new request: `POST http://127.0.0.1:8000/api/auth/admin-login/`
2. Add body with your credentials
3. Send and copy the `refresh` token
4. Create another request: `POST http://127.0.0.1:8000/api/auth/admin/logout/`
5. Paste the refresh token in the body
6. Send

