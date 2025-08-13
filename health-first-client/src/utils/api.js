import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://192.168.0.212:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'accept': 'application/json',
  },
});

// Request interceptor for adding auth token or other headers
api.interceptors.request.use(
  (config) => {
    // Get CSRF token from cookies if available
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    
    if (csrfToken) {
      config.headers['X-CSRFTOKEN'] = csrfToken;
    }
    
    // Get auth token from localStorage if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors (401, 403, etc.)
    if (error.response) {
      const { status } = error.response;
      
      if (status === 401) {
        // Handle unauthorized (e.g., redirect to login)
        localStorage.removeItem('authToken');
        // You might want to redirect to login page here
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
