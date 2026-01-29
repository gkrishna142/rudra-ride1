#!/usr/bin/env python
"""
Script to remove id column from frontend_role_permissions table.
Run this script with database credentials that have ALTER privileges.

Usage:
    python remove_id_column.py

Or set environment variables:
    DB_HOST=15.207.8.95
    DB_PORT=6432
    DB_NAME=rudraride_db
    DB_USER=app_user
    DB_PASSWORD=your_password
"""

import os
import sys
import psycopg2
from psycopg2 import sql

# Database connection settings (from Django settings or environment)
DB_HOST = os.getenv('DB_HOST', '15.207.8.95')
DB_PORT = os.getenv('DB_PORT', '6432')
DB_NAME = os.getenv('DB_NAME', 'rudraride_db')
DB_USER = os.getenv('DB_USER', 'app_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

def remove_id_column():
    """Remove id column and set composite primary key"""
    try:
        # Connect to database
        print(f"Connecting to database {DB_NAME} at {DB_HOST}:{DB_PORT} as {DB_USER}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("Connected successfully!")
        
        # Step 1: Check if id column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'frontend_role_permissions' 
            AND column_name = 'id'
        """)
        
        if cursor.fetchone():
            print("✓ Found 'id' column - will remove it")
        else:
            print("⚠ 'id' column not found - may already be removed")
        
        # Step 2: Drop the existing primary key constraint
        print("\nStep 1: Dropping existing primary key constraint...")
        cursor.execute("""
            ALTER TABLE frontend_role_permissions 
            DROP CONSTRAINT IF EXISTS frontend_role_permissions_pkey
        """)
        print("✓ Primary key constraint dropped")
        
        # Step 3: Drop the id column
        print("\nStep 2: Dropping 'id' column...")
        cursor.execute("""
            ALTER TABLE frontend_role_permissions 
            DROP COLUMN IF EXISTS id
        """)
        print("✓ 'id' column dropped")
        
        # Step 4: Create composite primary key
        print("\nStep 3: Creating composite primary key...")
        cursor.execute("""
            ALTER TABLE frontend_role_permissions 
            ADD PRIMARY KEY (role_id, page_path, permission_type)
        """)
        print("✓ Composite primary key created")
        
        # Commit changes
        conn.commit()
        print("\n✅ All changes committed successfully!")
        
        # Verify changes
        print("\nVerifying changes...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'frontend_role_permissions' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("\nCurrent columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # Check primary key
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'frontend_role_permissions' 
            AND constraint_type = 'PRIMARY KEY'
        """)
        pk = cursor.fetchone()
        if pk:
            print(f"\n✓ Primary key: {pk[0]}")
        else:
            print("\n⚠ No primary key found!")
        
        cursor.close()
        conn.close()
        print("\n✅ Done! The id column has been removed and composite primary key is set.")
        return True
        
    except psycopg2.errors.InsufficientPrivilege as e:
        print(f"\n❌ Permission Error: {e}")
        print("\nYou need to run this script as a database superuser or table owner.")
        print("Please:")
        print("1. Connect to the database as a superuser")
        print("2. Run the SQL commands from 'manual_sql_remove_id_column.sql'")
        print("3. Or ask your database administrator to grant ALTER privileges")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Remove id Column from frontend_role_permissions Table")
    print("=" * 60)
    
    if not DB_PASSWORD:
        print("\n⚠ Warning: DB_PASSWORD not set. You may be prompted for password.")
        print("Set it as environment variable: export DB_PASSWORD=your_password")
    
    success = remove_id_column()
    sys.exit(0 if success else 1)

