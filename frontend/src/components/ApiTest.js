import React, { useState } from 'react';
import { Box, Button, Typography, Card, CardContent, Alert } from '@mui/material';
import { API_ENDPOINTS, makeApiRequest, API_BASE_URL } from '../config/api';

export default function ApiTest() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testConnection = async () => {
    setLoading(true);
    setResult(null);
    
    console.log('🔍 Testing API connection...');
    console.log('📍 Backend URL:', API_BASE_URL);
    console.log('🎯 Endpoint:', API_ENDPOINTS.PROVIDER_LOGIN);
    
    try {
      const testData = {
        email: 'test@example.com',
        password: 'testpassword123'
      };
      
      console.log('📤 Sending data:', testData);
      const result = await makeApiRequest(API_ENDPOINTS.PROVIDER_LOGIN, testData, 'POST');
      
      console.log('📥 API Response:', result);
      setResult(result);
    } catch (error) {
      console.error('❌ API Error:', error);
      setResult({ success: false, error: error.message });
    }
    
    setLoading(false);
  };

  return (
    <Box sx={{ p: 4, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        🧪 API Integration Test
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6">Configuration:</Typography>
          <Typography>Backend URL: <strong>{API_BASE_URL}</strong></Typography>
          <Typography>Login Endpoint: <strong>{API_ENDPOINTS.PROVIDER_LOGIN}</strong></Typography>
          <Typography>Full URL: <strong>{API_BASE_URL}{API_ENDPOINTS.PROVIDER_LOGIN}</strong></Typography>
        </CardContent>
      </Card>

      <Button 
        variant="contained" 
        onClick={testConnection} 
        disabled={loading}
        size="large"
        sx={{ mb: 3 }}
      >
        {loading ? '🔄 Testing...' : '🚀 Test API Connection'}
      </Button>

      {result && (
        <Alert 
          severity={result.success ? 'success' : 'error'} 
          sx={{ mb: 2 }}
        >
          <Typography variant="h6">
            {result.success ? '✅ API Call Successful!' : '❌ API Call Failed'}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            Status: {result.status || 'No status'}
          </Typography>
          <Typography variant="body2">
            Response: {JSON.stringify(result.data || result.error, null, 2)}
          </Typography>
        </Alert>
      )}

      <Alert severity="info">
        <Typography variant="body2">
          <strong>📝 Instructions:</strong><br/>
          1. Open browser DevTools (F12)<br/>
          2. Go to Network tab<br/>
          3. Click "Test API Connection"<br/>
          4. Check Console tab for detailed logs<br/>
          5. Verify network requests to {API_BASE_URL}
        </Typography>
      </Alert>
    </Box>
  );
}