"""
Test database connection to diagnose connection issues
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.db.utils import OperationalError
import time

def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    print("=" * 60)
    
    try:
        # Close any existing connections
        connection.close()
        print("✓ Closed existing connections")
        
        # Test connection
        print("\nAttempting to connect...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✓ Connected successfully!")
            print(f"  PostgreSQL version: {version[:50]}...")
        
        # Test a simple query
        print("\nTesting simple query...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
            table_count = cursor.fetchone()[0]
            print(f"✓ Query successful! Found {table_count} tables in public schema")
        
        # Test frontend_role table
        print("\nTesting frontend_role table...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM frontend_role;")
                role_count = cursor.fetchone()[0]
                print(f"✓ frontend_role table accessible! Count: {role_count}")
        except Exception as e:
            print(f"⚠ Could not access frontend_role: {e}")
        
        print("\n" + "=" * 60)
        print("✓ All connection tests passed!")
        print("=" * 60)
        return True
        
    except OperationalError as e:
        print(f"\n✗ Operational Error: {e}")
        print("\nPossible causes:")
        print("  1. Database server is down or unreachable")
        print("  2. PgBouncer connection pool is exhausted")
        print("  3. Network connectivity issues")
        print("  4. Too many connections from this user")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False
    finally:
        # Always close connection
        try:
            connection.close()
            print("\n✓ Connection closed")
        except:
            pass

if __name__ == '__main__':
    test_connection()

