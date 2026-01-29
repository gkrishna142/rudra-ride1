#!/bin/bash
# Test Admin Logout API using cURL

# Configuration
BASE_URL="http://localhost:8000"
ENDPOINT="${BASE_URL}/api/auth/admin/logout/"

# Your refresh token
REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2NjU3MDkyMywiaWF0IjoxNzY2NDg0NTIzLCJqdGkiOiJiMGRmZjIxOWEzNjQ0MjdhYjgzYzNjNDIwNmI2OWNkMiIsInVzZXJfaWQiOiIxIn0.th-GyHGqccLLe7fFd2vvBUFoHh-CKxTVLLFZayTUXuU"

echo "============================================================"
echo "Testing Admin Logout API"
echo "============================================================"
echo ""
echo "Endpoint: $ENDPOINT"
echo "Refresh Token: ${REFRESH_TOKEN:0:50}..."
echo ""
echo "------------------------------------------------------------"
echo ""

# Make the request
curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -v

echo ""
echo "============================================================"

