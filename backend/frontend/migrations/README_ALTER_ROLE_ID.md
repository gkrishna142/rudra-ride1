# Alter role_id Column from INTEGER to VARCHAR

## Problem
The migration requires ALTER TABLE privileges on the `frontend_user` table, but the current database user doesn't have sufficient permissions.

## Solution: Run SQL Manually

### Step 1: Run the SQL Script
Connect to your PostgreSQL database as a superuser or the table owner and run the SQL script:

**Option A: Using psql command line**
```bash
psql -h your_host -p your_port -U your_superuser -d your_database -f backend/frontend/migrations/manual_sql_alter_role_id.sql
```

**Option B: Using database admin tool (pgAdmin, DBeaver, etc.)**
1. Open your database admin tool
2. Connect to your database
3. Open the SQL editor
4. Copy and paste the contents of `manual_sql_alter_role_id.sql`
5. Execute it

**Option C: Direct SQL execution**
```sql
-- Convert existing integer role_id values to strings
UPDATE frontend_user 
SET role_id = CASE 
    WHEN role_id IS NULL THEN NULL
    ELSE role_id::text
END
WHERE role_id IS NOT NULL;

-- Alter the column type from INTEGER to VARCHAR(50)
ALTER TABLE frontend_user 
ALTER COLUMN role_id TYPE VARCHAR(50) USING role_id::text;
```

### Step 2: Mark Migration as Applied
After running the SQL script, mark the migration as applied (fake it):

```bash
python manage.py migrate frontend 0045 --fake
```

This tells Django that the migration has been applied without actually running it.

### Step 3: Verify
Verify the change was successful:

```sql
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'frontend_user' AND column_name = 'role_id';
```

Expected result:
- `data_type` should be `character varying`
- `character_maximum_length` should be `50`

## Alternative: Grant Permissions
If you want to run migrations automatically in the future, ask your database administrator to grant ALTER privileges:

```sql
-- Grant ALTER privilege to your database user
ALTER TABLE frontend_user OWNER TO your_database_user;
-- OR
GRANT ALL PRIVILEGES ON TABLE frontend_user TO your_database_user;
```

Then you can run migrations normally:
```bash
python manage.py migrate
```

## What This Migration Does
1. Converts existing integer `role_id` values (e.g., 1, 2) to strings (e.g., "1", "2")
2. Changes the column type from `INTEGER` to `VARCHAR(50)` to support string values like "R001", "R002", etc.
3. Updates Django's model state to reflect the change

## Notes
- Existing integer values will be preserved as strings (1 → "1", 2 → "2")
- NULL values remain NULL
- The column now supports both numeric strings ("1", "2") and alphanumeric strings ("R001", "R002")
- All application code has been updated to handle both string and integer inputs

