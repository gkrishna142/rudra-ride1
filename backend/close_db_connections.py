"""
Close all database connections and wait before retrying
This helps when connection pool is exhausted
"""
import os
import sys
import time
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Close connections before Django setup
try:
    from django.db import connections
    print("Closing all database connections...")
    for alias in connections:
        try:
            connections[alias].close()
            print(f"✓ Closed connection: {alias}")
        except:
            pass
except:
    pass

django.setup()

from django.db import connection

def close_and_wait():
    """Close connections and wait"""
    print("\nClosing database connections...")
    try:
        connection.close()
        print("✓ Closed default connection")
    except:
        pass
    
    # Close all connections
    try:
        from django.db import connections
        for conn in connections.all():
            try:
                conn.close()
            except:
                pass
        print("✓ Closed all connections")
    except:
        pass
    
    print("\nWaiting 5 seconds for connection pool to clear...")
    time.sleep(5)
    
    print("\n✓ Ready to retry database operations")
    print("\nNow you can run:")
    print("  python manage.py migrate")

if __name__ == '__main__':
    close_and_wait()
