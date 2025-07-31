import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, TextField, Button, Checkbox,
  FormControlLabel, InputAdornment, IconButton, Link, CircularProgress, Alert
} from '@mui/material';
import { Visibility, VisibilityOff, Email, Phone, Lock, Person } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS, makeApiRequest, API_BASE_URL } from '../config/api';

const isEmail = (value) => /\S+@\S+\.\S+/.test(value);
const isPhone = (value) => /^\+?\d{10,15}$/.test(value);

export default function ProviderLogin() {
  const [credential, setCredential] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [touched, setTouched] = useState({ credential: false, password: false });
  const navigate = useNavigate();

  // Validation
  const credentialValid = isEmail(credential) || isPhone(credential);
  const passwordValid = password.length >= 8;

  const handleLogin = async (e) => {
    e.preventDefault();
    setTouched({ credential: true, password: true });
    setError('');
    if (!credentialValid || !passwordValid) return;

    setLoading(true);
    
    try {
      const loginData = {
        email: credential, // Backend expects email field
        password: password
      };

      console.log('🚀 MAKING API CALL TO:', API_ENDPOINTS.PROVIDER_LOGIN);
      console.log('📤 Sending login data:', loginData);
      console.log('🌐 Backend URL configured:', API_BASE_URL);
      
      const result = await makeApiRequest(API_ENDPOINTS.PROVIDER_LOGIN, loginData, 'POST');
      
      console.log('📥 API Response received:', result);

      setLoading(false);
      
      if (result.success) {
        // Store token if provided
        if (result.data.token || result.data.access_token) {
          localStorage.setItem('provider_token', result.data.token || result.data.access_token);
        }
        // Success: redirect to dashboard
        navigate('/dashboard');
      } else {
        setError(result.error || 'Invalid credentials. Please try again.');
      }
    } catch (err) {
      setLoading(false);
      setError('Network error. Please try again.');
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #e0f2fe 0%, #f4f8fb 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Person sx={{ fontSize: 48, color: 'primary.main' }} />
        <Typography variant="h4" fontWeight="bold" color="primary.main" gutterBottom>
          Provider Login
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Secure access for medical professionals
        </Typography>
      </Box>

      {/* Login Card */}
      <Card sx={{ minWidth: 340, maxWidth: 380, mx: 1, boxShadow: 3 }}>
        <CardContent>
          <form autoComplete="on" onSubmit={handleLogin}>
            <TextField
              fullWidth
              label="Email or Phone Number"
              placeholder="Enter your email or phone"
              margin="normal"
              value={credential}
              onChange={e => setCredential(e.target.value)}
              onBlur={() => setTouched(t => ({ ...t, credential: true }))}
              error={touched.credential && !credentialValid}
              helperText={
                touched.credential && !credentialValid
                  ? 'Enter a valid email or phone number'
                  : ' '
              }
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    {isEmail(credential) ? <Email /> : <Phone />}
                  </InputAdornment>
                ),
                inputProps: {
                  'aria-label': 'Email or Phone Number',
                  autoComplete: 'username',
                },
              }}
              required
            />

            <TextField
              fullWidth
              label="Password"
              placeholder="Enter your password"
              margin="normal"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={e => setPassword(e.target.value)}
              onBlur={() => setTouched(t => ({ ...t, password: true }))}
              error={touched.password && !passwordValid}
              helperText={
                touched.password && !passwordValid
                  ? 'Password must be at least 8 characters'
                  : ' '
              }
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      onClick={() => setShowPassword(s => !s)}
                      edge="end"
                      tabIndex={-1}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
                inputProps: {
                  'aria-label': 'Password',
                  autoComplete: 'current-password',
                },
              }}
              required
            />

            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={rememberMe}
                    onChange={e => setRememberMe(e.target.checked)}
                    color="primary"
                    inputProps={{ 'aria-label': 'Remember Me' }}
                  />
                }
                label="Remember Me"
              />
              <Link
                component="button"
                variant="body2"
                onClick={() => navigate('/forgot-password')}
                tabIndex={0}
                underline="hover"
                sx={{ color: 'secondary.main', fontWeight: 500 }}
              >
                Forgot Password?
              </Link>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              disabled={loading}
              sx={{ mt: 1, mb: 2, height: 48, fontWeight: 'bold', fontSize: 16 }}
              aria-label="Login"
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Login'}
            </Button>
          </form>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Link
              component="button"
              variant="body2"
              onClick={() => navigate('/register')}
              tabIndex={0}
              underline="hover"
              sx={{ color: 'primary.main', fontWeight: 500 }}
            >
              New provider? Register
            </Link>
            <Link
              href="#"
              variant="body2"
              underline="hover"
              sx={{ color: 'text.secondary' }}
            >
              Privacy Policy
            </Link>
          </Box>
        </CardContent>
      </Card>

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center', color: 'text.secondary' }}>
        <Typography variant="caption">
          &copy; {new Date().getFullYear()} Your Healthcare App. Need help? <Link href="#">Contact Support</Link>
        </Typography>
      </Box>
    </Box>
  );
} 