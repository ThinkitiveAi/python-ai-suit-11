import api from './api';

/**
 * Service for provider-related API calls
 */
const providerService = {
  /**
   * Get list of all providers for dropdown
   * @returns {Promise} Promise with provider list data
   */
  getProviderList: async () => {
    try {
      const response = await api.get('/dropdown/providers');
      return response.data;
    } catch (error) {
      console.error('Error fetching provider list:', error);
      throw error;
    }
  },
};

export default providerService;
