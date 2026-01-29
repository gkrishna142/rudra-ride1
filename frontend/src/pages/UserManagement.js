import React, { useEffect, useState } from 'react';
import {
  FiSearch, FiPlus, FiEye, FiEdit, FiX, FiCheck,
  FiUser, FiMail, FiUserPlus
} from 'react-icons/fi';
import api from '../api';
import { usePermissions } from '../hooks/usePermissions';
import './UserManagement.css';

const UserManagement = () => {
  const { canCreate, canEdit, canDelete } = usePermissions();
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [roles, setRoles] = useState([]);
  const [loadingRoles, setLoadingRoles] = useState(false);

  //  FORM STATE 
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone_number: '',
    password: '',
    confirm_password: '',
    role: '', // stores ROLE ID
  });

  // FETCH USERS

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await api.get('users/');
      setUsers(Array.isArray(response.data.data) ? response.data.data : []);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      // Don't show alert for 401 - the interceptor handles it
      if (error.response?.status !== 401 && error.response?.data) {
        alert(`Error: ${error.response.data.error || error.response.data.message || 'Failed to fetch users'}`);
      } else if (error.response?.status !== 401) {
        alert('Failed to fetch users. Please check your connection and try again.');
      }
      // 401 errors are handled by the API interceptor (token refresh or redirect)
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  /*  FILTER USERS  */
  const filteredUsers = users.filter(user => {
    const name = user.name || '';
    const email = user.email || '';
    const phone = user.phone_number || '';
    const id = user.id ? user.id.toString() : '';

    const matchesSearch =
      name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      phone.includes(searchTerm) ||
      id.includes(searchTerm);

    const matchesFilter =
      filter === 'all'
        ? true
        : filter === 'active'
        ? user.is_active
        : !user.is_active;

    return matchesSearch && matchesFilter;
  });

  /*  HANDLERS  */
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    const { name, email, password, confirm_password, role } = formData;

    if (!name || !email || !password || !confirm_password || !role) {
      alert('Please fill all required fields');
      return false;
    }

    // Validate phone number format if provided (optional field)
    // Indian phone numbers: 10 digits, can start with 6-9
    if (formData.phone_number) {
      const phoneDigits = formData.phone_number.replace(/\D/g, ''); // Remove all non-digits
      if (phoneDigits.length !== 10 || !/^[6-9]/.test(phoneDigits)) {
        alert('Please enter a valid 10-digit Indian phone number (starting with 6-9)');
        return false;
      }
    }

    if (!/^[a-zA-Z\s]+$/.test(name)) {
      alert('Name should only contain letters and spaces');
      return false;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      alert('Invalid email address');
      return false;
    }

    if (password !== confirm_password) {
      alert('Passwords do not match');
      return false;
    }

    if (password.length < 6) {
      alert('Password must be at least 6 characters');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      // Validate role_id is selected (should be a string like "R001", "R003", etc.)
      if (!formData.role || formData.role.trim() === '') {
        alert('Please select a valid role.');
        setIsSubmitting(false);
        return;
      }
      
      // Format phone number with India code (+91)
      let phoneNumber = formData.phone_number ? formData.phone_number.replace(/\D/g, '') : null;
      if (phoneNumber && phoneNumber.length === 10) {
        phoneNumber = `+91${phoneNumber}`;
      }
      // If phoneNumber doesn't have exactly 10 digits, keep it as is (already set above)

      const response = await api.post('users/', {
        name: formData.name,
        email: formData.email,
        phone_number: phoneNumber,
        password: formData.password,
        confirm_password: formData.confirm_password,
        role_id: formData.role, // Send role_id as string (e.g., "R001", "R003", "R_ADMIN")
      });

      // Show success message with email status
      let successMessage = 'User created successfully!';
      
      // Always check and display email status
      if (response.data.email_sent !== undefined) {
        if (response.data.email_sent) {
          successMessage = `User created successfully!\n\n✅ ${response.data.email_message || `Email has been sent to ${formData.email}`}`;
        } else {
          // Show detailed error message if email failed
          const emailError = response.data.email_message || 'Email could not be sent. Please check email configuration in backend.';
          successMessage = `User created successfully!\n\n⚠️ Email Status: ${emailError}\n\nNote: User account was created, but email notification failed.`;
        }
      } else {
        // If email_sent is not in response, assume email was attempted
        successMessage = `User created successfully!\n\nℹ️ Email status unknown. Please check backend logs.`;
      }
      
      alert(successMessage);
      setShowForm(false);
      fetchUsers();
      setFormData({
        name: '',
        email: '',
        phone_number: '',
        password: '',
        confirm_password: '',
        role: '',
      });
    } catch (error) {
      console.error('Error creating user:', error);
      if (error.response?.data) {
        const errorData = error.response.data;
        // Handle different error formats
        let errorMessage = 'Failed to create user';
        
        if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.errors) {
          // Handle validation errors
          const errorMessages = Object.entries(errorData.errors)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join('\n');
          errorMessage = errorMessages;
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
        
        alert(`Error: ${errorMessage}`);
      } else {
        alert('Failed to create user. Please check your connection and try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };
    const fetchRoles = async () => {
  setLoadingRoles(true);
  try {
    const response = await api.get('roles/basic/');

    console.log('Roles API response:', response.data);

    // Parse the response - API returns { message_type, count, data: [...] }
    const rolesData = response.data?.data || [];

    setRoles(
      rolesData.map(role => ({
        role_id: role.role_id,
        role_name: role.role_name,
      }))
    );
  } catch (error) {
    console.error('Failed to fetch roles:', error);
    alert('Failed to fetch roles. Please try again.');
  } finally {
    setLoadingRoles(false);
  }
};



        // Fetch roles when form modal opens
        useEffect(() => {
          if (showForm && roles.length === 0 && !loadingRoles) {
            fetchRoles();
          }
          // eslint-disable-next-line react-hooks/exhaustive-deps
        }, [showForm]);

  return (
 
      <div className="user-management">
      <div className="page-header">
        <h1>User Management</h1>
           {canCreate('/users') && (
             <button className="btn-primary" onClick={() => setShowForm(true)}> 
               <FiPlus /> Add New User
             </button>
           )}
          </div>
      {/* ADD USER MODAL  */}
      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="header-icon-box">
                <FiUserPlus />
              </div>
              <h3>Add New User</h3>
              <button className="close-btn" onClick={() => setShowForm(false)} aria-label="Close">
                <FiX />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="user-form">
              <div className="form-group">
                <label htmlFor="name">Full Name <span className="required">*</span></label>
                <input 
                  id="name"
                  name="name" 
                  type="text"
                  placeholder="Enter full name"
                  value={formData.name} 
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address <span className="required">*</span></label>
                <input 
                  id="email"
                  name="email" 
                  type="email"
                  placeholder="user@example.com"
                  value={formData.email} 
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone_number">Phone Number</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ 
                    padding: '0.75rem', 
                    background: '#f8f9fa', 
                    border: '1px solid #dee2e6', 
                    borderRadius: '6px',
                    color: '#495057',
                    fontWeight: '500',
                    fontSize: '0.875rem',
                    whiteSpace: 'nowrap'
                  }}>+91</span>
                  <input 
                    id="phone_number"
                    name="phone_number" 
                    type="tel"
                    placeholder="9876543210"
                    value={formData.phone_number} 
                    onChange={handleInputChange}
                    style={{ flex: 1 }}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="password">Password <span className="required">*</span></label>
                <input 
                  id="password"
                  type="password" 
                  name="password" 
                  placeholder="Minimum 6 characters"
                  value={formData.password} 
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirm_password">Confirm Password <span className="required">*</span></label>
                <input 
                  id="confirm_password"
                  type="password" 
                  name="confirm_password" 
                  placeholder="Re-enter password"
                  value={formData.confirm_password} 
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="role">User Role <span className="required">*</span></label>
                <select
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">
                    {loadingRoles ? 'Loading roles...' : 'Select a role'}
                  </option>
                  {roles.map(role => (
                    <option key={role.role_id} value={role.role_id}>
                      {role.role_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-actions">
                <button 
                  type="button" 
                  className="btn-cancel" 
                  onClick={() => setShowForm(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn-submit" 
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <span className="spinner"></span>
                      Creating...
                    </>
                  ) : (
                    <>
                      <FiUserPlus />
                      Create User
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

       {/* Filter */}

       <div className="filters-section">
         <div className="search-box">
           <FiSearch className="search-icon" />
           <input 
             type="text" 
             placeholder="Search by name, email, phone, or user ID..." 
             value={searchTerm} 
             onChange={e => setSearchTerm(e.target.value)} 
           />
         </div>
         <div className="filter-section">
           <label>Status:</label>
           <div className="filter-buttons">
             <button 
               className={filter === 'all' ? 'active' : ''} 
               onClick={() => setFilter('all')}
             >
               All Users
             </button>
             <button 
               className={filter === 'active' ? 'active' : ''} 
               onClick={() => setFilter('active')}
             >
               Active
             </button>
             <button 
               className={filter === 'blocked' ? 'active' : ''} 
               onClick={() => setFilter('blocked')}
             >
               Blocked
             </button>
           </div>
         </div>
         {!loading && (
           <div className="results-count">
             <span className="count-number">{filteredUsers.length}</span>
             <span className="count-label">
               {filteredUsers.length === 1 ? 'user' : 'users'} found
             </span>
           </div>
         )}
      </div>

      {/* USERS TABLE */}
      {loading ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading users...</p>
        </div>
      ) : filteredUsers.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <FiUser />
          </div>
          <h3>No Users Found</h3>
          <p>
            {searchTerm || filter !== 'all'
              ? 'Try adjusting your search or filter criteria to find users.'
              : 'Get started by adding your first user to the system.'}
          </p>
        </div>
      ) : (
        <div className="users-table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(user => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>
                    <FiUser /> {user.name}
                  </td>
                  <td>
                    <FiMail /> {user.email}
                  </td>
                  <td>
                    {user.role_name}
                  </td>
                  <td>
                    <span className={`status-badge ${user.is_active ? 'status-active' : 'status-blocked'}`}>
                      {user.is_active ? 'Active' : 'Blocked'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button className="btn-icon" title="View Details">
                        <FiEye />
                      </button>
                      {canEdit('/users') && (
                        <button className="btn-icon" title="Edit User">
                          <FiEdit />
                        </button>
                      )}
                      {canDelete('/users') && (
                        <>
                          {user.is_active ? (
                            <button className="btn-icon btn-danger" title="Block User">
                              <FiX />
                            </button>
                          ) : (
                            <button className="btn-icon btn-success" title="Unblock User">
                              <FiCheck />
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default UserManagement;

