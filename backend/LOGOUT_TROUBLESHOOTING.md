# Logout Troubleshooting Guide

## Common Error: "Invalid refresh token or token already blacklisted"

### Why This Happens

1. **Token Rotation**: If you used the `/api/auth/admin/refresh/` endpoint to get a new access token, your old refresh token was automatically blacklisted. This is by design for security.

2. **Already Logged Out**: If you already called the logout endpoint successfully, the token is already blacklisted and cannot be used again.

3. **Token Expired**: The refresh token has expired (check expiration time in token payload).

### Solutions

#### Solution 1: Get a Fresh Token
If your token is blacklisted, you need to login again to get a new refresh token:

```bash
POST /api/auth/admin-login/
{
    "username": "your_username",
    "password": "your_password"
}
```

This will give you a new `access` and `refresh` token.

#### Solution 2: Check Token Status
Use the diagnostic script to check your token:

```bash
cd backend
python check_token_status.py
```

#### Solution 3: Use the Correct Token
Make sure you're using the **refresh token** (not the access token) for logout:

- ✅ **Refresh Token**: Use this for logout
- ❌ **Access Token**: Do NOT use this for logout

### How Token Rotation Works

When `ROTATE_REFRESH_TOKENS: True` is set (which it is in your settings):

1. You login → Get `access_token_1` and `refresh_token_1`
2. You use `/api/auth/admin/refresh/` with `refresh_token_1`
3. You get `access_token_2` and `refresh_token_2`
4. **`refresh_token_1` is automatically blacklisted**
5. You can only use `refresh_token_2` now

**Important**: After using the refresh endpoint, you must use the NEW refresh token for logout, not the old one.

### Best Practice Workflow

1. **Login** → Store both `access` and `refresh` tokens
2. **Use API** → Use `access` token in Authorization header
3. **When access expires** → Use `refresh` token to get new tokens
4. **Update stored tokens** → Replace old tokens with new ones
5. **Logout** → Use the current `refresh` token (the latest one)

### Testing Logout

1. **First, login to get fresh tokens:**
   ```bash
   POST http://localhost:8000/api/auth/admin-login/
   Content-Type: application/json
   
   {
       "username": "admin",
       "password": "your_password"
   }
   ```

2. **Save the refresh token from the response**

3. **Use that refresh token for logout:**
   ```bash
   POST http://localhost:8000/api/auth/admin/logout/
   Content-Type: application/json
   
   {
       "refresh": "your_refresh_token_here"
   }
   ```

4. **Expected response:**
   ```json
   {
       "message_type": "success",
       "message": "Successfully logged out. Token has been blacklisted."
   }
   ```

### Error Messages (Improved)

The logout endpoint now provides more specific error messages:

- **"Token has already been blacklisted (already logged out)"** → Token was already used for logout
- **"Refresh token has expired. Please login again."** → Token expired, need to login again
- **"Invalid refresh token format"** → Token format is wrong
- **"Invalid refresh token or token already blacklisted"** → Generic error (check details in DEBUG mode)

### Quick Fix

If you're getting the error, simply:

1. **Login again** to get a fresh refresh token
2. **Use that new refresh token** for logout
3. **Don't use the refresh endpoint** between login and logout (or use the new token if you do)

