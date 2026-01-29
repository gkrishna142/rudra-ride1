"""Quick script to verify database data"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Check roles
cursor.execute('SELECT COUNT(*) FROM frontend_role')
role_count = cursor.fetchone()[0]
print(f'✓ Roles in database: {role_count}')

# Check permissions
cursor.execute('SELECT COUNT(*) FROM frontend_role_permissions')
perm_count = cursor.fetchone()[0]
print(f'✓ Permissions in database: {perm_count}')

# List roles
if role_count > 0:
    print('\nRoles:')
    cursor.execute('SELECT role_id, name, is_active FROM frontend_role ORDER BY role_id')
    for row in cursor.fetchall():
        status = "Active" if row[2] else "Inactive"
        print(f'  {row[0]} - {row[1]} ({status})')

# List sample permissions
if perm_count > 0:
    print('\nSample Permissions (first 10):')
    cursor.execute("""
        SELECT role_id, page_path, permission_type, is_allowed 
        FROM frontend_role_permissions 
        ORDER BY role_id, page_path, permission_type 
        LIMIT 10
    """)
    for row in cursor.fetchall():
        status = "allowed" if row[3] else "denied"
        print(f'  {row[0]} | {row[1]:30} | {row[2]:10} | {status}')

