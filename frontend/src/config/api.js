import axios from 'axios';
import { getBackendUrl } from './environment';

// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || getBackendUrl();

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// API Endpoints
export const API_ENDPOINTS = {
  // Provider endpoints
  PROVIDER_REGISTER: '/api/v1/provider/register',
  PROVIDER_LOGIN: '/api/v1/provider/login',
  PROVIDER_AVAILABILITY: '/api/v1/provider/availability',
  
  // Patient endpoints
  PATIENT_REGISTER: '/api/v1/patient/register',
  PATIENT_LOGIN: '/api/v1/patient/login',
  
  // Common endpoints
  UPLOAD_IMAGE: '/api/v1/upload/image',
};

// API helper function using axios
export const makeApiRequest = async (endpoint, data = null, method = 'GET') => {
  try {
    const config = {
      method: method,
      url: endpoint,
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      config.data = data;
    }
    
    const response = await apiClient(config);
    
    return { 
      success: true, 
      data: response.data, 
      status: response.status 
    };
  } catch (error) {
    let errorMessage = 'API request failed';
    
    if (error.response) {
      // Server responded with error status
      errorMessage = error.response.data?.detail || 
                    error.response.data?.message || 
                    error.response.data?.error || 
                    `Server error: ${error.response.status}`;
    } else if (error.request) {
      // Network error
      errorMessage = 'Network error. Please check your connection.';
    } else {
      // Other error
      errorMessage = error.message;
    }
    
    return { 
      success: false, 
      error: errorMessage,
      status: error.response?.status 
    };
  }
};

// Export axios instance for direct use if needed
export { apiClient };