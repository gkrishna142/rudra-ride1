"""
Script to delete ONLY frontend_role table data (keeps permissions)
Provides SQL commands to run manually in pgAdmin if automatic deletion fails
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def delete_roles_with_sql_script():
    """Provide SQL commands for manual execution"""
    print("=" * 60)
    print("Delete frontend_role Table Data Only (Keep Permissions)")
    print("=" * 60)
    
    cursor = connection.cursor()
    
    # Check current counts
    cursor.execute("SELECT COUNT(*) FROM frontend_role")
    role_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
    perm_count = cursor.fetchone()[0]
    
    print(f"\nCurrent state:")
    print(f"  Roles: {role_count}")
    print(f"  Permissions: {perm_count}")
    
    if role_count == 0:
        print("\n✓ frontend_role table is already empty.")
        return
    
    print(f"\n⚠ Foreign key constraint prevents automatic deletion.")
    print(f"   You need to run SQL commands manually in pgAdmin.")
    
    print("\n" + "=" * 60)
    print("SQL COMMANDS TO RUN IN PGADMIN:")
    print("=" * 60)
    print("""
-- Step 1: Drop the foreign key constraint
ALTER TABLE frontend_role_permissions 
DROP CONSTRAINT IF EXISTS frontend_role_permis_role_id_6897cda1_fk_frontend_;

-- Step 2: Delete all roles
DELETE FROM frontend_role;

-- Step 3: (Optional) Recreate constraint if needed later
-- ALTER TABLE frontend_role_permissions
-- ADD CONSTRAINT frontend_role_permis_role_id_6897cda1_fk_frontend_
-- FOREIGN KEY (role_id) REFERENCES frontend_role(role_id)
-- ON DELETE CASCADE;
""")
    print("=" * 60)
    
    print("\n📝 Instructions:")
    print("1. Open pgAdmin")
    print("2. Connect to your database")
    print("3. Open Query Tool")
    print("4. Copy and paste the SQL commands above")
    print("5. Execute the query")
    print("\nOr use the SQL file: backend/delete_roles_keep_permissions.sql")
    
    # Try to get constraint name dynamically
    try:
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'frontend_role_permissions' 
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name LIKE '%role_id%'
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            constraint_name = result[0]
            print(f"\n✓ Found constraint name: {constraint_name}")
            print(f"\nUpdated SQL command:")
            print(f"ALTER TABLE frontend_role_permissions DROP CONSTRAINT IF EXISTS {constraint_name};")
            print(f"DELETE FROM frontend_role;")
    except Exception as e:
        print(f"\n⚠ Could not get constraint name: {e}")

if __name__ == '__main__':
    delete_roles_with_sql_script()

