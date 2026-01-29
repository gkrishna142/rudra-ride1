/**
 * Example: How to create a role with permissions using Axios
 * 
 * Endpoint: POST /api/role-permissions/
 * or: POST /api/auth/role-permissions/
 */

import axios from 'axios';

// Base URL - adjust according to your setup
const API_BASE_URL = 'http://localhost:8000/api'; // or your production URL

// Example 1: Create a role with permissions
const createRoleWithPermissions = async (token) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/role-permissions/`,
      {
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
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` // Add token if authentication required
        }
      }
    );
    
    console.log('✅ Role created successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Error creating role:', error.response?.data || error.message);
    throw error;
  }
};

// Example 2: Create a Super Admin role with full permissions
const createSuperAdminRole = async (token) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/role-permissions/`,
      {
        name: "Super Admin",
        description: "Full access to all features and settings",
        defaultPage: "/",
        permissions: {
          "/": {
            "view": true,
            "edit": true
          },
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
          },
          "/drivers": {
            "view": true,
            "create": true,
            "edit": true,
            "delete": true,
            "approve": true
          },
          "/customers": {
            "view": true,
            "create": true,
            "edit": true,
            "delete": true,
            "block": true
          },
          "/payments": {
            "view": true,
            "create": true,
            "edit": true,
            "delete": true,
            "refund": true
          },
          "/vehicles": {
            "view": true,
            "create": true,
            "edit": true,
            "delete": true
          },
          "/complaints": {
            "view": true,
            "create": true,
            "edit": true,
            "delete": true,
            "reply": true,
            "resolve": true
          },
          "/promotions": {
            "view": true,
            "create": true,
            "edit": true,
            "delete": true
          },
          "/notifications": {
            "view": true,
            "create": true,
            "edit": true,
            "delete": true,
            "send": true
          },
          "/settings": {
            "view": true,
            "edit": true
          },
          "/roles": {
            "view": true,
            "create": true,
            "edit": true,
            "delete": true
          },
          "/zones": {
            "view": true,
            "create": true,
            "edit": true,
            "delete": true
          }
        }
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    console.log('✅ Super Admin role created:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
    throw error;
  }
};

// Example 3: Create a Support role with limited permissions
const createSupportRole = async (token) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/role-permissions/`,
      {
        name: "Support",
        description: "Can view and respond to complaints only",
        defaultPage: "/complaints",
        permissions: {
          "/": {
            "view": true
          },
          "/complaints": {
            "view": true,
            "reply": true
          },
          "/rides": {
            "view": true
          },
          "/drivers": {
            "view": true
          },
          "/customers": {
            "view": true
          }
        }
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    console.log('✅ Support role created:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
    throw error;
  }
};

// Example 4: Using in React component
const RoleForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    defaultPage: '/',
    permissions: {}
  });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token'); // Get token from storage
      const response = await createRoleWithPermissions(token);
      
      // Handle success
      alert('Role created successfully!');
      console.log('Role ID:', response.data.role.role_id);
      
    } catch (error) {
      // Handle error
      if (error.response?.data?.errors) {
        console.error('Validation errors:', error.response.data.errors);
      } else {
        console.error('Error:', error.message);
      }
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};

// Export functions for use in other files
export {
  createRoleWithPermissions,
  createSuperAdminRole,
  createSupportRole
};

