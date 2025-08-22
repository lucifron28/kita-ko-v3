import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

// Auth context
const AuthContext = createContext();

// Auth reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        loading: true,
        error: null,
      };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        loading: false,
        isAuthenticated: true,
        user: action.payload.user,
        accessToken: action.payload.accessToken,
        error: null,
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        loading: false,
        isAuthenticated: false,
        user: null,
        accessToken: null,
        error: action.payload,
      };
    case 'LOGOUT':
      localStorage.removeItem('hasSession');
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        accessToken: null,
        loading: false,
        error: null,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };
    case 'UPDATE_ACCESS_TOKEN':
      return {
        ...state,
        accessToken: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
};

// Initial state
const initialState = {
  isAuthenticated: false,
  user: null,
  accessToken: null, // Store access token in memory
  loading: true,
  error: null,
};

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Update access token function
  const updateAccessToken = (token) => {
    dispatch({ type: 'UPDATE_ACCESS_TOKEN', payload: token });
  };

  // Expose auth context globally for API interceptors
  useEffect(() => {
    window.authContext = {
      accessToken: state.accessToken,
      updateAccessToken,
      logout: () => dispatch({ type: 'LOGOUT' })
    };
  }, [state.accessToken]);

    // Check for existing session on mount
  useEffect(() => {
    const checkSession = async () => {
      // Only try to verify session if we might have a refresh token (cookie)
      // Check for session indicators
      const hasSessionIndicator = document.cookie.includes('refresh_token') || 
                                   localStorage.getItem('hasSession') === 'true';
      
      if (!hasSessionIndicator) {
        // No session indicators, user was never logged in or explicitly logged out
        dispatch({ type: 'SET_LOADING', payload: false });
        return;
      }

      // For now, just set as authenticated based on session indicators
      // The actual profile data will be fetched by React Query hooks when needed
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: null, // Will be fetched by useProfile hook
          accessToken: null, // Token will be managed by API interceptors
        },
      });
      
      // Set session indicator
      localStorage.setItem('hasSession', 'true');
      dispatch({ type: 'SET_LOADING', payload: false });
    };

    checkSession();
  }, []);

  // Login function
  const login = async (accessToken, user) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user,
          accessToken,
        },
      });

      // Set session indicator for future session checks
      localStorage.setItem('hasSession', 'true');
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      dispatch({
        type: 'LOGIN_FAIL',
        payload: error.message || 'Login failed',
      });
      return { success: false, error: error.message || 'Login failed' };
    }
  };

  // Register function
  const register = async (userData) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authAPI.register(userData);
      const { user, tokens } = response.data;

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user,
          accessToken: tokens.access,
        },
      });

      // Set session indicator for future session checks
      localStorage.setItem('hasSession', 'true');
      
      toast.success('Registration successful!');
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);

      // Handle different error response formats
      let errorMessage = 'Registration failed';

      if (error.response?.data) {
        const errorData = error.response.data;

        // Check for various error message formats
        if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.details) {
          errorMessage = errorData.details;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.non_field_errors) {
          errorMessage = Array.isArray(errorData.non_field_errors)
            ? errorData.non_field_errors[0]
            : errorData.non_field_errors;
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else {
          // Handle field-specific errors
          const fieldErrors = [];
          Object.keys(errorData).forEach(field => {
            if (Array.isArray(errorData[field])) {
              fieldErrors.push(`${field}: ${errorData[field][0]}`);
            } else if (typeof errorData[field] === 'string') {
              fieldErrors.push(`${field}: ${errorData[field]}`);
            }
          });
          if (fieldErrors.length > 0) {
            errorMessage = fieldErrors[0]; // Show first error
          }
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      dispatch({
        type: 'LOGIN_FAILURE',
        payload: errorMessage,
      });
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      // Call logout API to clear httpOnly cookie
      await authAPI.logout();
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API error:', error);
    } finally {
      // Clear state and session indicator
      dispatch({ type: 'LOGOUT' });
      localStorage.removeItem('hasSession');
      toast.success('Logged out successfully');
    }
  };

  // Update user profile
  const updateProfile = async (profileData) => {
    try {
      const response = await authAPI.updateProfile(profileData);
      dispatch({
        type: 'UPDATE_USER',
        payload: response.data,
      });
      toast.success('Profile updated successfully');
      return { success: true };
    } catch (error) {
      console.error('Profile update error:', error);

      let errorMessage = 'Profile update failed';
      if (error.response?.data) {
        const errorData = error.response.data;
        if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.details) {
          errorMessage = errorData.details;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      }

      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Change password
  const changePassword = async (passwordData) => {
    try {
      await authAPI.changePassword(passwordData);
      toast.success('Password changed successfully');
      return { success: true };
    } catch (error) {
      console.error('Password change error:', error);

      let errorMessage = 'Password change failed';
      if (error.response?.data) {
        const errorData = error.response.data;
        if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.details) {
          errorMessage = errorData.details;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.old_password) {
          errorMessage = Array.isArray(errorData.old_password)
            ? errorData.old_password[0]
            : errorData.old_password;
        } else if (errorData.new_password) {
          errorMessage = Array.isArray(errorData.new_password)
            ? errorData.new_password[0]
            : errorData.new_password;
        }
      }

      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Clear error
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Context value
  const value = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    clearError,
    updateAccessToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
