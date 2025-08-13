import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import logo from './logo.svg';
import './App.css';
import ProviderLogin from './components/ProviderLogin';
import ProviderRegistration from './components/ProviderRegistration';
import PatientLogin from './components/PatientLogin';
import PatientRegistration from './components/PatientRegistration';
import ProviderAvailability from './components/ProviderAvailability';
import ApiTest from './components/ApiTest';
import EMRDashboard from './components/EMRDashboard';

// Placeholder for ProviderLogin import

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<EMRDashboard />} />
          <Route path="/dashboard" element={<EMRDashboard />} />
          <Route path="/register" element={<ProviderRegistration />} />
          <Route path="/patient-login" element={<PatientLogin />} />
          <Route path="/patient-registration" element={<PatientRegistration />} />
          <Route path="/provider-availability" element={<ProviderAvailability />} />
          <Route path="/api-test" element={<ApiTest />} />
          <Route path="/emr-dashboard" element={<EMRDashboard />} />
          {/* Add routes for /dashboard, /register, /forgot-password as needed */}
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
