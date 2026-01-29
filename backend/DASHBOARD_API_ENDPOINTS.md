# Dashboard API Endpoints Documentation

## Base URL
All endpoints are prefixed with `/api/`

## Dashboard Endpoints

### 1. Service Types Statistics
**Endpoint:** `GET /api/dashboard/service-types/`

**Description:** Get statistics by service types (cab, bike, auto)

**Response:**
```json
[
  {
    "vehicle_type": "cab",
    "total_rides": 150,
    "completed_rides": 120,
    "cancelled_rides": 15,
    "pending_rides": 10,
    "active_rides": 5,
    "revenue": 50000.00
  },
  {
    "vehicle_type": "bike",
    "total_rides": 200,
    "completed_rides": 180,
    "cancelled_rides": 10,
    "pending_rides": 5,
    "active_rides": 5,
    "revenue": 30000.00
  },
  {
    "vehicle_type": "auto",
    "total_rides": 100,
    "completed_rides": 90,
    "cancelled_rides": 5,
    "pending_rides": 3,
    "active_rides": 2,
    "revenue": 20000.00
  }
]
```

---

### 2. Total Rides Daily (Grouped by Day)
**Endpoint:** `GET /api/dashboard/total-rides-daily/`

**Query Parameters:**
- `days` (optional): Number of days to fetch (default: 30)

**Example:** `GET /api/dashboard/total-rides-daily/?days=7`

**Response:**
```json
[
  {
    "date": "2025-12-10",
    "total_rides": 50,
    "completed": 40,
    "cancelled": 5,
    "pending": 3,
    "active": 2,
    "revenue": 15000.00
  },
  {
    "date": "2025-12-09",
    "total_rides": 45,
    "completed": 38,
    "cancelled": 4,
    "pending": 2,
    "active": 1,
    "revenue": 14000.00
  }
]
```

---

### 3. Active Stats Today (Percentage)
**Endpoint:** `GET /api/dashboard/active-stats-today/`

**Description:** Get active rides and drivers statistics for today with percentages

**Response:**
```json
{
  "active_rides": 10,
  "active_rides_percentage": 20.0,
  "active_drivers": 8,
  "active_drivers_percentage": 16.0,
  "total_rides_today": 50,
  "total_drivers_today": 50
}
```

---

### 4. Today's Revenue
**Endpoint:** `GET /api/dashboard/today-revenue/`

**Response:**
```json
{
  "date": "2025-12-10",
  "revenue": 25000.00,
  "currency": "INR"
}
```

---

### 5. Active Users Statistics
**Endpoint:** `GET /api/dashboard/active-users/`

**Description:** Get active users statistics including bookings breakdown

**Response:**
```json
{
  "total_active_users": 500,
  "users_with_rides": 150,
  "bike_bookings": 60,
  "cab_bookings": 70,
  "auto_bookings": 20,
  "drivers_with_bookings": 45,
  "breakdown_by_vehicle": {
    "bike": 60,
    "cab": 70,
    "auto": 20
  }
}
```

---

### 6. Cab Driver Statistics
**Endpoint:** `GET /api/dashboard/cab-driver-stats/`

**Description:** Get cab driver statistics including activation status and revenue

**Response:**
```json
{
  "total_cab_drivers": 100,
  "activated_drivers": 85,
  "inactive_drivers": 15,
  "activation_percentage": 85.0,
  "total_revenue": 500000.00,
  "revenue_today": 15000.00
}
```

---

### 7. Complete Dashboard Overview
**Endpoint:** `GET /api/dashboard/overview/`

**Description:** Get complete dashboard overview with all statistics in one call

**Response:**
```json
{
  "service_types": [...],
  "daily_rides": [...],
  "active_stats": {...},
  "today_revenue": 25000.00,
  "active_users": {...},
  "cab_driver_stats": {...}
}
```

---

## Other Endpoints

### Rides
- `GET /api/rides/` - List all rides
- `POST /api/rides/` - Create a new ride
- `GET /api/rides/{id}/` - Get ride details
- `PUT /api/rides/{id}/` - Update ride
- `DELETE /api/rides/{id}/` - Delete ride

### Drivers
- `GET /api/drivers/` - List all drivers
- `POST /api/drivers/` - Create a new driver profile
- `GET /api/drivers/{id}/` - Get driver details
- `PUT /api/drivers/{id}/` - Update driver
- `DELETE /api/drivers/{id}/` - Delete driver

---

## Usage Examples

### Using cURL

```bash
# Get service types statistics
curl http://localhost:8000/api/dashboard/service-types/

# Get daily rides for last 7 days
curl http://localhost:8000/api/dashboard/total-rides-daily/?days=7

# Get today's revenue
curl http://localhost:8000/api/dashboard/today-revenue/

# Get complete dashboard overview
curl http://localhost:8000/api/dashboard/overview/
```

### Using Python requests

```python
import requests

# Get dashboard overview
response = requests.get('http://localhost:8000/api/dashboard/overview/')
data = response.json()

print(f"Today's Revenue: {data['today_revenue']}")
print(f"Active Rides: {data['active_stats']['active_rides']}")
print(f"Active Drivers: {data['active_stats']['active_drivers']}")
```

---

## Notes

- All dates are in UTC timezone
- Revenue is calculated only from completed rides
- Active rides/drivers are calculated based on rides created today with 'active' status
- Percentages are rounded to 2 decimal places
- All monetary values are in the currency specified (default: INR)

