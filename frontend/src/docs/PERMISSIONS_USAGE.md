# Permissions System Usage Guide

This document explains how to use the permissions system throughout the application.

## Overview

Permissions are received from the login API response and stored in the AuthContext. They control access to routes, menu items, and actions throughout the application.

## Permission Structure

Permissions are organized by route path and action:

```javascript
{
  "/users": {
    "view": true,
    "create": true,
    "edit": true,
    "delete": true
  },
  "/rides": {
    "view": true,
    "create": true,
    "edit": true,
    "delete": true,
    "assign": true
  }
  // ... more routes
}
```

## Using Permissions in Components

### 1. Using the `usePermissions` Hook

Import and use the hook in any component:

```javascript
import { usePermissions } from '../hooks/usePermissions';

const MyComponent = () => {
  const { canView, canCreate, canEdit, canDelete, hasPermission } = usePermissions();

  return (
    <div>
      {canView('/users') && <UsersList />}
      {canCreate('/users') && <button>Add User</button>}
      {canEdit('/users') && <button>Edit</button>}
      {canDelete('/users') && <button>Delete</button>}
      
      {/* For custom actions */}
      {hasPermission('/rides', 'assign') && <button>Assign Ride</button>}
    </div>
  );
};
```

### 2. Available Methods

- `canView(path)` - Check if user can view a route
- `canCreate(path)` - Check if user can create in a route
- `canEdit(path)` - Check if user can edit in a route
- `canDelete(path)` - Check if user can delete in a route
- `hasPermission(path, action)` - Check any specific permission
- `getRoutePermissions(path)` - Get all permissions for a route
- `hasAnyPermission(path)` - Check if user has any permission for a route
- `isSuperAdmin` - Boolean indicating if user is superadmin

### 3. Protecting Routes

Use the `PermissionRoute` component to protect entire routes:

```javascript
import PermissionRoute from '../components/PermissionRoute';

// In App.js or route configuration
<PermissionRoute path="/users" action="view">
  <UserManagement />
</PermissionRoute>

// With custom fallback
<PermissionRoute 
  path="/users" 
  action="create"
  fallback={<div>You don't have permission to create users</div>}
>
  <CreateUserForm />
</PermissionRoute>
```

### 4. Filtering Menu Items

The Sidebar component automatically filters menu items based on view permissions. Menu items are only shown if the user has `view` permission for that route.

### 5. Conditional Rendering

Hide/show UI elements based on permissions:

```javascript
const { canCreate, canEdit, canDelete } = usePermissions();

return (
  <div>
    {canCreate('/users') && (
      <button onClick={handleCreate}>Add New User</button>
    )}
    
    {canEdit('/users') && (
      <button onClick={handleEdit}>Edit</button>
    )}
    
    {canDelete('/users') && (
      <button onClick={handleDelete}>Delete</button>
    )}
  </div>
);
```

### 6. Superadmin Access

Superadmins automatically have all permissions. The `hasPermission` function in AuthContext returns `true` for all checks if `user.is_superadmin` is `true`.

## Permission Actions by Route

Different routes may have different actions:

- **Standard actions**: `view`, `create`, `edit`, `delete`
- **Rides**: `assign`
- **Drivers**: `approve`
- **Customers**: `block`
- **Payments**: `refund`
- **Complaints**: `reply`, `resolve`
- **Notifications**: `send`

## Examples

### Example 1: User Management Page

```javascript
import { usePermissions } from '../hooks/usePermissions';

const UserManagement = () => {
  const { canCreate, canEdit, canDelete } = usePermissions();

  return (
    <div>
      <h1>User Management</h1>
      
      {canCreate('/users') && (
        <button onClick={openCreateModal}>Add New User</button>
      )}
      
      <table>
        {users.map(user => (
          <tr key={user.id}>
            <td>{user.name}</td>
            <td>
              {canEdit('/users') && <button>Edit</button>}
              {canDelete('/users') && <button>Delete</button>}
            </td>
          </tr>
        ))}
      </table>
    </div>
  );
};
```

### Example 2: Ride Management with Assign Permission

```javascript
import { usePermissions } from '../hooks/usePermissions';

const RideManagement = () => {
  const { canView, hasPermission } = usePermissions();

  return (
    <div>
      {canView('/rides') && (
        <>
          <RidesList />
          {hasPermission('/rides', 'assign') && (
            <button onClick={assignRide}>Assign Driver</button>
          )}
        </>
      )}
    </div>
  );
};
```

## Storage

Permissions are:
- Stored in `localStorage` as `permissions` (JSON string)
- Stored in AuthContext state
- Automatically loaded on app initialization
- Cleared on logout

## Notes

- Dashboard route (`/`) is always accessible to authenticated users
- Superadmins bypass all permission checks
- If permissions are not loaded, all checks return `false` (deny by default)
- Permissions are updated on every login

