import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is logged in on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    const storedPermissions = localStorage.getItem('permissions');
    
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
    }
    
    if (storedPermissions) {
      try {
        setPermissions(JSON.parse(storedPermissions));
      } catch (e) {
        console.error('Error parsing stored permissions:', e);
      }
    }
    
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('admin/login/', {
        email,
        password,
      });

      // Extract JWT token, user data, and permissions from response
      const { message_type, tokens, user: userData, permissions: permissionsData } = response.data;
      
      // Check message_type and store JWT token and user data
      if (message_type === 'success' && tokens && tokens.access) {
        localStorage.setItem('token', tokens.access);
        if (tokens.refresh) {
          localStorage.setItem('refresh_token', tokens.refresh);
        }
        
        // Store user data exactly as received from backend
        const user = {
          id: userData.id,
          name: userData.name,
          username: userData.username,
          email: userData.email,
          role_id: userData.role_id,
          role_name: userData.role_name,
          is_superadmin: userData.is_superadmin,
          is_active: userData.is_active
        };
        
        localStorage.setItem('user', JSON.stringify(user));
        setUser(user);
        
        // Store permissions if available
        if (permissionsData) {
          localStorage.setItem('permissions', JSON.stringify(permissionsData));
          setPermissions(permissionsData);
        }
        
        return { success: true, user, permissions: permissionsData };
      } else {
        return { success: false, error: 'No token received from server' };
      }
    } catch (error) {
      // Handle error response
      const responseData = error.response?.data;
      
      // Check if error has message_type
      if (responseData?.message_type === 'error') {
        return { success: false, error: 'Please enter valid email or password' };
      }
      
      const errorMessage = responseData?.error || 
                          responseData?.message || 
                          responseData?.detail ||
                          error.message || 
                          'Login failed. Please try again.';
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('permissions');
    setUser(null);
    setPermissions(null);
  };

  const sendOTP = async (email) => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/auth/send-otp', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email }),
      // });
      // const data = await response.json();
      
      // Simulated OTP sending for now
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Store OTP in sessionStorage for verification (in production, this would be on the backend)
      const mockOTP = Math.floor(100000 + Math.random() * 900000).toString();
      sessionStorage.setItem('otp', mockOTP);
      sessionStorage.setItem('otpExpiry', (Date.now() + 600000).toString()); // 10 minutes
      
      console.log('Mock OTP for testing:', mockOTP); // Remove in production
      
      return { success: true, message: 'OTP sent successfully' };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const verifyOTP = async (email, otp) => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/auth/verify-otp', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, otp }),
      // });
      // const data = await response.json();
      
      // Simulated OTP verification for now
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const storedOTP = sessionStorage.getItem('otp');
      const otpExpiry = sessionStorage.getItem('otpExpiry');
      
      if (!storedOTP || !otpExpiry) {
        return { success: false, error: 'OTP expired or invalid. Please request a new OTP.' };
      }
      
      if (Date.now() > parseInt(otpExpiry)) {
        sessionStorage.removeItem('otp');
        sessionStorage.removeItem('otpExpiry');
        return { success: false, error: 'OTP has expired. Please request a new OTP.' };
      }
      
      if (storedOTP !== otp) {
        return { success: false, error: 'Invalid OTP. Please try again.' };
      }
      
      // OTP verified successfully
      sessionStorage.setItem('otpVerified', 'true');
      
      return { success: true, message: 'OTP verified successfully' };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const resetPassword = async (email, newPassword) => {
    try {
      // Check if OTP was verified
      const otpVerified = sessionStorage.getItem('otpVerified');
      if (otpVerified !== 'true') {
        return { success: false, error: 'Please verify OTP first' };
      }
      
      // TODO: Replace with actual API call
      // const response = await fetch('/api/auth/reset-password', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, newPassword }),
      // });
      // const data = await response.json();
      
      // Simulated password reset for now
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Clear OTP data
      sessionStorage.removeItem('otp');
      sessionStorage.removeItem('otpExpiry');
      sessionStorage.removeItem('otpVerified');
      
      return { success: true, message: 'Password reset successfully' };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  // Helper function to check permissions
  const hasPermission = (path, action) => {
    // Superadmin has all permissions
    if (user?.is_superadmin) {
      return true;
    }
    
    // If no permissions data, deny access
    if (!permissions) {
      return false;
    }
    
    // Check if path exists in permissions
    const pathPermissions = permissions[path];
    if (!pathPermissions) {
      return false;
    }
    
    // Check if action is allowed
    return pathPermissions[action] === true;
  };

  const value = {
    user,
    setUser,
    permissions,
    setPermissions,
    login,
    logout,
    sendOTP,
    verifyOTP,
    resetPassword,
    hasPermission,
    isAuthenticated: !!user,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

