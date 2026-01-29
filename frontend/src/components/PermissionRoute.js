import React from 'react';
import PropTypes from 'prop-types';
import { Navigate, useLocation } from 'react-router-dom';
import { usePermissions } from '../hooks/usePermissions';

/**
 * PermissionRoute component - Protects routes based on user permissions
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - The component to render if permission is granted
 * @param {string} props.path - The route path to check permissions for (e.g., '/users')
 * @param {string} props.action - The action to check (default: 'view')
 * @param {React.ReactNode} props.fallback - Optional component to show if permission is denied (default: redirect to dashboard)
 * 
 * @example
 * <PermissionRoute path="/users" action="view">
 *   <UserManagement />
 * </PermissionRoute>
 * 
 * <PermissionRoute path="/users" action="create" fallback={<div>No permission</div>}>
 *   <CreateUserForm />
 * </PermissionRoute>
 */
const PermissionRoute = ({ children, path, action = 'view', fallback = null }) => {
  const perms = usePermissions();
  const hasPermission = perms && typeof perms.hasPermission === 'function' ? perms.hasPermission : null;
  const location = useLocation();

  // Check if user has the required permission (safe call)
  const hasAccess = hasPermission ? hasPermission(path, action) : false;

  if (!hasAccess) {
    // If fallback is provided, render it
    if (fallback) {
      return <>{fallback}</>;
    }
    
    // Otherwise, redirect to dashboard with a message
    // You could also show an "Access Denied" page here
    return <Navigate to="/" replace state={{ from: location, message: 'You do not have permission to access this page' }} />;
  }

  return <>{children}</>;
};

PermissionRoute.propTypes = {
  children: PropTypes.node,
  path: PropTypes.string.isRequired,
  action: PropTypes.string,
  fallback: PropTypes.node,
};

PermissionRoute.defaultProps = {
  action: 'view',
  fallback: null,
};

export default PermissionRoute;

