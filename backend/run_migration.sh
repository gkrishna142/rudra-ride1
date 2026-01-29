#!/bin/bash
# Script to run the role_id migration
# Usage: ./run_migration.sh

echo "Connecting to PostgreSQL database..."
echo "Host: 15.207.8.95"
echo "Port: 6432"
echo "Database: rudraride_db"
echo ""

# Run the SQL migration
psql -h 15.207.8.95 -p 6432 -U app_user -d rudraride_db << EOF

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

-- Verify the change
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'frontend_user' AND column_name = 'role_id';

EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SQL migration completed successfully!"
    echo ""
    echo "Now marking Django migration as applied..."
    cd backend
    python manage.py migrate frontend 0045 --fake
    echo ""
    echo "✅ Migration complete! You can now save role_id values like 'R001'."
else
    echo ""
    echo "❌ Migration failed. Please check your database permissions."
    echo "You may need to run this as a database administrator."
fi

