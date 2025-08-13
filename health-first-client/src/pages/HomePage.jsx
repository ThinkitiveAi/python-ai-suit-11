import React from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Card, 
  CardContent,
  Grid,
  Paper,
  Link
} from '@mui/material';
import { 
  LocalHospital, 
  Person, 
  MedicalServices, 
  ArrowForward 
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';

const HomePage = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f0f9ff',
        backgroundImage: 'linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%)',
      }}
    >
      {/* Header */}
      <Box 
        sx={{ 
          py: 3, 
          backgroundColor: 'white',
          boxShadow: 1
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <LocalHospital sx={{ fontSize: 40, color: 'primary.main', mr: 1 }} />
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700, color: 'primary.main' }}>
              Health First
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* Hero Section */}
      <Box 
        sx={{ 
          py: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center'
        }}
      >
        <Container maxWidth="md">
          <Typography 
            variant="h2" 
            component="h2" 
            sx={{ 
              fontWeight: 700, 
              mb: 2,
              background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Healthcare at Your Fingertips
          </Typography>
          <Typography 
            variant="h5" 
            color="text.secondary" 
            sx={{ mb: 4, maxWidth: '800px', mx: 'auto' }}
          >
            Access quality healthcare services online with our comprehensive platform for both patients and healthcare providers.
          </Typography>
        </Container>
      </Box>

      {/* Login Options */}
      <Container maxWidth="lg" sx={{ mb: 8 }}>
        <Grid container spacing={4} justifyContent="center">
          {/* Provider Login Card */}
          <Grid item xs={12} md={5}>
            <Card 
              elevation={4}
              sx={{
                height: '100%',
                borderRadius: 3,
                transition: 'transform 0.3s, box-shadow 0.3s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: 8,
                },
              }}
            >
              <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <MedicalServices sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Typography variant="h4" component="h3" sx={{ fontWeight: 600 }}>
                    For Providers
                  </Typography>
                </Box>
                
                <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary', flexGrow: 1 }}>
                  Healthcare professionals can access patient records, manage appointments, and provide virtual consultations through our secure provider portal.
                </Typography>
                
                <Button
                  component={RouterLink}
                  to="/login"
                  variant="contained"
                  color="primary"
                  size="large"
                  endIcon={<ArrowForward />}
                  sx={{ 
                    py: 1.5,
                    fontWeight: 600,
                    borderRadius: 2,
                  }}
                >
                  Provider Login
                </Button>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Patient Login Card */}
          <Grid item xs={12} md={5}>
            <Card 
              elevation={4}
              sx={{
                height: '100%',
                borderRadius: 3,
                transition: 'transform 0.3s, box-shadow 0.3s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: 8,
                },
              }}
            >
              <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Person sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Typography variant="h4" component="h3" sx={{ fontWeight: 600 }}>
                    For Patients
                  </Typography>
                </Box>
                
                <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary', flexGrow: 1 }}>
                  Patients can book appointments, access medical records, communicate with healthcare providers, and manage prescriptions all in one place.
                </Typography>
                
                <Button
                  component={RouterLink}
                  to="/patient/login"
                  variant="contained"
                  color="secondary"
                  size="large"
                  endIcon={<ArrowForward />}
                  sx={{ 
                    py: 1.5,
                    fontWeight: 600,
                    borderRadius: 2,
                  }}
                >
                  Patient Login
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Footer */}
      <Box 
        sx={{ 
          py: 3, 
          mt: 'auto',
          backgroundColor: 'white',
          borderTop: 1,
          borderColor: 'divider'
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={2} justifyContent="space-between" alignItems="center">
            <Grid item>
              <Typography variant="body2" color="text.secondary">
                © {new Date().getFullYear()} Health First. All rights reserved.
              </Typography>
            </Grid>
            <Grid item>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Link href="#" underline="hover" color="text.secondary" variant="body2">
                  Privacy Policy
                </Link>
                <Link href="#" underline="hover" color="text.secondary" variant="body2">
                  Terms of Service
                </Link>
                <Link href="#" underline="hover" color="text.secondary" variant="body2">
                  Help & Support
                </Link>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default HomePage;
