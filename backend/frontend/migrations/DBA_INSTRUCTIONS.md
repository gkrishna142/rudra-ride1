# Database Migration Request - role_id Column Type Change

## Request
Please alter the `role_id` column in the `frontend_user` table from `INTEGER` to `VARCHAR(50)`.

## Why This Is Needed
The application needs to support string role IDs like "R001", "R002", etc., in addition to numeric values like 1, 2.

## SQL Command to Run
```sql
-- This command converts the column type and existing data in one step
ALTER TABLE frontend_user 
ALTER COLUMN role_id TYPE VARCHAR(50) USING 
    CASE 
        WHEN role_id IS NULL THEN NULL
        ELSE role_id::text
    END;
```

## Database Details
- **Host**: 15.207.8.95
- **Port**: 6432
- **Database**: rudraride_db
- **Table**: frontend_user
- **Column**: role_id

## What This Does
1. Converts existing integer values (1, 2, etc.) to strings ("1", "2", etc.)
2. Changes the column type from INTEGER to VARCHAR(50)
3. Allows NULL values to remain NULL
4. Enables storing string role IDs like "R001", "R002", etc.

## Verification Query
After running the ALTER command, verify it worked:
```sql
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'frontend_user' AND column_name = 'role_id';
```

**Expected result:**
- `data_type` should be `character varying`
- `character_maximum_length` should be `50`

## Current Status
The column is currently `integer` type, which prevents storing string values like "R001".

## Alternative: Grant Permissions
If you prefer to grant ALTER privileges to `app_user` instead:
```sql
ALTER TABLE frontend_user OWNER TO app_user;
-- OR
GRANT ALL PRIVILEGES ON TABLE frontend_user TO app_user;
```

Then the application can run the migration itself.

