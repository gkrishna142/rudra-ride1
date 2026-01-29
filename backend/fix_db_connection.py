"""
Fix database connection issues by closing stale connections
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Close any existing connections before Django setup
try:
    from django.db import connections
    for conn in connections.all():
        try:
            conn.close()
        except:
            pass
except:
    pass

django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("Closing stale database connections...")
    try:
        connection.close()
        print("✓ Closed database connections")
    except:
        pass
    
    print("\nRunning migrations...")
    execute_from_command_line(['manage.py', 'migrate'])

