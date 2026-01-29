"""
Force delete ONLY frontend_role table data
Uses direct database connection to handle foreign key constraints
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.settings import DATABASES
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def force_delete_roles_only():
    """Force delete only frontend_role table data, keeping permissions"""
    db_config = DATABASES['default']
    
    try:
        # Connect directly with psycopg2 for more control
        conn = psycopg2.connect(
            host=db_config['HOST'],
            port=db_config['PORT'],
            database=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD']
        )
        
        # Set isolation level to allow DDL operations
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check current state
        cursor.execute("SELECT COUNT(*) FROM frontend_role")
        role_count_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
        perm_count = cursor.fetchone()[0]
        
        print(f"Current state:")
        print(f"  Roles: {role_count_before}")
        print(f"  Permissions: {perm_count}")
        
        if role_count_before == 0:
            print("\n✓ frontend_role table is already empty.")
            return
        
        print(f"\nAttempting to delete {role_count_before} roles...")
        
        # Try to drop the foreign key constraint
        constraint_name = "frontend_role_permis_role_id_6897cda1_fk_frontend_"
        
        try:
            print(f"Step 1: Dropping foreign key constraint...")
            cursor.execute(f"""
                ALTER TABLE frontend_role_permissions 
                DROP CONSTRAINT IF EXISTS {constraint_name}
            """)
            print("✓ Foreign key constraint dropped")
        except Exception as e:
            print(f"⚠ Could not drop constraint (may need superuser): {e}")
            print("   Trying to find constraint name...")
            
            # Try to find the constraint name
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
                    actual_constraint = result[0]
                    print(f"   Found constraint: {actual_constraint}")
                    cursor.execute(f"""
                        ALTER TABLE frontend_role_permissions 
                        DROP CONSTRAINT IF EXISTS {actual_constraint}
                    """)
                    print("✓ Foreign key constraint dropped")
                    constraint_name = actual_constraint
            except Exception as e2:
                print(f"⚠ Could not drop constraint: {e2}")
                print("\n⚠ You need to run this SQL manually in pgAdmin:")
                print(f"   ALTER TABLE frontend_role_permissions DROP CONSTRAINT IF EXISTS {constraint_name};")
                print("   DELETE FROM frontend_role;")
                return
        
        # Now delete all roles
        try:
            print(f"\nStep 2: Deleting roles from frontend_role table...")
            cursor.execute("DELETE FROM frontend_role")
            deleted_count = cursor.rowcount
            print(f"✓ Deleted {deleted_count} roles")
        except Exception as e:
            print(f"✗ Error deleting roles: {e}")
            raise
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM frontend_role")
        role_count_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM frontend_role_permissions")
        perm_count_after = cursor.fetchone()[0]
        
        print(f"\n✓ Verification:")
        print(f"   Roles: {role_count_after} (was {role_count_before})")
        print(f"   Permissions: {perm_count_after} (preserved)")
        
        if role_count_after == 0:
            print("\n✓ frontend_role table is now empty!")
        if perm_count_after == perm_count:
            print("✓ frontend_role_permissions data preserved")
        
        # Optionally recreate the constraint
        print(f"\nStep 3: Recreating foreign key constraint...")
        try:
            cursor.execute(f"""
                ALTER TABLE frontend_role_permissions
                ADD CONSTRAINT {constraint_name}
                FOREIGN KEY (role_id) REFERENCES frontend_role(role_id)
                ON DELETE CASCADE
            """)
            print("✓ Foreign key constraint recreated")
        except Exception as e:
            print(f"⚠ Could not recreate constraint (may already exist or need superuser): {e}")
            print("   You can recreate it later if needed.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n✗ Database error: {e}")
        print("\n⚠ You may need to run this SQL manually in pgAdmin:")
        print("""
-- Drop constraint
ALTER TABLE frontend_role_permissions 
DROP CONSTRAINT IF EXISTS frontend_role_permis_role_id_6897cda1_fk_frontend_;

-- Delete roles
DELETE FROM frontend_role;

-- (Optional) Recreate constraint
-- ALTER TABLE frontend_role_permissions
-- ADD CONSTRAINT frontend_role_permis_role_id_6897cda1_fk_frontend_
-- FOREIGN KEY (role_id) REFERENCES frontend_role(role_id)
-- ON DELETE CASCADE;
        """)

if __name__ == '__main__':
    print("=" * 60)
    print("Force Delete frontend_role Table Data Only")
    print("=" * 60)
    print("\nThis will delete ALL data from frontend_role table ONLY.")
    print("frontend_role_permissions data will be PRESERVED.")
    print("\n⚠ WARNING: This action cannot be undone!")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print("\nDeleting roles...")
    force_delete_roles_only()
    
    print("\n" + "=" * 60)
    print("Deletion complete!")
    print("=" * 60)

