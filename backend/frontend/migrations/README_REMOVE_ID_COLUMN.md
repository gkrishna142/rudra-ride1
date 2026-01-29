# Removing id Column from frontend_role_permissions Table

## Problem
The migration requires ALTER privileges on the `frontend_role_permissions` table, but the current database user doesn't have sufficient permissions.

## Solution Options

### Option 1: Run SQL Manually (Recommended)
1. Connect to your PostgreSQL database as a superuser or the table owner
2. Run the SQL script: `manual_sql_remove_id_column.sql`
3. After running the SQL, fake the migration:

```bash
python manage.py migrate frontend 0039 --fake
```

### Option 2: Grant Permissions
Ask your database administrator to grant ALTER privileges:

```sql
-- Grant ALTER privilege to your database user
ALTER TABLE frontend_role_permissions OWNER TO your_database_user;
-- OR
GRANT ALL PRIVILEGES ON TABLE frontend_role_permissions TO your_database_user;
```

Then run the migration normally:
```bash
python manage.py migrate
```

### Option 3: Skip Database Changes (Not Recommended)
If you can't modify the database structure, you can skip the migration entirely, but the model will still expect an `id` field which may cause issues.

## What the Migration Does
1. Drops the existing primary key constraint on `id`
2. Removes the `id` column
3. Creates a composite primary key on `(role_id, page_path, permission_type)`
4. Updates Django's model state to reflect the change

## Verification
After running the SQL, verify the changes:

```sql
-- Check primary key
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'frontend_role_permissions' 
AND constraint_type = 'PRIMARY KEY';

-- Check columns (id should be gone)
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'frontend_role_permissions' 
ORDER BY ordinal_position;
```

