// Environment Configuration
// You can change this URL to point to your backend server

const environments = {
  development: "http://192.168.0.212:8000",
  production: "http://192.168.0.212:8000", // Update this for production
  local: "http://localhost:8000", // For local backend development
};

// Current environment - change this as needed
export const CURRENT_ENV = "development";

export const getBackendUrl = () => {
  return environments[CURRENT_ENV] || environments.development;
};

export default {
  BACKEND_URL: getBackendUrl(),
  API_TIMEOUT: 10000,
  ENVIRONMENTS: environments,
};
