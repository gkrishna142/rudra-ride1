import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import Toast from '../components/Toast';
import { FiMail, FiLock, FiLogIn, FiAlertCircle } from 'react-icons/fi';
import './Login.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [toast, setToast] = useState(null);
  const { isAuthenticated, setUser, setPermissions } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!email || !password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    try {
      // Make POST request to admin/login/ endpoint
      const response = await api.post('admin/login/', {
        email,
        password,
      });

      // Check message_type from response
      const { message_type, tokens, user: userData, permissions: permissionsData } = response.data;

      // Handle success response
      if (message_type === 'success') {
        // Show success toast
        setToast({
          message: 'Login successful! Redirecting...',
          type: 'success'
        });

        // Store JWT token and user data
        if (tokens && tokens.access) {
          // Store access token in localStorage (ensure it's a string, not an object)
          let accessToken = tokens.access;
          if (typeof accessToken !== 'string') {
            accessToken = String(accessToken);
          }
          // Remove any quotes and trim
          accessToken = accessToken.replace(/^["']|["']$/g, '').trim();
          localStorage.setItem('token', accessToken);
          
          // Verify token was stored
          const storedToken = localStorage.getItem('token');
          if (storedToken !== accessToken) {
            console.error('Token storage failed! Expected:', accessToken.substring(0, 20), 'Got:', storedToken?.substring(0, 20));
          }
          
          // Store refresh token if available
          if (tokens.refresh) {
            let refreshToken = tokens.refresh;
            if (typeof refreshToken !== 'string') {
              refreshToken = String(refreshToken);
            }
            refreshToken = refreshToken.replace(/^["']|["']$/g, '').trim();
            localStorage.setItem('refresh_token', refreshToken);
          }
          
          console.log('Tokens stored successfully. Access token length:', accessToken.length);

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

          // Store user data in localStorage
          localStorage.setItem('user', JSON.stringify(user));

          // Store permissions if available
          if (permissionsData) {
            localStorage.setItem('permissions', JSON.stringify(permissionsData));
            // Update AuthContext with permissions
            if (setPermissions) {
              setPermissions(permissionsData);
            }
          }

          // Update AuthContext with the new user
          if (setUser) {
            setUser(user);
          }

          setLoading(false);
          
          // Navigate after a short delay to show the toast
          setTimeout(() => {
            navigate('/');
          }, 1000);
        } else {
          setError('No token received from server');
          setLoading(false);
        }
      } else if (message_type === 'error') {
        // Handle error response with message_type: "error"
        setError('Please enter valid email or password');
        setLoading(false);
      } else {
        // Fallback for other cases
        setError('Login failed. Please try again.');
        setLoading(false);
      }
    } catch (error) {
      // Handle error response
      const responseData = error.response?.data;
      
      // Check if error has message_type
      if (responseData?.message_type === 'error') {
        setError('Please enter valid email or password');
      } else {
        const errorMessage = responseData?.error || 
                            responseData?.message || 
                            responseData?.detail ||
                            error.message || 
                            'Please enter valid email or password';
        setError(errorMessage);
      }
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <div className="login-logo">
              <FiLogIn className="logo-icon" />
            </div>
            <h2 className="login-title">Welcome Back</h2>
            <p className="login-subtitle">Sign in to your Rudra Admin account</p>
          </div>

          {error && (
            <div className="alert alert-danger d-flex align-items-center" role="alert">
              <FiAlertCircle className="me-2" />
              <div>{error}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="login-form">
            <div className="mb-3">
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <div className="input-group">
                <span className="input-group-text">
                  <FiMail />
                </span>
                <input
                  type="email"
                  className="form-control"
                  id="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="mb-3">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <div className="input-group">
                <span className="input-group-text">
                  <FiLock />
                </span>
                <input
                  type="password"
                  className="form-control"
                  id="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="mb-3 d-flex justify-content-between align-items-center">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="rememberMe"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <label className="form-check-label" htmlFor="rememberMe">
                  Remember me
                </label>
              </div>
              <Link to="/forgot-password" className="forgot-password-link">
                Forgot Password?
              </Link>
            </div>

            <button
              type="submit"
              className="btn btn-primary w-100 login-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Signing in...
                </>
              ) : (
                <>
                  <FiLogIn className="me-2" />
                  Sign In
                </>
              )}
            </button>
          </form>

          <div className="login-footer">
            <p className="text-center text-muted mb-0">
              Don't have an account?{' '}
              <Link to="/register" className="register-link">
                Contact Administrator
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

