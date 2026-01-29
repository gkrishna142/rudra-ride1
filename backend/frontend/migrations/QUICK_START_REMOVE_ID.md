# Quick Start: Remove id Column from Database

## The Problem
The `id` column still exists in the database because migration 0039 was **faked** (only updated Django's state, not the actual database).

## Solution: Run SQL Manually

### Option 1: Using Python Script (Easier)
```bash
# Set your database password
export DB_PASSWORD=your_password

# Run the script
python backend/frontend/migrations/remove_id_column.py
```

### Option 2: Using SQL Directly (If you have database access)

**Step 1:** Connect to your PostgreSQL database:
```bash
psql -h 15.207.8.95 -p 6432 -U app_user -d rudraride_db
```

**Step 2:** Run these SQL commands:
```sql
-- Drop the existing primary key
ALTER TABLE frontend_role_permissions DROP CONSTRAINT IF EXISTS frontend_role_permissions_pkey;

-- Drop the id column
ALTER TABLE frontend_role_permissions DROP COLUMN IF EXISTS id;

-- Create composite primary key
ALTER TABLE frontend_role_permissions 
ADD PRIMARY KEY (role_id, page_path, permission_type);
```

**Step 3:** Verify:
```sql
-- Check columns (id should be gone)
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'frontend_role_permissions' 
ORDER BY ordinal_position;
```

### Option 3: Using Database Admin Tool
1. Open pgAdmin, DBeaver, or your preferred database tool
2. Connect to your database
3. Open the SQL editor
4. Copy and paste the SQL from `manual_sql_remove_id_column.sql`
5. Execute it

## After Running SQL

Once the SQL is executed, your database will match Django's state and everything will work correctly. No need to run migrations again - they're already faked.

## Troubleshooting

**Error: "must be owner of table"**
- You need superuser or table owner privileges
- Ask your database administrator to run the SQL for you
- Or ask them to grant you ALTER privileges:
  ```sql
  ALTER TABLE frontend_role_permissions OWNER TO app_user;
  ```

