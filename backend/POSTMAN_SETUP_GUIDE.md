# Postman Setup Guide for Zone API

## ✅ Correct Way to Add Token

### Option 1: Using Authorization Tab (Recommended)

1. Go to **Authorization** tab
2. Select **"Bearer Token"** from the dropdown (NOT "JWT Bearer")
3. Paste your token in the **"Token"** field
4. Postman will automatically create: `Authorization: Bearer <your_token>`

### Option 2: Manual Header (If Authorization tab doesn't work)

1. Go to **Headers** tab
2. Add a new header:
   - **Key**: `Authorization`
   - **Value**: `Bearer <your_token>` (include the word "Bearer" and a space before the token)
   - **Important**: Make sure there's a space between "Bearer" and your token!

## ❌ Common Mistakes

### Wrong:
```
Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
(Missing "Bearer" prefix)

### Wrong:
```
Authorization: BearereyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
(No space after "Bearer")

### ✅ Correct:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
(Word "Bearer" + space + token)

## How to Verify

1. Go to **Headers** tab
2. Look for a header named `Authorization`
3. The value should start with `Bearer ` (with a space)
4. Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Quick Test

1. Make sure your token is in the header correctly
2. Click **Send**
3. You should get **200 OK** with zone data
4. If you still get **401**, check:
   - Token is not expired (tokens last 1 hour)
   - Header format is exactly: `Authorization: Bearer <token>`
   - No extra spaces or characters

