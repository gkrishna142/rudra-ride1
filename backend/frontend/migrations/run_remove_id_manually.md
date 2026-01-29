# How to Remove id Column from frontend_role_permissions Table

## Current Situation
The migration was faked (only updated Django's state), so the `id` column still exists in the database.

## Solution: Run SQL Manually

You need to connect to your PostgreSQL database as a **superuser or table owner** and run these SQL commands:

### Step 1: Connect to Database
```bash
# Using psql
psql -h 15.207.8.95 -p 6432 -U app_user -d rudraride_db

# Or use your database admin tool (pgAdmin, DBeaver, etc.)
```

### Step 2: Run These SQL Commands
```sql
-- Step 1: Drop the existing primary key constraint
ALTER TABLE frontend_role_permissions DROP CONSTRAINT IF EXISTS frontend_role_permissions_pkey;

-- Step 2: Drop the id column
ALTER TABLE frontend_role_permissions DROP COLUMN IF EXISTS id;

-- Step 3: Create composite primary key on (role_id, page_path, permission_type)
ALTER TABLE frontend_role_permissions 
ADD PRIMARY KEY (role_id, page_path, permission_type);
```

### Step 3: Verify the Changes
```sql
-- Check that id column is removed
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'frontend_role_permissions' 
ORDER BY ordinal_position;

-- Check the primary key constraint
SELECT 
    constraint_name, 
    constraint_type,
    table_name
FROM information_schema.table_constraints 
WHERE table_name = 'frontend_role_permissions' 
AND constraint_type = 'PRIMARY KEY';
```

### Step 4: After Running SQL
Once you've run the SQL manually, the database will match Django's state and everything should work correctly.

## Alternative: If You Don't Have Database Access
If you don't have superuser/owner access, ask your database administrator to:
1. Run the SQL commands above
2. Or grant you ALTER privileges on the table:
   ```sql
   ALTER TABLE frontend_role_permissions OWNER TO app_user;
   -- OR
   GRANT ALL PRIVILEGES ON TABLE frontend_role_permissions TO app_user;
   ```

