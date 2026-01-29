import { useAuth } from '../context/AuthContext';

/**
 * Custom hook for checking user permissions
 * @returns {Object} Permission checking utilities
 * 
 * @example
 * const { hasPermission, canView, canCreate, canEdit, canDelete } = usePermissions();
 * 
 * // Check specific permission
 * if (hasPermission('/users', 'create')) {
 *   // Show create button
 * }
 * 
 * // Use convenience methods
 * if (canView('/users')) {
 *   // Show users page
 * }
 */
export const usePermissions = () => {
  const { hasPermission: checkPermission, user, permissions } = useAuth();

  /**
   * Check if user has a specific permission
   * @param {string} path - The route path (e.g., '/users', '/roles')
   * @param {string} action - The action (e.g., 'view', 'create', 'edit', 'delete')
   * @returns {boolean}
   */
  const hasPermission = (path, action) => {
    return checkPermission(path, action);
  };

  /**
   * Check if user can view a route
   * @param {string} path - The route path
   * @returns {boolean}
   */
  const canView = (path) => {
    return checkPermission(path, 'view');
  };

  /**
   * Check if user can create in a route
   * @param {string} path - The route path
   * @returns {boolean}
   */
  const canCreate = (path) => {
    return checkPermission(path, 'create');
  };

  /**
   * Check if user can edit in a route
   * @param {string} path - The route path
   * @returns {boolean}
   */
  const canEdit = (path) => {
    return checkPermission(path, 'edit');
  };

  /**
   * Check if user can delete in a route
   * @param {string} path - The route path
   * @returns {boolean}
   */
  const canDelete = (path) => {
    return checkPermission(path, 'delete');
  };

  /**
   * Get all permissions for a specific route
   * @param {string} path - The route path
   * @returns {Object|null} Object with all permissions for the route, or null if no permissions
   */
  const getRoutePermissions = (path) => {
    if (user?.is_superadmin) {
      // Return all permissions as true for superadmin
      return {
        view: true,
        create: true,
        edit: true,
        delete: true,
        assign: true,
        approve: true,
        block: true,
        refund: true,
        reply: true,
        resolve: true,
        send: true
      };
    }
    
    return permissions?.[path] || null;
  };

  /**
   * Check if user has any permission for a route
   * @param {string} path - The route path
   * @returns {boolean}
   */
  const hasAnyPermission = (path) => {
    if (user?.is_superadmin) {
      return true;
    }
    
    const routePerms = permissions?.[path];
    if (!routePerms) {
      return false;
    }
    
    return Object.values(routePerms).some(val => val === true);
  };

  return {
    hasPermission,
    canView,
    canCreate,
    canEdit,
    canDelete,
    getRoutePermissions,
    hasAnyPermission,
    permissions,
    isSuperAdmin: user?.is_superadmin || false
  };
};

export default usePermissions;

