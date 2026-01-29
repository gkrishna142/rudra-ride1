import React, { useState, useEffect } from 'react';
import { FiSearch, FiPlus, FiEdit, FiTrash2, FiShield, FiArrowLeft, FiChevronDown } from 'react-icons/fi';
import { 
  FiHome, FiNavigation, FiUsers, FiUser, FiCreditCard, 
  FiTruck, FiMessageSquare, FiTag, FiBell, FiSettings,
  FiUserCheck, FiMap
} from 'react-icons/fi';
import api from '../api';
import './RolesPermissions.css';

const RolesPermissions = () => {
  const [showModal, setShowModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPage, setSelectedPage] = useState('');
  const [formPermissions, setFormPermissions] = useState({});
  const [defaultPage, setDefaultPage] = useState('/');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(null);
  const [roles, setRoles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);

  // All available pages/routes
  const pages = [
    { path: '/', label: 'Dashboard', icon: FiHome },
    { path: '/users', label: 'User Management', icon: FiUserCheck },
    { path: '/roles', label: 'Roles & Permissions', icon: FiShield },
    { path: '/rides', label: 'Ride Management', icon: FiNavigation },
    { path: '/drivers', label: 'Driver Management', icon: FiUsers },
    { path: '/customers', label: 'Customer Management', icon: FiUser },
    { path: '/zones', label: 'Zone Management', icon: FiMap },
    { path: '/payments', label: 'Payments & Transactions', icon: FiCreditCard },
    { path: '/vehicles', label: 'Vehicles Management', icon: FiTruck },
    { path: '/complaints', label: 'Complaints & Support', icon: FiMessageSquare },
    { path: '/promotions', label: 'Promotions & Coupons', icon: FiTag },
    { path: '/notifications', label: 'Notifications', icon: FiBell },
    { path: '/settings', label: 'Admin Settings', icon: FiSettings }
  ];

  // Standard permissions available for all pages
  const standardPermissions = ['view', 'create', 'edit', 'delete'];
  
  // Additional permissions specific to certain pages
  const pageSpecificPermissions = {
    '/': ['edit'],
    '/rides': ['assign'],
    '/drivers': ['approve'],
    '/customers': ['block'],
    '/payments': ['refund'],
    '/complaints': ['reply', 'resolve'],
    '/notifications': ['send'],
    '/settings': ['edit'],
    '/roles': ['create', 'edit', 'delete']
  };

  // Fetch roles and permissions from API
  useEffect(() => {
    const fetchRolesAndPermissions = async () => {
      setIsLoading(true);
      setFetchError(null);
      
      try {
        const [rolesResponse, permissionsResponse] = await Promise.all([
          api.get('/roles/'),
          api.get('/role-permissions/')
        ]);
        
        const rolesData = rolesResponse.data?.data || [];
        const permissionsData = permissionsResponse.data?.data || [];
        
        const permissionsByRole = {};
        permissionsData.forEach(perm => {
          const roleId = perm.role_id;
          const pagePath = perm.page_path;
          const permType = perm.permission_type;
          const isAllowed = perm.is_allowed === 'allowed' || perm.is_allowed === true;
          
          if (!permissionsByRole[roleId]) {
            permissionsByRole[roleId] = {};
          }
          
          if (!permissionsByRole[roleId][pagePath]) {
            permissionsByRole[roleId][pagePath] = {};
          }
          
          if (isAllowed) {
            permissionsByRole[roleId][pagePath][permType] = true;
          }
        });
        
        const combinedRoles = rolesData.map(role => {
          const roleId = role.role_id;
          const rolePermissions = permissionsByRole[roleId] || {};
          
          return {
            id: roleId,
            name: role.name || 'Unnamed Role',
            description: role.description || '',
            userCount: 0,
            defaultPage: role.default_page || '/',
            isActive: role.is_active || 'active',
            permissions: rolePermissions
          };
        });
        
        setRoles(combinedRoles);
      } catch (error) {
        console.error('Error fetching roles and permissions:', error);
        setFetchError(error.response?.data?.message || error.message || 'Failed to load roles and permissions');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchRolesAndPermissions();
  }, []);

  // Refresh data after successful role creation/update
  useEffect(() => {
    if (submitSuccess) {
      setTimeout(() => {
        const fetchRolesAndPermissions = async () => {
          try {
            const [rolesResponse, permissionsResponse] = await Promise.all([
              api.get('/roles/'),
              api.get('/role-permissions/')
            ]);
            
            const rolesData = rolesResponse.data?.data || [];
            const permissionsData = permissionsResponse.data?.data || [];
            
            const permissionsByRole = {};
            permissionsData.forEach(perm => {
              const roleId = perm.role_id;
              const pagePath = perm.page_path;
              const permType = perm.permission_type;
              const isAllowed = perm.is_allowed === 'allowed' || perm.is_allowed === true;
              
              if (!permissionsByRole[roleId]) {
                permissionsByRole[roleId] = {};
              }
              
              if (!permissionsByRole[roleId][pagePath]) {
                permissionsByRole[roleId][pagePath] = {};
              }
              
              if (isAllowed) {
                permissionsByRole[roleId][pagePath][permType] = true;
              }
            });
            
            const combinedRoles = rolesData.map(role => {
              const roleId = role.role_id;
              const rolePermissions = permissionsByRole[roleId] || {};
              
              return {
                id: roleId,
                name: role.name || 'Unnamed Role',
                description: role.description || '',
                userCount: 0,
                defaultPage: role.default_page || '/',
                isActive: role.is_active || 'active',
                permissions: rolePermissions
              };
            });
            
            setRoles(combinedRoles);
          } catch (error) {
            console.error('Error refreshing roles:', error);
          }
        };
        
        fetchRolesAndPermissions();
      }, 1000);
    }
  }, [submitSuccess]);

  const filteredRoles = roles.filter(role =>
    role.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    role.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getPermissionLabel = (permission) => {
    const labels = {
      view: 'View',
      create: 'Create',
      edit: 'Edit',
      delete: 'Delete',
      assign: 'Assign',
      approve: 'Approve',
      block: 'Block',
      refund: 'Refund',
      reply: 'Reply',
      resolve: 'Resolve',
      send: 'Send'
    };
    return labels[permission] || permission;
  };

  const getPagePermissions = (pagePath) => {
    const basePerms = [...standardPermissions];
    const specificPerms = pageSpecificPermissions[pagePath] || [];
    
    if (pagePath === '/') {
      return ['view', 'edit'];
    }
    
    const allPerms = [...new Set([...basePerms, ...specificPerms])];
    
    if (pagePath === '/settings') {
      return allPerms.filter(p => p !== 'create' && p !== 'delete');
    }
    
    return allPerms;
  };

  const getPageInfo = (pagePath) => {
    return pages.find(p => p.path === pagePath) || { path: pagePath, label: pagePath, icon: FiHome };
  };

  const handleEditRole = (role) => {
    setSelectedRole(role);
    setSelectedPage('');
    const copiedPermissions = {};
    Object.keys(role.permissions || {}).forEach(pagePath => {
      const existingPerms = role.permissions[pagePath] || {};
      const availablePerms = getPagePermissions(pagePath);
      const pagePermsObj = {};
      
      availablePerms.forEach(permType => {
        pagePermsObj[permType] = existingPerms[permType] === true;
      });
      
      copiedPermissions[pagePath] = pagePermsObj;
    });
    setFormPermissions(copiedPermissions);
    setDefaultPage(role.defaultPage || '/');
    setSubmitError(null);
    setSubmitSuccess(null);
    setShowModal(true);
  };

  const handleDeleteRole = async (role) => {
    const confirmMessage = `Are you sure you want to delete the role "${role.name}"?\n\nThis will also delete all permissions associated with this role. This action cannot be undone.`;
    
    if (!window.confirm(confirmMessage)) {
      return;
    }

    try {
      const response = await api.delete(`/role-permissions/${role.id}/`);
      
      if (response.data && response.data.message_type === 'success') {
        setSubmitSuccess(`Role "${role.name}" deleted successfully!`);
        
        setTimeout(() => {
          const fetchRolesAndPermissions = async () => {
            try {
              const [rolesResponse, permissionsResponse] = await Promise.all([
                api.get('/roles/'),
                api.get('/role-permissions/')
              ]);
              
              const rolesData = rolesResponse.data?.data || [];
              const permissionsData = permissionsResponse.data?.data || [];
              
              const permissionsByRole = {};
              permissionsData.forEach(perm => {
                const roleId = perm.role_id;
                const pagePath = perm.page_path;
                const permType = perm.permission_type;
                const isAllowed = perm.is_allowed === 'allowed' || perm.is_allowed === true;
                
                if (!permissionsByRole[roleId]) {
                  permissionsByRole[roleId] = {};
                }
                
                if (!permissionsByRole[roleId][pagePath]) {
                  permissionsByRole[roleId][pagePath] = {};
                }
                
                if (isAllowed) {
                  permissionsByRole[roleId][pagePath][permType] = true;
                }
              });
              
              const combinedRoles = rolesData.map(role => {
                const roleId = role.role_id;
                const rolePermissions = permissionsByRole[roleId] || {};
                
                return {
                  id: roleId,
                  name: role.name || 'Unnamed Role',
                  description: role.description || '',
                  userCount: 0,
                  defaultPage: role.default_page || '/',
                  isActive: role.is_active || 'active',
                  permissions: rolePermissions
                };
              });
              
              setRoles(combinedRoles);
              setSubmitSuccess(null);
            } catch (error) {
              console.error('Error refreshing roles:', error);
              setSubmitError('Role deleted but failed to refresh the list. Please reload the page.');
            }
          };
          
          fetchRolesAndPermissions();
        }, 1000);
      } else {
        throw new Error(response.data?.message || 'Failed to delete role');
      }
    } catch (error) {
      console.error('Error deleting role:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.error ||
                          error.message || 
                          'Failed to delete role. Please try again.';
      setSubmitError(errorMessage);
      setTimeout(() => setSubmitError(null), 5000);
    }
  };

  const handleCreateRole = () => {
    setSelectedRole(null);
    setSelectedPage('');
    setFormPermissions({});
    setDefaultPage('/');
    setSubmitError(null);
    setSubmitSuccess(null);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedPage('');
    setFormPermissions({});
    setDefaultPage('/');
    setSubmitError(null);
    setSubmitSuccess(null);
    setIsSubmitting(false);
  };

  const handlePermissionChange = (pagePath, permission, checked) => {
    setFormPermissions(prev => {
      const newPerms = { ...prev };
      if (!newPerms[pagePath]) {
        const availablePerms = getPagePermissions(pagePath);
        newPerms[pagePath] = {};
        availablePerms.forEach(perm => {
          newPerms[pagePath][perm] = false;
        });
      }
      newPerms[pagePath] = {
        ...newPerms[pagePath],
        [permission]: checked === true
      };
      return newPerms;
    });
  };

  const handleToggleAllPagePermissions = (pagePath, checked) => {
    const pagePerms = getPagePermissions(pagePath);
    const newPerms = {};
    pagePerms.forEach(perm => {
      newPerms[perm] = checked;
    });
    
    setFormPermissions(prev => ({
      ...prev,
      [pagePath]: newPerms
    }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(null);
    
    try {
      const formData = new FormData(e.target);
      const roleName = formData.get('roleName') || selectedRole?.name || '';
      const roleDescription = formData.get('roleDescription') || selectedRole?.description || '';
      
      const cleanedPermissions = {};
      Object.keys(formPermissions).forEach(pagePath => {
        const pagePerms = formPermissions[pagePath] || {};
        const availablePerms = getPagePermissions(pagePath);
        const cleanedPagePerms = {};
        
        availablePerms.forEach(permType => {
          cleanedPagePerms[permType] = pagePerms[permType] === true;
        });
        
        cleanedPermissions[pagePath] = cleanedPagePerms;
      });
      
      console.log('📤 Final permissions payload:', JSON.stringify(cleanedPermissions, null, 2));
      
      const payload = {
        name: roleName,
        description: roleDescription || '',
        defaultPage: defaultPage,
        permissions: cleanedPermissions
      };
      
      console.log('Submitting role data:', payload);
      
      let response;
      if (selectedRole) {
        response = await api.put(`/role-permissions/${selectedRole.id}/`, payload);
      } else {
        response = await api.post('/role-permissions/', payload);
      }
      
      if (response.data && response.data.message_type === 'success') {
        setSubmitSuccess(selectedRole ? 'Role updated successfully!' : 'Role created successfully!');
        
        setTimeout(() => {
          handleCloseModal();
        }, 2000);
      } else {
        throw new Error(response.data?.message || 'Failed to save role');
      }
    } catch (error) {
      console.error('Error submitting role:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.error ||
                          (error.response?.data?.errors ? JSON.stringify(error.response.data.errors) : null) ||
                          error.message || 
                          'Failed to save role. Please try again.';
      setSubmitError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (showModal) {
    return (
      <div className="roles-permissions-form-page">
        <div className="form-page-header">
          <button className="btn-back" onClick={handleCloseModal}>
            <FiArrowLeft /> Back to Roles
          </button>
          <h1>{selectedRole ? 'Edit Role' : 'Create New Role'}</h1>
          <p className="form-subtitle">
            {selectedRole 
              ? 'Update role details and permissions below' 
              : 'Fill in the role information and configure permissions for each page'}
          </p>
        </div>

        <form onSubmit={handleFormSubmit} className="role-form">
          <div className="form-section">
            <h2>Role Information</h2>
            <div className="form-row">
              <div className="form-group">
                <label>Role Name <span className="required">*</span></label>
                <input 
                  type="text" 
                  name="roleName"
                  defaultValue={selectedRole?.name || ''}
                  placeholder="e.g., Manager, Support Staff, Moderator"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea 
                  name="roleDescription"
                  rows="3"
                  defaultValue={selectedRole?.description || ''}
                  placeholder="Describe the role and its responsibilities..."
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Default Page <span className="required">*</span></label>
                <p className="field-help-text">The page users with this role will see first after login</p>
                <div className="dropdown-wrapper">
                  <select
                    value={defaultPage}
                    onChange={(e) => setDefaultPage(e.target.value)}
                    className="page-select-dropdown"
                    required
                  >
                    {pages.map((page) => (
                      <option key={page.path} value={page.path}>
                        {page.label}
                      </option>
                    ))}
                  </select>
                  <FiChevronDown className="dropdown-arrow" />
                </div>
              </div>
            </div>
          </div>

          <div className="form-section permissions-section-full">
            <div className="section-header-with-help">
              <div>
                <h2>Page Permissions</h2>
                <p className="help-text">Click on any page card below to configure its permissions. Pages with configured permissions will be highlighted in green.</p>
              </div>
            </div>

            <div className="pages-grid-container">
              {pages.map((page) => {
                const pagePerms = formPermissions[page.path] || {};
                const hasAnyPermission = Object.values(pagePerms).some(v => v === true);
                const enabledPermsCount = Object.entries(pagePerms).filter(([_, v]) => v).length;
                const totalPermsCount = getPagePermissions(page.path).length;
                const Icon = page.icon;
                const isSelected = selectedPage === page.path;
                
                return (
                  <div 
                    key={page.path} 
                    className={`page-card ${isSelected ? 'selected' : ''} ${hasAnyPermission ? 'has-permissions' : ''}`}
                    onClick={() => {
                      const newSelectedPage = isSelected ? '' : page.path;
                      setSelectedPage(newSelectedPage);
                      
                      if (newSelectedPage) {
                        setFormPermissions(prev => {
                          if (!prev[newSelectedPage]) {
                            const availablePerms = getPagePermissions(newSelectedPage);
                            const initialPerms = {};
                            availablePerms.forEach(perm => {
                              initialPerms[perm] = false;
                            });
                            return {
                              ...prev,
                              [newSelectedPage]: initialPerms
                            };
                          }
                          return prev;
                        });
                      }
                    }}
                  >
                    <div className="page-card-header">
                      <div className="page-card-icon">
                        <Icon />
                      </div>
                      <div className="page-card-info">
                        <h4>{page.label}</h4>
                        {hasAnyPermission && (
                          <span className="permission-badge">
                            {enabledPermsCount} / {totalPermsCount} enabled
                          </span>
                        )}
                      </div>
                      {hasAnyPermission && (
                        <div className="permission-indicator"></div>
                      )}
                    </div>
                    
                    {isSelected && (
                      <div className="page-permissions-expanded">
                        <div className="permissions-controls">
                          <label className="toggle-all-permissions">
                            <input 
                              type="checkbox" 
                              checked={getPagePermissions(page.path).every(
                                perm => pagePerms[perm] === true
                              )}
                              onChange={(e) => {
                                handleToggleAllPagePermissions(page.path, e.target.checked);
                              }}
                            />
                            <span>Enable All Permissions</span>
                          </label>
                        </div>
                        <div className="permissions-grid-expanded">
                          {getPagePermissions(page.path).map((perm) => {
                            const currentValue = pagePerms[perm] === true;
                            return (
                              <label key={perm} className="permission-item-expanded">
                                <input 
                                  type="checkbox" 
                                  checked={currentValue}
                                  onChange={(e) => {
                                    handlePermissionChange(page.path, perm, e.target.checked);
                                  }}
                                />
                                <span className="permission-label">{getPermissionLabel(perm)}</span>
                                <span className="permission-description">
                                  {perm === 'view' && 'Can view this page'}
                                  {perm === 'create' && 'Can create new items'}
                                  {perm === 'edit' && 'Can edit existing items'}
                                  {perm === 'delete' && 'Can delete items'}
                                  {perm === 'assign' && 'Can assign rides to drivers'}
                                  {perm === 'approve' && 'Can approve drivers'}
                                  {perm === 'block' && 'Can block/unblock users'}
                                  {perm === 'refund' && 'Can process refunds'}
                                  {perm === 'reply' && 'Can reply to complaints'}
                                  {perm === 'resolve' && 'Can resolve complaints'}
                                  {perm === 'send' && 'Can send notifications'}
                                </span>
                              </label>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {Object.keys(formPermissions).length > 0 && (
              <div className="permissions-summary">
                <h4>📋 Permissions Summary</h4>
                <div className="summary-stats">
                  <div className="summary-item">
                    <span className="summary-label">Pages Configured:</span>
                    <span className="summary-value">
                      {Object.keys(formPermissions).filter(path => 
                        Object.values(formPermissions[path] || {}).some(v => v === true)
                      ).length} / {pages.length}
                    </span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Total Permissions:</span>
                    <span className="summary-value">
                      {Object.values(formPermissions).reduce((total, perms) => 
                        total + Object.values(perms || {}).filter(v => v === true).length, 0
                      )}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {submitSuccess && (
            <div className="alert alert-success">
              <span>✓</span> {submitSuccess}
            </div>
          )}
          {submitError && (
            <div className="alert alert-error">
              <span>✗</span> {submitError}
            </div>
          )}

          <div className="form-actions">
            <button 
              type="button" 
              className="btn-secondary" 
              onClick={handleCloseModal}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>⏳ {selectedRole ? 'Updating...' : 'Creating...'}</>
              ) : (
                <>{selectedRole ? 'Update Role' : 'Create Role'}</>
              )}
            </button>
          </div>
        </form>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="roles-permissions">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading roles and permissions...</p>
        </div>
      </div>
    );
  }

  if (fetchError) {
    return (
      <div className="roles-permissions">
        <div className="error-state">
          <h3>Error loading data</h3>
          <p>{fetchError}</p>
          <button className="btn-primary-modern" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="roles-permissions">
      <div className="page-header-modern">
        <div className="header-content">
          <div className="header-text">
            <h1>Roles & Permissions</h1>
            <p className="header-subtitle">Manage user roles and their access permissions across the platform</p>
          </div>
          <button className="btn-primary-modern" onClick={handleCreateRole}>
            <FiPlus /> Create New Role
          </button>
        </div>
      </div>

      {submitSuccess && (
        <div className="alert alert-success">
          <span>✓</span> {submitSuccess}
        </div>
      )}
      {submitError && (
        <div className="alert alert-error">
          <span>✗</span> {submitError}
        </div>
      )}

      <div className="stats-overview">
        <div className="stat-card">
          <div className="stat-icon users">
            <FiUsers />
          </div>
          <div className="stat-content">
            <span className="stat-number">{roles.length}</span>
            <span className="stat-label">Total Roles</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon total-users">
            <FiUserCheck />
          </div>
          <div className="stat-content">
            <span className="stat-number">
              {roles.reduce((sum, role) => sum + role.userCount, 0)}
            </span>
            <span className="stat-label">Total Users</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon pages">
            <FiShield />
          </div>
          <div className="stat-content">
            <span className="stat-number">{pages.length}</span>
            <span className="stat-label">Available Pages</span>
          </div>
        </div>
      </div>

      <div className="filters-section-modern">
        <div className="search-box-modern">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search roles by name or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <span className="search-results">
              {filteredRoles.length} {filteredRoles.length === 1 ? 'role' : 'roles'} found
            </span>
          )}
        </div>
      </div>

      {filteredRoles.length === 0 ? (
        <div className="empty-state">
          <FiShield className="empty-icon" />
          <h3>No roles found</h3>
          <p>Try adjusting your search terms or create a new role</p>
          <button className="btn-primary-modern" onClick={handleCreateRole}>
            <FiPlus /> Create Your First Role
          </button>
        </div>
      ) : (
        <div className="roles-grid-modern">
          {filteredRoles.map((role) => {
            const totalPermissions = Object.values(role.permissions).reduce(
              (total, perms) => total + Object.values(perms).filter(v => v === true).length,
              0
            );
            const pagesWithAccess = Object.keys(role.permissions).filter(path =>
              Object.values(role.permissions[path] || {}).some(v => v === true)
            ).length;
            
            return (
              <div key={role.id} className="role-card-modern">
                <div className="role-card-header-modern">
                  <div className="role-badge">
                    <FiShield />
                  </div>
                  <div className="role-title-info">
                    <h3>{role.name}</h3>
                    <div className="role-badges">
                      <span className="role-id-badge">{role.id}</span>
                      <span className={`status-badge ${role.isActive === 'active' ? 'status-active' : 'status-inactive'}`}>
                        {role.isActive === 'active' ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                  <div className="role-actions-modern">
                    <button 
                      className="btn-action-edit" 
                      onClick={() => handleEditRole(role)}
                      title="Edit Role"
                    >
                      <FiEdit />
                    </button>
                    {role.name !== 'Super Admin' && (
                      <button 
                        className="btn-action-delete" 
                        onClick={() => handleDeleteRole(role)}
                        title="Delete Role"
                      >
                        <FiTrash2 />
                      </button>
                    )}
                  </div>
                </div>

                <p className="role-description-modern">{role.description}</p>
                
                <div className="role-metrics">
                  <div className="metric-item">
                    <div className="metric-icon">
                      <FiUsers />
                    </div>
                    <div className="metric-content">
                      <span className="metric-value">{role.userCount}</span>
                      <span className="metric-label">Users</span>
                    </div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-icon">
                      <FiShield />
                    </div>
                    <div className="metric-content">
                      <span className="metric-value">{pagesWithAccess}</span>
                      <span className="metric-label">Pages</span>
                    </div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-icon">
                      <FiShield />
                    </div>
                    <div className="metric-content">
                      <span className="metric-value">{totalPermissions}</span>
                      <span className="metric-label">Permissions</span>
                    </div>
                  </div>
                </div>

                <div className="default-page-badge">
                  <span className="badge-label">Default Page:</span>
                  <span className="badge-value">
                    {(() => {
                      const defaultPageInfo = getPageInfo(role.defaultPage || '/');
                      const DefaultIcon = defaultPageInfo.icon;
                      return (
                        <span className="default-page-content">
                          <DefaultIcon /> {defaultPageInfo.label}
                        </span>
                      );
                    })()}
                  </span>
                </div>

                <div className="permissions-preview-modern">
                  <div className="permissions-header">
                    <h4>Page Access</h4>
                    <span className="permissions-count">{pagesWithAccess} pages</span>
                  </div>
                  <div className="permissions-list-modern">
                    {Object.entries(role.permissions).slice(0, 5).map(([pagePath, perms]) => {
                      const pageInfo = getPageInfo(pagePath);
                      const hasPermission = Object.values(perms).some(v => v === true);
                      if (!hasPermission) return null;
                      const Icon = pageInfo.icon;
                      const permCount = Object.entries(perms).filter(([_, v]) => v).length;
                      return (
                        <div key={pagePath} className="permission-item-modern">
                          <div className="permission-icon-wrapper">
                            <Icon />
                          </div>
                          <div className="permission-info">
                            <span className="permission-name">{pageInfo.label}</span>
                            <span className="permission-count-badge">{permCount} perms</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  {Object.keys(role.permissions).filter(path =>
                    Object.values(role.permissions[path] || {}).some(v => v === true)
                  ).length > 5 && (
                    <div className="more-permissions">
                      +{Object.keys(role.permissions).filter(path =>
                        Object.values(role.permissions[path] || {}).some(v => v === true)
                      ).length - 5} more pages
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RolesPermissions;
