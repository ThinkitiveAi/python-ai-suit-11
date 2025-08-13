import api from './api';

/**
 * Authentication service for both providers and patients
 */
const authService = {
  /**
   * Provider login
   * @param {Object} credentials - Login credentials
   * @param {string} credentials.email - Provider email
   * @param {string} credentials.password - Provider password
   * @returns {Promise} - Response from API
   */
  providerLogin: async (credentials) => {
    try {
      const response = await api.post('/provider/login', credentials);
      
      // If login successful, store auth token and user type
      if (response.data && response.data.token) {
        localStorage.setItem('authToken', response.data.token);
        localStorage.setItem('userType', 'provider');
      }
      
      return response.data;
    } catch (error) {
      console.error('Provider login error:', error);
      throw error;
    }
  },
  
  /**
   * Patient login
   * @param {Object} credentials - Login credentials
   * @param {string} credentials.email - Patient email
   * @param {string} credentials.password - Patient password
   * @returns {Promise} - Response from API
   */
  patientLogin: async (credentials) => {
    try {
      const response = await api.post('/patient/login/', credentials);
      
      // If login successful, store auth token and user type
      if (response.data && response.data.token) {
        localStorage.setItem('authToken', response.data.token);
        localStorage.setItem('userType', 'patient');
      }
      
      return response.data;
    } catch (error) {
      console.error('Patient login error:', error);
      throw error;
    }
  },
  
  /**
   * Logout user (provider or patient)
   */
  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userType');
    // Additional logout logic can be added here
  },
  
  /**
   * Check if user is authenticated
   * @returns {boolean} - Authentication status
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('authToken');
  },
  
  /**
   * Get user type (provider or patient)
   * @returns {string|null} - User type or null if not authenticated
   */
  getUserType: () => {
    return localStorage.getItem('userType');
  }
};

export default authService;
