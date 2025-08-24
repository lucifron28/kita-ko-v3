import axios from 'axios';
import toast from 'react-hot-toast';

// Base API configuration
const isDevelopment = import.meta.env.MODE === 'development';
const API_BASE_URL = isDevelopment
  ? (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api')
  : '/api';  // Same domain in production

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  withCredentials: true, // Important for httpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Get token from auth context if available, fallback to localStorage
    const token = window.authContext?.accessToken || localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Debug logging
    if (import.meta.env.VITE_DEBUG === 'true') {
      console.log('API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        headers: config.headers,
        data: config.data
      });
    }

    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    // Debug logging
    if (import.meta.env.VITE_DEBUG === 'true') {
      console.log('API Response:', {
        status: response.status,
        url: response.config.url,
        data: response.data
      });
    }
    return response;
  },
  async (error) => {
    // Debug logging
    if (import.meta.env.VITE_DEBUG === 'true') {
      console.error('API Error:', {
        status: error.response?.status,
        url: error.config?.url,
        data: error.response?.data,
        message: error.message
      });
    }

    const originalRequest = error.config;

    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token using httpOnly cookie
        const refreshResponse = await axios.post(
          `${API_BASE_URL}/auth/token/refresh/`,
          {},
          { 
            withCredentials: true,
            headers: { 'Content-Type': 'application/json' }
          }
        );

        const newAccessToken = refreshResponse.data.access;
        
        // Notify the auth context about the new token
        if (window.authContext && window.authContext.updateAccessToken) {
          window.authContext.updateAccessToken(newAccessToken);
        }

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        if (window.authContext && window.authContext.logout) {
          window.authContext.logout();
        } else {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    // Handle other errors
    if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.response?.status === 429) {
      toast.error('Too many requests. Please slow down.');
    }

    return Promise.reject(error);
  }
);

// Auth API endpoints
export const authAPI = {
  login: async (credentials) => {
    const response = await api.post('/auth/login/', credentials);
    // The access token will be handled by the auth context
    // The refresh token will be stored as an httpOnly cookie by the backend
    return response;
  },
  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    // The access token will be handled by the auth context
    // The refresh token will be stored as an httpOnly cookie by the backend
    return response;
  },
  logout: async () => {
    const response = await api.post('/auth/logout/');
    // The backend will clear the httpOnly cookie
    return response;
  },
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.put('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
  getDashboard: () => api.get('/auth/dashboard/'),
};

// Transaction API endpoints
export const transactionAPI = {
  uploadFile: (formData) => api.post('/transactions/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getUploads: (params) => api.get('/transactions/uploads/', { params }),
  getUploadStatus: (uploadId) => api.get(`/transactions/uploads/${uploadId}/status/`),
  processUpload: (uploadId) => api.post(`/transactions/uploads/${uploadId}/process/`),
  deleteUpload: (uploadId) => api.delete(`/transactions/uploads/${uploadId}/delete/`),
  getTransactions: (params) => api.get('/transactions/', { params }),
  getTransaction: (id) => api.get(`/transactions/${id}/`),
  updateTransaction: (id, data) => api.put(`/transactions/${id}/`, data),
  deleteTransaction: (id) => api.delete(`/transactions/${id}/`),
  bulkUpdateTransactions: (data) => api.post('/transactions/bulk-update/', data),
  getTransactionSummary: (params) => api.get('/transactions/summary/', { params }),
};

// AI Processing API endpoints
export const aiAPI = {
  categorizeTransactions: (data) => api.post('/ai/categorize/', data),
  generateSummary: (data) => api.post('/ai/summarize/', data),
  detectAnomalies: (data) => api.post('/ai/detect-anomalies/', data),
  getJobs: (params) => api.get('/ai/jobs/', { params }),
  getJobStatus: (jobId) => api.get(`/ai/jobs/${jobId}/`),
};

// Reports API endpoints
export const reportsAPI = {
  createReport: (data) => api.post('/reports/create/', data),
  getReports: (params) => api.get('/reports/', { params }),
  getReport: (id) => api.get(`/reports/${id}/`),
  getReportStatus: (id) => api.get(`/reports/${id}/status/`),
  updateReport: (id, data) => api.put(`/reports/${id}/`, data),
  deleteReport: (id) => api.delete(`/reports/${id}/delete/`),
  generatePDF: (data) => api.post('/reports/generate-pdf/', data),
  downloadReport: (id, token) => {
    const url = token 
      ? `/reports/${id}/download/?token=${token}`
      : `/reports/${id}/download/`;
    return api.get(url, { responseType: 'blob' });
  },
  verifyReport: (data) => api.post('/reports/verify/', data),
  getAnalytics: () => api.get('/reports/analytics/'),
};

// Utility functions
export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(amount);
};

export const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-PH', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date));
};

export const formatDateTime = (date) => {
  return new Intl.DateTimeFormat('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
};

// Export both as default and named export for flexibility
export { api };
export default api;
