"""
Diagnostic script to check JWT token status
This helps debug logout issues by checking if a token is valid, expired, or blacklisted.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth.models import User
import json
from datetime import datetime

def decode_token_payload(token_string):
    """Decode JWT token to see its payload without verification"""
    try:
        import jwt
        from django.conf import settings
        
        # Decode without verification to see the payload
        decoded = jwt.decode(token_string, options={"verify_signature": False})
        return decoded
    except Exception as e:
        return {"error": f"Could not decode token: {str(e)}"}

def check_token_status(refresh_token_string):
    """Check the status of a refresh token"""
    print("=" * 70)
    print("JWT Token Status Checker")
    print("=" * 70)
    print(f"\nToken: {refresh_token_string[:50]}...")
    print("\n" + "-" * 70)
    
    # Step 1: Decode token payload (without verification)
    print("\n1. Token Payload (decoded):")
    payload = decode_token_payload(refresh_token_string)
    if "error" not in payload:
        print(json.dumps(payload, indent=2))
        
        # Check expiration
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            is_expired = datetime.now().timestamp() > exp_timestamp
            
            print(f"\n   Expiration Time: {exp_datetime}")
            print(f"   Current Time: {now}")
            print(f"   Status: {'❌ EXPIRED' if is_expired else '✅ Valid (not expired)'}")
            
            if is_expired:
                print(f"   ⚠️  Token expired {now - exp_datetime} ago")
    else:
        print(f"   ❌ {payload['error']}")
    
    # Step 2: Try to create RefreshToken object
    print("\n2. Token Validation:")
    try:
        token = RefreshToken(refresh_token_string)
        print("   ✅ Token format is valid")
        
        # Get token jti (JWT ID)
        jti = token.get('jti')
        user_id = token.get('user_id')
        
        print(f"   Token JTI: {jti}")
        print(f"   User ID: {user_id}")
        
        # Step 3: Check if token is in OutstandingToken table
        print("\n3. Outstanding Token Check:")
        try:
            outstanding_token = OutstandingToken.objects.get(jti=jti)
            print(f"   ✅ Token found in OutstandingToken table")
            print(f"   Created at: {outstanding_token.created_at}")
            
            # Step 4: Check if token is blacklisted
            print("\n4. Blacklist Status:")
            try:
                blacklisted = BlacklistedToken.objects.get(token=outstanding_token)
                print(f"   ❌ Token is BLACKLISTED")
                print(f"   Blacklisted at: {blacklisted.blacklisted_at}")
                return {
                    "status": "blacklisted",
                    "message": "Token has already been blacklisted (already logged out)"
                }
            except BlacklistedToken.DoesNotExist:
                print(f"   ✅ Token is NOT blacklisted")
                
                # Try to blacklist it
                print("\n5. Attempting to blacklist token:")
                try:
                    token.blacklist()
                    print("   ✅ Token successfully blacklisted!")
                    return {
                        "status": "success",
                        "message": "Token has been blacklisted successfully"
                    }
                except Exception as blacklist_error:
                    print(f"   ❌ Failed to blacklist: {str(blacklist_error)}")
                    return {
                        "status": "error",
                        "message": f"Could not blacklist token: {str(blacklist_error)}"
                    }
                    
        except OutstandingToken.DoesNotExist:
            print(f"   ⚠️  Token not found in OutstandingToken table")
            print(f"   This might mean:")
            print(f"   - Token was created before migrations were run")
            print(f"   - Token is from a different server/secret key")
            print(f"   - Token was manually deleted from database")
            
            # Still try to blacklist
            print("\n5. Attempting to blacklist token anyway:")
            try:
                token.blacklist()
                print("   ✅ Token successfully blacklisted!")
                return {
                    "status": "success",
                    "message": "Token has been blacklisted successfully"
                }
            except Exception as blacklist_error:
                print(f"   ❌ Failed to blacklist: {str(blacklist_error)}")
                return {
                    "status": "error",
                    "message": f"Could not blacklist token: {str(blacklist_error)}"
                }
                
    except TokenError as e:
        print(f"   ❌ Token Error: {str(e)}")
        return {
            "status": "error",
            "message": f"Token validation failed: {str(e)}"
        }
    except Exception as e:
        print(f"   ❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }
    
    print("\n" + "=" * 70)
    return None

if __name__ == "__main__":
    # Your refresh token
    REFRESH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2NjU3MDkyMywiaWF0IjoxNzY2NDg0NTIzLCJqdGkiOiJiMGRmZjIxOWEzNjQ0MjdhYjgzYzNjNDIwNmI2OWNkMiIsInVzZXJfaWQiOiIxIn0.th-GyHGqccLLe7fFd2vvBUFoHh-CKxTVLLFZayTUXuU"
    
    result = check_token_status(REFRESH_TOKEN)
    
    if result:
        print(f"\n\nFinal Result: {result['status'].upper()}")
        print(f"Message: {result['message']}")

