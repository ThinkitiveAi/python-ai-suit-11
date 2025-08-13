import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  IconButton,
  Card,
  Grid,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  Badge,
  Avatar,
  Menu,
  Paper,
  Divider,
  Chip,
  CircularProgress,
  Alert,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Modal,
  Stepper,
  Step,
  StepLabel,
  Switch,
  FormControlLabel,
  Radio,
  RadioGroup,
  FormLabel
} from '@mui/material';
import {
  Search,
  Notifications,
  AccountCircle,
  ExpandMore,
  AccessTime,
  Delete,
  Add,
  CalendarToday,
  Settings,
  Edit,
  Save,
  Cancel,
  Schedule,
  Close,
  Person,
  Phone,
  Email,
  LocationOn,
  VideoCall,
  EventNote,
  AttachMoney
} from '@mui/icons-material';
import axios from 'axios';

const EMRDashboard = () => {
  const [tabValue, setTabValue] = useState(1); // Default to "Scheduling" tab (index 1)
  const [selectedProvider, setSelectedProvider] = useState('');
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [timeZone, setTimeZone] = useState('');
  const [blockDays, setBlockDays] = useState([
    { date: '', fromTime: '', tillTime: '' },
    { date: '', fromTime: '', tillTime: '' }
  ]);
  const [anchorEl, setAnchorEl] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [editingDay, setEditingDay] = useState(null);
  const [appointmentModal, setAppointmentModal] = useState(false);
  const [appointments, setAppointments] = useState([
    {
      id: 1,
      date: '02/24/21',
      time: '11:17am',
      type: 'New',
      patientName: 'Heena West (F)',
      dob: '10-31-1959 (63)',
      contact: '202-555-0188',
      provider: 'Jacob Jones',
      reason: 'Infection Disease',
      status: 'Scheduled'
    },
    {
      id: 2,
      date: '02/26/21',
      time: '9:40pm',
      type: 'Follow Up',
      patientName: 'Arlene McCoy (M)',
      dob: '10-31-1959 (42)',
      contact: '202-555-0186',
      provider: 'Bessie Cooper',
      reason: 'Itching',
      status: 'Checked-in'
    },
    {
      id: 3,
      date: '03/07/21',
      time: '2:53am',
      type: 'New',
      patientName: 'Esther Howard (M)',
      dob: '10-31-1959 (32)',
      contact: '202-555-0172',
      provider: 'Wade Warren',
      reason: 'Insomnia',
      status: 'Scheduled'
    },
    {
      id: 4,
      date: '03/01/21',
      time: '6:05am',
      type: 'Follow Up',
      patientName: 'Jane Cooper (F)',
      dob: '10-31-1959 (24)',
      contact: '202-555-0124',
      provider: 'Darrell Steward',
      reason: 'Blurred Vision',
      status: 'Cancelled'
    },
    {
      id: 5,
      date: '02/10/21',
      time: '8:01pm',
      type: 'Follow Up',
      patientName: 'Darrell Steward (M)',
      dob: '10-31-1959 (66)',
      contact: '202-555-0108',
      provider: 'Savannah Nguyen',
      reason: 'Hearing Loss',
      status: 'Scheduled'
    }
  ]);
  const [newAppointment, setNewAppointment] = useState({
    patient_id: '',
    provider_id: '',
    appointment_slot_id: '',
    appointment_mode: 'in_person',
    appointment_type: 'consultation',
    appointment_date: '',
    appointment_time: '',
    duration_minutes: 60,
    timezone: 'America/New_York',
    estimated_amount: '',
    currency: 'USD',
    reason_for_visit: '',
    symptoms: '',
    special_instructions: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    location_details: {
      clinic_name: '',
      address: '',
      city: '',
      state: '',
      zipcode: ''
    },
    video_call_link: ''
  });

  // Days of the week with default times
  const [weekDays, setWeekDays] = useState([
    { day: 'Monday', from: '09:00', till: '18:00', enabled: true },
    { day: 'Tuesday', from: '09:00', till: '18:00', enabled: true },
    { day: 'Wednesday', from: '09:00', till: '18:00', enabled: true },
    { day: 'Thursday', from: '09:00', till: '18:00', enabled: true },
    { day: 'Friday', from: '09:00', till: '18:00', enabled: true },
    { day: 'Saturday', from: '09:00', till: '18:00', enabled: true }
  ]);

  // API configuration
  const API_BASE_URL = 'http://0.0.0.0:8000/api/v1';
  const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYzJiYzY5NzktNmYxZC00MmJjLWI0ZDktNzJlYzdlMjcwNjZmIiwidXNlcl90eXBlIjoicHJvdmlkZXIiLCJlbWFpbCI6ImRyLnNhcmFoLmpvaG5zb25AZXhhbXBsZS5jb20iLCJmaXJzdF9uYW1lIjoiRHIuIFNhcmFoIiwibGFzdF9uYW1lIjoiSm9obnNvbiIsInNwZWNpYWxpemF0aW9uIjoiQ2FyZGlvbG9neSIsInZlcmlmaWNhdGlvbl9zdGF0dXMiOiJ2ZXJpZmllZCIsImlhdCI6MTc1NDU2MTc2MCwiZXhwIjoxNzU0NjQ4MTYwLCJ0b2tlbl90eXBlIjoiYWNjZXNzIn0.UlDa4g9DxeqsVI2hI5HYVIV7lwZLIN2dU2p0j9NXLTw';
  const CSRF_TOKEN_APPOINTMENTS = '5bWdtUN3Zi1qvHgJJAPKbaUXc6pHqkltRtSDUFe7tZx58x7Lu0PVYMMWRg9PeH9W';
  const CSRF_TOKEN = 'yHk1nRM73CJqVHFD3jXHGtP7lGZpUkS5kZgrOCdbxjf5yxwFOJXSt5H60QJxIHGy';

  // Fetch providers from API
  useEffect(() => {
    const fetchProviders = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_BASE_URL}/dropdown/providers`, {
          headers: {
            'accept': 'application/json',
            'Authorization': AUTH_TOKEN,
            'X-CSRFTOKEN': CSRF_TOKEN
          }
        });
        
        if (response.data && Array.isArray(response.data)) {
          setProviders(response.data);
          if (response.data.length > 0) {
            setSelectedProvider(response.data[0].id || response.data[0].name || response.data[0]);
          }
        }
        setSnackbar({ open: true, message: 'Providers loaded successfully', severity: 'success' });
      } catch (error) {
        console.error('Error fetching providers:', error);
        setSnackbar({ open: true, message: 'Failed to load providers', severity: 'error' });
        // Fallback to mock data
        setProviders([
          { id: 'john-doe', name: 'Dr. John Doe', specialization: 'Cardiology' },
          { id: 'jane-smith', name: 'Dr. Jane Smith', specialization: 'Neurology' },
          { id: 'mike-brown', name: 'Dr. Mike Brown', specialization: 'Orthopedics' }
        ]);
        setSelectedProvider('john-doe');
      } finally {
        setLoading(false);
      }
    };

    fetchProviders();
  }, []);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleProviderChange = (event) => {
    setSelectedProvider(event.target.value);
    setSnackbar({ open: true, message: `Provider changed to ${event.target.value}`, severity: 'info' });
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const addBlockDay = () => {
    setBlockDays([...blockDays, { date: '', fromTime: '', tillTime: '' }]);
  };

  const removeBlockDay = (index) => {
    const newBlockDays = blockDays.filter((_, i) => i !== index);
    setBlockDays(newBlockDays);
  };

  const updateBlockDay = (index, field, value) => {
    const newBlockDays = [...blockDays];
    newBlockDays[index][field] = value;
    setBlockDays(newBlockDays);
  };

  const updateWeekDay = (index, field, value) => {
    const newWeekDays = [...weekDays];
    newWeekDays[index][field] = value;
    setWeekDays(newWeekDays);
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      // Simulate API call for saving
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSnackbar({ open: true, message: 'Settings saved successfully!', severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: 'Failed to save settings', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Appointment form handlers
  const handleAppointmentModalOpen = () => {
    setAppointmentModal(true);
  };

  const handleAppointmentModalClose = () => {
    setAppointmentModal(false);
    setNewAppointment({
      patient_id: '',
      provider_id: '',
      appointment_slot_id: '',
      appointment_mode: 'in_person',
      appointment_type: 'consultation',
      appointment_date: '',
      appointment_time: '',
      duration_minutes: 60,
      timezone: 'America/New_York',
      estimated_amount: '',
      currency: 'USD',
      reason_for_visit: '',
      symptoms: '',
      special_instructions: '',
      emergency_contact_name: '',
      emergency_contact_phone: '',
      location_details: {
        clinic_name: '',
        address: '',
        city: '',
        state: '',
        zipcode: ''
      },
      video_call_link: ''
    });
  };

  const updateAppointmentField = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setNewAppointment(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setNewAppointment(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const createAppointment = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/provider/appointments/`,
        newAppointment,
        {
          headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFTOKEN': CSRF_TOKEN_APPOINTMENTS
          }
        }
      );
      
      setSnackbar({ open: true, message: 'Appointment created successfully!', severity: 'success' });
      handleAppointmentModalClose();
      
      // Add the new appointment to the list (mock for demo)
      const newAppt = {
        id: appointments.length + 1,
        date: new Date(newAppointment.appointment_date).toLocaleDateString(),
        time: newAppointment.appointment_time,
        type: newAppointment.appointment_type,
        patientName: 'New Patient',
        dob: 'TBD',
        contact: 'TBD',
        provider: providers.find(p => p.id === newAppointment.provider_id)?.name || 'Unknown',
        reason: newAppointment.reason_for_visit,
        status: 'Scheduled'
      };
      setAppointments(prev => [newAppt, ...prev]);
      
    } catch (error) {
      console.error('Error creating appointment:', error);
      setSnackbar({ open: true, message: 'Failed to create appointment', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'scheduled': return '#1976d2';
      case 'checked-in': return '#388e3c';
      case 'cancelled': return '#d32f2f';
      case 'completed': return '#7b1fa2';
      default: return '#616161';
    }
  };

  const getStatusBgColor = (status) => {
    switch (status.toLowerCase()) {
      case 'scheduled': return '#e3f2fd';
      case 'checked-in': return '#e8f5e8';
      case 'cancelled': return '#ffebee';
      case 'completed': return '#f3e5f5';
      default: return '#f5f5f5';
    }
  };

  // Content for different tabs
  const renderTabContent = () => {
    switch(tabValue) {
      case 0:
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ mb: 2, color: '#2c5aa0' }}>Dashboard</Typography>
            <Typography variant="body1" color="text.secondary">
              Welcome to the EMR Dashboard. Select a tab to view different sections.
            </Typography>
          </Box>
        );
      case 1:
        return (
          <Box sx={{ p: 3 }}>
            {/* Header with Schedule Button */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#2c5aa0' }}>
                Appointment Scheduling
              </Typography>
              <Button
                variant="contained"
                size="large"
                startIcon={<Schedule />}
                onClick={handleAppointmentModalOpen}
                sx={{
                  bgcolor: '#2c5aa0',
                  borderRadius: '10px',
                  px: 3,
                  py: 1.5,
                  textTransform: 'none',
                  fontSize: '16px',
                  '&:hover': {
                    bgcolor: '#1e3a6f',
                    transform: 'translateY(-1px)'
                  }
                }}
              >
                Schedule Appointment
              </Button>
            </Box>

            {/* Appointments Table */}
            <Card sx={{ 
              borderRadius: '12px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <TableContainer>
                <Table sx={{ minWidth: 650 }}>
                  <TableHead sx={{ bgcolor: '#f8f9fc' }}>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Date & Time</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Appointment Type</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Patient Name</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Date of Birth</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Contact Details</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Provider Name</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Reason for Visit</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', color: '#374151' }}>Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {appointments.map((appointment) => (
                      <TableRow
                        key={appointment.id}
                        sx={{
                          '&:hover': {
                            bgcolor: '#f8f9fc',
                            transform: 'translateY(-1px)',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                          },
                          transition: 'all 0.2s ease-in-out'
                        }}
                      >
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {appointment.date}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {appointment.time}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={appointment.type}
                            size="small"
                            sx={{
                              bgcolor: appointment.type === 'New' ? '#e3f2fd' : '#f3e5f5',
                              color: appointment.type === 'New' ? '#1976d2' : '#7b1fa2',
                              fontWeight: 'medium'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {appointment.patientName}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {appointment.dob}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {appointment.contact}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {appointment.provider}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {appointment.reason}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={appointment.status}
                            size="small"
                            sx={{
                              bgcolor: getStatusBgColor(appointment.status),
                              color: getStatusColor(appointment.status),
                              fontWeight: 'medium'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Button
                              size="small"
                              variant="outlined"
                              sx={{
                                fontSize: '12px',
                                px: 2,
                                py: 0.5,
                                borderColor: '#2c5aa0',
                                color: '#2c5aa0',
                                '&:hover': {
                                  bgcolor: '#e3f2fd'
                                }
                              }}
                            >
                              Start
                            </Button>
                            <IconButton
                              size="small"
                              sx={{
                                color: '#6b7280',
                                '&:hover': { bgcolor: '#f3f4f6' }
                              }}
                            >
                              <Edit fontSize="small" />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Card>
          </Box>
        );
      case 2:
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ mb: 2, color: '#2c5aa0' }}>Patients</Typography>
            <Typography variant="body1" color="text.secondary">
              Patient management and records will be displayed here.
            </Typography>
          </Box>
        );
      case 3:
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ mb: 2, color: '#2c5aa0' }}>Communications</Typography>
            <Typography variant="body1" color="text.secondary">
              Messages and communication tools will be available here.
            </Typography>
          </Box>
        );
      case 4:
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ mb: 2, color: '#2c5aa0' }}>Billing</Typography>
            <Typography variant="body1" color="text.secondary">
              Billing and payment management will be displayed here.
            </Typography>
          </Box>
        );
      case 5:
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ mb: 2, color: '#2c5aa0' }}>Referral</Typography>
            <Typography variant="body1" color="text.secondary">
              Referral management system will be available here.
            </Typography>
          </Box>
        );
      case 6:
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ mb: 2, color: '#2c5aa0' }}>Reports</Typography>
            <Typography variant="body1" color="text.secondary">
              Analytics and reports will be displayed here.
            </Typography>
          </Box>
        );
      case 7:
        return (
          // Settings content - Provider Availability and Slot Creation
          <Card sx={{ 
            borderRadius: '12px',
            overflow: 'hidden',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            border: '1px solid #e5e7eb'
          }}>
            {/* Provider Selection Header */}
            <Box sx={{ 
              bgcolor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
              background: 'linear-gradient(135deg, #2c5aa0 0%, #1e3a6f 100%)',
              p: 3, 
              borderBottom: '1px solid #e9ecef',
              display: 'flex',
              alignItems: 'center',
              gap: 3
            }}>
              <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold', minWidth: '80px' }}>
                Provider
              </Typography>
              <FormControl size="medium" sx={{ minWidth: 300 }}>
                <Select
                  value={selectedProvider}
                  onChange={handleProviderChange}
                  displayEmpty
                  disabled={loading}
                  sx={{ 
                    bgcolor: 'white',
                    borderRadius: '8px',
                    '& .MuiSelect-select': { py: 1.5 }
                  }}
                  startAdornment={loading && <CircularProgress size={20} sx={{ mr: 1 }} />}
                >
                  {providers.length === 0 ? (
                    <MenuItem value="" disabled>
                      {loading ? 'Loading providers...' : 'No providers available'}
                    </MenuItem>
                  ) : (
                    providers.map((provider) => (
                      <MenuItem key={provider.id || provider.name} value={provider.id || provider.name}>
                        <Box>
                          <Typography variant="body1" fontWeight="medium">
                            {provider.name || provider}
                          </Typography>
                          {provider.specialization && (
                            <Typography variant="caption" color="text.secondary">
                              {provider.specialization}
                            </Typography>
                          )}
                        </Box>
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Box>

            {/* Main Content Grid */}
            <Box sx={{ p: 3 }}>
              <Grid container spacing={4}>
                {/* Left Side - Day Wise Availability */}
                <Grid item xs={12} md={6}>
                  <Box sx={{ 
                    bgcolor: '#f8f9fc',
                    borderRadius: '12px',
                    p: 3,
                    border: '1px solid #e5e7eb'
                  }}>
                    <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', color: '#2c5aa0', display: 'flex', alignItems: 'center' }}>
                      <CalendarToday sx={{ mr: 1 }} />
                      Day Wise Availability
                    </Typography>
                    
                    <Box sx={{ display: 'flex', gap: 2, mb: 3, fontSize: '14px', fontWeight: 'bold', color: '#666', px: 1 }}>
                      <Box sx={{ minWidth: '120px' }}>Day</Box>
                      <Box sx={{ minWidth: '100px' }}>From</Box>
                      <Box sx={{ minWidth: '100px' }}>Till</Box>
                      <Box sx={{ minWidth: '60px' }}>Actions</Box>
                    </Box>

                    {weekDays.map((dayData, index) => (
                      <Card key={index} sx={{ 
                        mb: 2, 
                        p: 2,
                        bgcolor: dayData.enabled ? 'white' : '#f5f5f5',
                        border: dayData.enabled ? '1px solid #e5e7eb' : '1px solid #d1d5db',
                        borderRadius: '8px',
                        opacity: dayData.enabled ? 1 : 0.7,
                        transition: 'all 0.2s ease-in-out',
                        '&:hover': {
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                          transform: 'translateY(-1px)'
                        }
                      }}>
                        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                          <Typography variant="body1" sx={{ 
                            minWidth: '120px', 
                            fontWeight: 'medium',
                            color: dayData.enabled ? '#1f2937' : '#6b7280'
                          }}>
                            {dayData.day}
                          </Typography>
                          
                          <TextField
                            size="small"
                            type="time"
                            value={dayData.from}
                            disabled={!dayData.enabled}
                            onChange={(e) => updateWeekDay(index, 'from', e.target.value)}
                            sx={{ 
                              minWidth: '100px',
                              '& .MuiInputBase-input': { fontSize: '14px' }
                            }}
                          />
                          
                          <TextField
                            size="small"
                            type="time"
                            value={dayData.till}
                            disabled={!dayData.enabled}
                            onChange={(e) => updateWeekDay(index, 'till', e.target.value)}
                            sx={{ 
                              minWidth: '100px',
                              '& .MuiInputBase-input': { fontSize: '14px' }
                            }}
                          />
                          
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton 
                              size="small" 
                              sx={{ 
                                color: dayData.enabled ? '#10b981' : '#6b7280',
                                '&:hover': { bgcolor: dayData.enabled ? '#ecfdf5' : '#f3f4f6' }
                              }}
                              onClick={() => updateWeekDay(index, 'enabled', !dayData.enabled)}
                            >
                              {dayData.enabled ? <Save fontSize="small" /> : <Edit fontSize="small" />}
                            </IconButton>
                            <IconButton 
                              size="small" 
                              sx={{ 
                                color: '#ef4444',
                                '&:hover': { bgcolor: '#fef2f2' }
                              }}
                            >
                              <Delete fontSize="small" />
                            </IconButton>
                          </Box>
                        </Box>
                      </Card>
                    ))}
                  </Box>
                </Grid>

                {/* Right Side - Slot Creation Setting */}
                <Grid item xs={12} md={6}>
                  <Box sx={{ 
                    bgcolor: '#f8f9fc',
                    borderRadius: '12px',
                    p: 3,
                    border: '1px solid #e5e7eb'
                  }}>
                    <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', color: '#2c5aa0', display: 'flex', alignItems: 'center' }}>
                      <Settings sx={{ mr: 1 }} />
                      Slot Creation Setting
                    </Typography>
                    
                    {/* Time Zone */}
                    <Card sx={{ p: 3, mb: 3, border: '1px solid #e5e7eb', borderRadius: '8px' }}>
                      <Typography variant="body1" sx={{ mb: 2, fontWeight: 'medium', color: '#374151' }}>
                        Time Zone Configuration
                      </Typography>
                      <FormControl fullWidth size="medium">
                        <InputLabel>Time Zone</InputLabel>
                        <Select
                          value={timeZone}
                          label="Time Zone"
                          onChange={(e) => setTimeZone(e.target.value)}
                          sx={{ 
                            borderRadius: '8px',
                            '& .MuiSelect-select': { py: 1.5 }
                          }}
                        >
                          <MenuItem value="UTC-05:00">Eastern Standard Time (EST)</MenuItem>
                          <MenuItem value="UTC-08:00">Pacific Standard Time (PST)</MenuItem>
                          <MenuItem value="UTC-06:00">Central Standard Time (CST)</MenuItem>
                          <MenuItem value="UTC-07:00">Mountain Standard Time (MST)</MenuItem>
                          <MenuItem value="UTC+00:00">Coordinated Universal Time (UTC)</MenuItem>
                        </Select>
                      </FormControl>
                    </Card>

                    {/* Block Days */}
                    <Card sx={{ p: 3, border: '1px solid #e5e7eb', borderRadius: '8px' }}>
                      <Typography variant="body1" sx={{ mb: 3, fontWeight: 'medium', color: '#374151' }}>
                        Block Days Management
                      </Typography>
                      
                      {blockDays.map((blockDay, index) => (
                        <Card key={index} sx={{ 
                          mb: 2, 
                          p: 2,
                          bgcolor: '#fafafa',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          transition: 'all 0.2s ease-in-out',
                          '&:hover': {
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                            transform: 'translateY(-1px)'
                          }
                        }}>
                          <Grid container spacing={2} alignItems="center">
                            <Grid item xs={12} sm={4}>
                              <TextField
                                fullWidth
                                size="small"
                                type="date"
                                label="Date"
                                value={blockDay.date}
                                onChange={(e) => updateBlockDay(index, 'date', e.target.value)}
                                sx={{ 
                                  '& .MuiInputBase-input': { fontSize: '14px' }
                                }}
                              />
                            </Grid>
                            
                            <Grid item xs={6} sm={3}>
                              <TextField
                                fullWidth
                                size="small"
                                type="time"
                                label="From"
                                value={blockDay.fromTime}
                                onChange={(e) => updateBlockDay(index, 'fromTime', e.target.value)}
                                sx={{ 
                                  '& .MuiInputBase-input': { fontSize: '14px' }
                                }}
                              />
                            </Grid>
                            
                            <Grid item xs={6} sm={3}>
                              <TextField
                                fullWidth
                                size="small"
                                type="time"
                                label="Till"
                                value={blockDay.tillTime}
                                onChange={(e) => updateBlockDay(index, 'tillTime', e.target.value)}
                                sx={{ 
                                  '& .MuiInputBase-input': { fontSize: '14px' }
                                }}
                              />
                            </Grid>
                            
                            <Grid item xs={12} sm={2}>
                              <IconButton 
                                size="small" 
                                sx={{ 
                                  color: '#ef4444',
                                  '&:hover': { bgcolor: '#fef2f2' }
                                }}
                                onClick={() => removeBlockDay(index)}
                              >
                                <Delete fontSize="small" />
                              </IconButton>
                            </Grid>
                          </Grid>
                        </Card>
                      ))}

                      {/* Add Block Days Button */}
                      <Button
                        variant="contained"
                        size="medium"
                        startIcon={<Add />}
                        onClick={addBlockDay}
                        sx={{ 
                          mt: 2,
                          textTransform: 'none',
                          fontSize: '14px',
                          bgcolor: '#2c5aa0',
                          borderRadius: '8px',
                          '&:hover': {
                            bgcolor: '#1e3a6f'
                          }
                        }}
                        fullWidth
                      >
                        Add Block Days
                      </Button>
                    </Card>
                  </Box>
                </Grid>
              </Grid>

              {/* Action Buttons */}
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'flex-end', 
                gap: 3, 
                mt: 5, 
                pt: 4,
                borderTop: '2px solid #f1f5f9'
              }}>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<Cancel />}
                  sx={{ 
                    textTransform: 'none',
                    fontSize: '16px',
                    px: 4,
                    py: 1.5,
                    borderColor: '#6b7280',
                    color: '#6b7280',
                    borderRadius: '10px',
                    '&:hover': {
                      borderColor: '#4b5563',
                      bgcolor: 'rgba(107, 114, 128, 0.04)',
                      transform: 'translateY(-1px)'
                    }
                  }}
                >
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Save />}
                  onClick={handleSave}
                  disabled={loading}
                  sx={{ 
                    textTransform: 'none',
                    fontSize: '16px',
                    px: 4,
                    py: 1.5,
                    bgcolor: '#2c5aa0',
                    borderRadius: '10px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    '&:hover': {
                      bgcolor: '#1e3a6f',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 6px 8px -1px rgba(0, 0, 0, 0.15)'
                    }
                  }}
                >
                  {loading ? 'Saving...' : 'Save Settings'}
                </Button>
              </Box>
            </Box>
          </Card>
        );
      default:
        return (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h4" sx={{ mb: 2, color: '#2c5aa0' }}>Welcome</Typography>
            <Typography variant="body1" color="text.secondary">
              Select a tab to view content.
            </Typography>
          </Box>
        );
    }
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f5f7fa' }}>
      {/* Top Navigation Bar */}
      <AppBar position="static" sx={{ bgcolor: '#2c5aa0', boxShadow: 'none' }}>
        <Toolbar sx={{ minHeight: '56px !important' }}>
          <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 4, fontSize: '16px' }}>
            EMR
          </Typography>
          
          {/* Navigation Tabs */}
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange}
            sx={{ 
              flexGrow: 1,
              '& .MuiTab-root': { 
                color: 'rgba(255,255,255,0.7)', 
                minHeight: '56px',
                fontSize: '14px',
                textTransform: 'none',
                fontWeight: 'normal'
              },
              '& .Mui-selected': { 
                color: 'white !important',
                fontWeight: 'bold'
              },
              '& .MuiTabs-indicator': { 
                backgroundColor: 'white',
                height: '3px'
              }
            }}
          >
            <Tab label="Dashboard" />
            <Tab label="Scheduling" />
            <Tab label="Patients" />
            <Tab label="Communications" />
            <Tab label="Billing" />
            <Tab label="Referral" />
            <Tab label="Reports" />
            <Tab label="Settings" />
          </Tabs>

          {/* Right side icons */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit">
              <Search />
            </IconButton>
            <IconButton color="inherit">
              <Badge badgeContent={1} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            <IconButton
              color="inherit"
              onClick={handleProfileMenuOpen}
              sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
            >
              <AccountCircle />
              <ExpandMore />
            </IconButton>
          </Box>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
            <MenuItem onClick={handleMenuClose}>Settings</MenuItem>
            <MenuItem onClick={handleMenuClose}>Logout</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ p: 3, minHeight: 'calc(100vh - 56px)' }}>
        {renderTabContent()}
      </Box>

      {/* Schedule Appointment Modal */}
      <Modal
        open={appointmentModal}
        onClose={handleAppointmentModalClose}
        sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      >
        <Box sx={{
          bgcolor: 'white',
          borderRadius: '16px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          p: 0,
          width: '90%',
          maxWidth: '800px',
          maxHeight: '90vh',
          overflow: 'auto'
        }}>
          {/* Modal Header */}
          <Box sx={{
            bgcolor: 'linear-gradient(135deg, #2c5aa0 0%, #1e3a6f 100%)',
            background: 'linear-gradient(135deg, #2c5aa0 0%, #1e3a6f 100%)',
            p: 3,
            borderRadius: '16px 16px 0 0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <Typography variant="h5" sx={{ color: 'white', fontWeight: 'bold' }}>
              Schedule New Appointment
            </Typography>
            <IconButton
              onClick={handleAppointmentModalClose}
              sx={{ color: 'white', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}
            >
              <Close />
            </IconButton>
          </Box>

          {/* Modal Content */}
          <Box sx={{ p: 4 }}>
            <Grid container spacing={3}>
              {/* Patient Information */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, color: '#2c5aa0', display: 'flex', alignItems: 'center' }}>
                  <Person sx={{ mr: 1 }} />
                  Patient Information
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Patient ID"
                  value={newAppointment.patient_id}
                  onChange={(e) => updateAppointmentField('patient_id', e.target.value)}
                  placeholder="3fa85f64-5717-4562-b3fc-2c963f66afa6"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Provider</InputLabel>
                  <Select
                    value={newAppointment.provider_id}
                    label="Provider"
                    onChange={(e) => updateAppointmentField('provider_id', e.target.value)}
                  >
                    {providers.map((provider) => (
                      <MenuItem key={provider.id || provider.name} value={provider.id || provider.name}>
                        {provider.name || provider}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              {/* Appointment Details */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, mt: 2, color: '#2c5aa0', display: 'flex', alignItems: 'center' }}>
                  <Schedule sx={{ mr: 1 }} />
                  Appointment Details
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Appointment Date"
                  value={newAppointment.appointment_date}
                  onChange={(e) => updateAppointmentField('appointment_date', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="time"
                  label="Appointment Time"
                  value={newAppointment.appointment_time}
                  onChange={(e) => updateAppointmentField('appointment_time', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Appointment Type</InputLabel>
                  <Select
                    value={newAppointment.appointment_type}
                    label="Appointment Type"
                    onChange={(e) => updateAppointmentField('appointment_type', e.target.value)}
                  >
                    <MenuItem value="consultation">Consultation</MenuItem>
                    <MenuItem value="follow_up">Follow Up</MenuItem>
                    <MenuItem value="emergency">Emergency</MenuItem>
                    <MenuItem value="routine_checkup">Routine Checkup</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <FormLabel>Appointment Mode</FormLabel>
                  <RadioGroup
                    value={newAppointment.appointment_mode}
                    onChange={(e) => updateAppointmentField('appointment_mode', e.target.value)}
                    row
                  >
                    <FormControlLabel value="in_person" control={<Radio />} label="In Person" />
                    <FormControlLabel value="video_call" control={<Radio />} label="Video Call" />
                  </RadioGroup>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Duration (minutes)"
                  value={newAppointment.duration_minutes}
                  onChange={(e) => updateAppointmentField('duration_minutes', parseInt(e.target.value))}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Timezone"
                  value={newAppointment.timezone}
                  onChange={(e) => updateAppointmentField('timezone', e.target.value)}
                />
              </Grid>

              {/* Medical Information */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, mt: 2, color: '#2c5aa0', display: 'flex', alignItems: 'center' }}>
                  <EventNote sx={{ mr: 1 }} />
                  Medical Information
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Reason for Visit"
                  value={newAppointment.reason_for_visit}
                  onChange={(e) => updateAppointmentField('reason_for_visit', e.target.value)}
                  placeholder="Routine check-up and general health consultation"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Symptoms"
                  value={newAppointment.symptoms}
                  onChange={(e) => updateAppointmentField('symptoms', e.target.value)}
                  placeholder="Fatigue, mild headaches, and dizziness"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Special Instructions"
                  value={newAppointment.special_instructions}
                  onChange={(e) => updateAppointmentField('special_instructions', e.target.value)}
                  placeholder="Patient prefers early appointments; allergic to penicillin"
                />
              </Grid>

              {/* Emergency Contact */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, mt: 2, color: '#2c5aa0', display: 'flex', alignItems: 'center' }}>
                  <Phone sx={{ mr: 1 }} />
                  Emergency Contact
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Emergency Contact Name"
                  value={newAppointment.emergency_contact_name}
                  onChange={(e) => updateAppointmentField('emergency_contact_name', e.target.value)}
                  placeholder="Jane Doe"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Emergency Contact Phone"
                  value={newAppointment.emergency_contact_phone}
                  onChange={(e) => updateAppointmentField('emergency_contact_phone', e.target.value)}
                  placeholder="+1-555-123-4567"
                />
              </Grid>

              {/* Payment Information */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, mt: 2, color: '#2c5aa0', display: 'flex', alignItems: 'center' }}>
                  <AttachMoney sx={{ mr: 1 }} />
                  Payment Information
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Estimated Amount"
                  value={newAppointment.estimated_amount}
                  onChange={(e) => updateAppointmentField('estimated_amount', e.target.value)}
                  placeholder="120.00"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={newAppointment.currency}
                    label="Currency"
                    onChange={(e) => updateAppointmentField('currency', e.target.value)}
                  >
                    <MenuItem value="USD">USD</MenuItem>
                    <MenuItem value="EUR">EUR</MenuItem>
                    <MenuItem value="GBP">GBP</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              {/* Location Details */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, mt: 2, color: '#2c5aa0', display: 'flex', alignItems: 'center' }}>
                  <LocationOn sx={{ mr: 1 }} />
                  Location Details
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Clinic Name"
                  value={newAppointment.location_details.clinic_name}
                  onChange={(e) => updateAppointmentField('location_details.clinic_name', e.target.value)}
                  placeholder="Downtown Health Clinic"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Address"
                  value={newAppointment.location_details.address}
                  onChange={(e) => updateAppointmentField('location_details.address', e.target.value)}
                  placeholder="123 Main Street, Suite 400"
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="City"
                  value={newAppointment.location_details.city}
                  onChange={(e) => updateAppointmentField('location_details.city', e.target.value)}
                  placeholder="New York"
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="State"
                  value={newAppointment.location_details.state}
                  onChange={(e) => updateAppointmentField('location_details.state', e.target.value)}
                  placeholder="NY"
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Zipcode"
                  value={newAppointment.location_details.zipcode}
                  onChange={(e) => updateAppointmentField('location_details.zipcode', e.target.value)}
                  placeholder="10001"
                />
              </Grid>

              {/* Video Call Link (conditional) */}
              {newAppointment.appointment_mode === 'video_call' && (
                <Grid item xs={12}>
                  <Typography variant="h6" sx={{ mb: 2, mt: 2, color: '#2c5aa0', display: 'flex', alignItems: 'center' }}>
                    <VideoCall sx={{ mr: 1 }} />
                    Video Call Information
                  </Typography>
                  <TextField
                    fullWidth
                    label="Video Call Link"
                    value={newAppointment.video_call_link}
                    onChange={(e) => updateAppointmentField('video_call_link', e.target.value)}
                    placeholder="https://telehealth.example.com/meet/abc123"
                  />
                </Grid>
              )}
            </Grid>

            {/* Modal Actions */}
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'flex-end', 
              gap: 2, 
              mt: 4, 
              pt: 3,
              borderTop: '2px solid #f1f5f9'
            }}>
              <Button
                variant="outlined"
                size="large"
                onClick={handleAppointmentModalClose}
                sx={{
                  px: 4,
                  py: 1.5,
                  borderColor: '#6b7280',
                  color: '#6b7280',
                  borderRadius: '10px',
                  textTransform: 'none'
                }}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                size="large"
                onClick={createAppointment}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Save />}
                sx={{
                  px: 4,
                  py: 1.5,
                  bgcolor: '#2c5aa0',
                  borderRadius: '10px',
                  textTransform: 'none',
                  '&:hover': {
                    bgcolor: '#1e3a6f'
                  }
                }}
              >
                {loading ? 'Saving...' : 'Save & Close'}
              </Button>
            </Box>
          </Box>
        </Box>
      </Modal>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default EMRDashboard;
