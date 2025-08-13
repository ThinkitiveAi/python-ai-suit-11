import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme/theme';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import DashboardPage from './pages/DashboardPage';
import PatientLoginPage from './pages/PatientLoginPage';
import PatientRegistrationPage from './pages/PatientRegistrationPage';
import AvailabilityPage from './pages/AvailabilityPage';
import PatientListPage from './pages/PatientListPage';

// Layouts
import DashboardLayout from './components/dashboard/DashboardLayout';

// Layout
import Layout from './components/common/Layout';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="forgot-password" element={<ForgotPasswordPage />} />
            <Route path="patient">
              <Route path="login" element={<PatientLoginPage />} />
              <Route path="register" element={<PatientRegistrationPage />} />
              <Route path="forgot-password" element={<ForgotPasswordPage />} />
            </Route>
          </Route>
          
          {/* Provider Dashboard Routes */}
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="availability" element={<AvailabilityPage />} />
            <Route path="patients" element={<PatientListPage />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App
