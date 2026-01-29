# Role Permissions API Documentation

## Create Role with Permissions

### Endpoint
```
POST /api/role-permissions/
```
or
```
POST /api/auth/role-permissions/
```

### Request Headers
```
Content-Type: application/json
Authorization: Bearer <token>  (if authentication required)
```

### Request Body
```json
{
    "name": "pavi",
    "description": "wfdesfse",
    "defaultPage": "/users",
    "permissions": {
        "/": {
            "view": true
        },
        "/users": {
            "view": true
        },
        "/roles": {
            "view": true
        }
    }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Role name (e.g., "Super Admin", "Admin", "pavi") |
| `description` | string | No | Role description |
| `defaultPage` | string | No | Default page path after login (default: "/") |
| `permissions` | object | Yes | Dictionary of page paths and their permissions |
| `permissions[page_path]` | object | Yes | Permissions for a specific page |
| `permissions[page_path][permission_type]` | boolean | Yes | Whether permission is allowed |

### Valid Permission Types
- `view` - Can view the page
- `create` - Can create new items
- `edit` - Can edit existing items
- `delete` - Can delete items
- `assign` - Can assign (e.g., assign rides to drivers)
- `approve` - Can approve (e.g., approve drivers)
- `block` - Can block/unblock users
- `refund` - Can process refunds
- `reply` - Can reply to complaints
- `resolve` - Can resolve complaints
- `send` - Can send notifications

### Valid Page Paths
- `/` - Dashboard
- `/users` - User Management
- `/roles` - Roles & Permissions
- `/rides` - Ride Management
- `/drivers` - Driver Management
- `/customers` - Customer Management
- `/zones` - Zone Management
- `/payments` - Payments & Transactions
- `/vehicles` - Vehicles Management
- `/complaints` - Complaints & Support
- `/promotions` - Promotions & Coupons
- `/notifications` - Notifications
- `/settings` - Admin Settings

### Response (Success - 201 Created)
```json
{
    "message_type": "success",
    "message": "Permissions updated successfully. Created: 3, Updated: 0",
    "data": {
        "role": {
            "role_id": "R001",
            "name": "pavi",
            "description": "wfdesfse",
            "default_page": "/users",
            "is_active": true,
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z"
        },
        "role_created": true,
        "permissions": [
            {
                "id": 1,
                "role_id": "R001",
                "page_path": "/",
                "permission_type": "view",
                "is_allowed": true,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "role_id": "R001",
                "page_path": "/users",
                "permission_type": "view",
                "is_allowed": true,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            },
            {
                "id": 3,
                "role_id": "R001",
                "page_path": "/roles",
                "permission_type": "view",
                "is_allowed": true,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            }
        ],
        "created_count": 3,
        "updated_count": 0
    }
}
```

### Response (Error - 400 Bad Request)
```json
{
    "message_type": "error",
    "errors": {
        "name": ["A role with this name already exists."],
        "permissions": {
            "/invalid": ["Invalid permission type 'invalid' for page '/invalid'. Valid types: view, create, edit, delete, assign, approve, block, refund, reply, resolve, send"]
        }
    }
}
```

### Example: Using Axios

```javascript
import axios from 'axios';

const createRole = async () => {
  try {
    const response = await axios.post('/api/role-permissions/', {
      name: "pavi",
      description: "wfdesfse",
      defaultPage: "/users",
      permissions: {
        "/": {
          "view": true
        },
        "/users": {
          "view": true
        },
        "/roles": {
          "view": true
        }
      }
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` // if authentication required
      }
    });
    
    console.log('Role created:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error creating role:', error.response?.data || error.message);
    throw error;
  }
};
```

### Example: Using Fetch

```javascript
const createRole = async () => {
  try {
    const response = await fetch('/api/role-permissions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` // if authentication required
      },
      body: JSON.stringify({
        name: "pavi",
        description: "wfdesfse",
        defaultPage: "/users",
        permissions: {
          "/": {
            "view": true
          },
          "/users": {
            "view": true
          },
          "/roles": {
            "view": true
          }
        }
      })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.message || 'Failed to create role');
    }
    
    console.log('Role created:', data);
    return data;
  } catch (error) {
    console.error('Error creating role:', error);
    throw error;
  }
};
```

### Notes

1. **Auto-generated Role ID**: If `role_id` is not provided in the request, it will be automatically generated (R001, R002, R003, etc.)

2. **Role Creation**: If a role with the given `name` doesn't exist, it will be created automatically. If it exists, the permissions will be updated.

3. **Permission Updates**: When updating permissions for an existing role, only the permissions provided in the request will be updated. Other permissions remain unchanged.

4. **Boolean Values**: All permission values must be boolean (`true` or `false`). Only `true` values are stored in the database.

5. **Case Sensitivity**: Page paths and permission types are case-sensitive. Use lowercase for permission types.

### Database Tables

The data is stored in the following tables:

1. **`frontend_role`** - Stores role information
   - `role_id` (PRIMARY KEY) - Auto-generated if not provided
   - `name` - Role name
   - `description` - Role description
   - `default_page` - Default page path
   - `is_active` - Whether role is active

2. **`frontend_role_permissions`** - Stores permissions
   - `id` (PRIMARY KEY)
   - `role_id` (FOREIGN KEY) - References `frontend_role.role_id`
   - `page_path` - Page route path
   - `permission_type` - Type of permission
   - `is_allowed` - Whether permission is allowed (always true for stored records)

