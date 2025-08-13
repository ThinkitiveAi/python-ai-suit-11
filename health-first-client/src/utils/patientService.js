import api from './api';

/**
 * Service for patient-related API calls
 */
const patientService = {
  /**
   * Get list of all patients
   * @returns {Promise} Promise with patient list data
   */
  getPatientList: async () => {
    try {
      const response = await api.get('/dropdown/patients');
      return response.data;
    } catch (error) {
      console.error('Error fetching patient list:', error);
      throw error;
    }
  },
};

export default patientService;
