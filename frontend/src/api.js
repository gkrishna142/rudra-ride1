import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://44.200.173.141:8000/api/auth/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      // Remove any quotes or extra characters from token
      let cleanToken = token.replace(/^["']|["']$/g, '');
      // If token is still wrapped in quotes after first pass, try again
      cleanToken = cleanToken.trim();
      
      // Debug: Log token (first 20 chars only for security)
      if (process.env.NODE_ENV === 'development') {
        console.log('Sending request with token:', cleanToken.substring(0, 20) + '...');
      }
      
      config.headers.Authorization = `Bearer ${cleanToken}`;
    } else {
      // Debug: Log when no token found
      if (process.env.NODE_ENV === 'development') {
        console.warn('No token found in localStorage for request to:', config.url);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (refreshToken) {
          // Try to refresh the token using the admin refresh endpoint
          const response = await axios.post(
            'http://127.0.0.1:8000/api/auth/admin/refresh/',
            {
              refresh: refreshToken.replace(/^["']|["']$/g, '')
            }
          );

          // Backend returns { message_type: 'success', tokens: { access: ..., refresh: ... } }
          const { tokens, message_type } = response.data;
          
          if (message_type === 'success' && tokens && tokens.access) {
            // Store new access token
            let newAccessToken = tokens.access;
            // Ensure it's a string
            if (typeof newAccessToken !== 'string') {
              newAccessToken = String(newAccessToken);
            }
            // Remove any quotes
            newAccessToken = newAccessToken.replace(/^["']|["']$/g, '').trim();
            localStorage.setItem('token', newAccessToken);
            
            // Store new refresh token if provided (rotation enabled)
            if (tokens.refresh) {
              let newRefreshToken = tokens.refresh;
              if (typeof newRefreshToken !== 'string') {
                newRefreshToken = String(newRefreshToken);
              }
              newRefreshToken = newRefreshToken.replace(/^["']|["']$/g, '').trim();
              localStorage.setItem('refresh_token', newRefreshToken);
            }
            
            // Update the original request with new token
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            
            // Retry the original request
            return api(originalRequest);
          } else {
            console.error('Token refresh response format unexpected:', response.data);
          }
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        console.error('Token refresh failed:', refreshError);
        
        // Clear storage
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        // Only redirect if not already on login page
        if (window.location.pathname !== '/login' && window.location.pathname !== '/forgot-password') {
          // Show alert only once (use a flag to prevent multiple alerts)
          if (!window.authRedirectInProgress) {
            window.authRedirectInProgress = true;
            alert('Your session has expired. Please login again.');
            setTimeout(() => {
              window.authRedirectInProgress = false;
              window.location.href = '/login';
            }, 100);
          }
        }
        return Promise.reject(refreshError);
      }

      // If no refresh token, clear storage and redirect
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      // Only redirect if not already on login page
      if (window.location.pathname !== '/login' && window.location.pathname !== '/forgot-password') {
        if (!window.authRedirectInProgress) {
          window.authRedirectInProgress = true;
          alert('Your session has expired. Please login again.');
          setTimeout(() => {
            window.authRedirectInProgress = false;
            window.location.href = '/login';
          }, 100);
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;

