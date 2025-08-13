import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  FormControl,
  FormGroup,
  FormControlLabel,
  Checkbox,
  TextField,
  Button,
  Divider,
  IconButton,
  Chip,
  Stack,
  Alert,
  Switch,
  MenuItem,
  Select,
  InputLabel,
  Card,
  CardContent,
  CardHeader,
  Tooltip
} from '@mui/material';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon, 
  Save as SaveIcon,
  Info as InfoIcon,
  EventBusy as EventBusyIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';

const weekDays = [
  { name: 'Monday', value: 'monday' },
  { name: 'Tuesday', value: 'tuesday' },
  { name: 'Wednesday', value: 'wednesday' },
  { name: 'Thursday', value: 'thursday' },
  { name: 'Friday', value: 'friday' },
  { name: 'Saturday', value: 'saturday' },
  { name: 'Sunday', value: 'sunday' },
];

const timeSlots = Array.from({ length: 24 * 2 }, (_, i) => {
  const hour = Math.floor(i / 2);
  const minute = i % 2 === 0 ? '00' : '30';
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const hour12 = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return `${hour12}:${minute} ${ampm}`;
});

const AvailabilityPage = () => {
  const [weeklySchedule, setWeeklySchedule] = useState(
    weekDays.map(day => ({
      day: day.value,
      enabled: day.value !== 'saturday' && day.value !== 'sunday',
      slots: [{ start: '9:00 AM', end: '5:00 PM' }]
    }))
  );
  
  const [blockedDates, setBlockedDates] = useState([
    { date: new Date(), reason: 'Personal Leave' }
  ]);
  
  const [newBlockedDate, setNewBlockedDate] = useState(null);
  const [newBlockReason, setNewBlockReason] = useState('');
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  // Handle day toggle
  const handleDayToggle = (dayValue) => {
    setWeeklySchedule(prev => 
      prev.map(day => 
        day.day === dayValue ? { ...day, enabled: !day.enabled } : day
      )
    );
  };
  
  // Handle time slot change
  const handleTimeChange = (dayValue, slotIndex, field, value) => {
    setWeeklySchedule(prev => 
      prev.map(day => {
        if (day.day === dayValue) {
          const updatedSlots = [...day.slots];
          updatedSlots[slotIndex] = { 
            ...updatedSlots[slotIndex], 
            [field]: value 
          };
          return { ...day, slots: updatedSlots };
        }
        return day;
      })
    );
  };
  
  // Add new time slot to a day
  const addTimeSlot = (dayValue) => {
    setWeeklySchedule(prev => 
      prev.map(day => {
        if (day.day === dayValue) {
          return { 
            ...day, 
            slots: [...day.slots, { start: '9:00 AM', end: '5:00 PM' }] 
          };
        }
        return day;
      })
    );
  };
  
  // Remove time slot from a day
  const removeTimeSlot = (dayValue, slotIndex) => {
    setWeeklySchedule(prev => 
      prev.map(day => {
        if (day.day === dayValue && day.slots.length > 1) {
          const updatedSlots = [...day.slots];
          updatedSlots.splice(slotIndex, 1);
          return { ...day, slots: updatedSlots };
        }
        return day;
      })
    );
  };
  
  // Add blocked date
  const addBlockedDate = () => {
    if (newBlockedDate && newBlockReason) {
      setBlockedDates([
        ...blockedDates, 
        { date: newBlockedDate, reason: newBlockReason }
      ]);
      setNewBlockedDate(null);
      setNewBlockReason('');
    }
  };
  
  // Remove blocked date
  const removeBlockedDate = (index) => {
    const updatedBlockedDates = [...blockedDates];
    updatedBlockedDates.splice(index, 1);
    setBlockedDates(updatedBlockedDates);
  };
  
  // Save availability settings
  const saveAvailability = () => {
    // Here you would typically send the data to your backend API
    console.log('Weekly Schedule:', weeklySchedule);
    console.log('Blocked Dates:', blockedDates);
    
    // Show success message
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };
  
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        {/* Page Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600, mb: 1 }}>
            Availability Settings
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Set your regular working hours and block out dates when you're unavailable
          </Typography>
        </Box>
        
        {saveSuccess && (
          <Alert severity="success" sx={{ mb: 3 }}>
            Your availability settings have been saved successfully!
          </Alert>
        )}
        
        <Grid container spacing={3}>
          {/* Weekly Schedule Section */}
          <Grid item xs={12} lg={8}>
            <Card elevation={0} sx={{ mb: 4, borderRadius: 2 }}>
              <CardHeader 
                title={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AccessTimeIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6">Weekly Schedule</Typography>
                  </Box>
                }
                sx={{ pb: 0 }}
              />
              <CardContent>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Set your regular working hours for each day of the week
                </Typography>
                
                {weeklySchedule.map((day) => (
                  <Paper 
                    key={day.day} 
                    elevation={0} 
                    sx={{ 
                      p: 2, 
                      mb: 2, 
                      borderRadius: 2,
                      backgroundColor: day.enabled ? 'white' : '#f5f5f5',
                      border: '1px solid',
                      borderColor: day.enabled ? 'primary.light' : 'divider'
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={day.enabled} 
                            onChange={() => handleDayToggle(day.day)}
                            color="primary"
                          />
                        }
                        label={
                          <Typography 
                            variant="subtitle1" 
                            sx={{ 
                              fontWeight: 600,
                              color: day.enabled ? 'text.primary' : 'text.disabled'
                            }}
                          >
                            {weekDays.find(d => d.value === day.day).name}
                          </Typography>
                        }
                      />
                    </Box>
                    
                    {day.enabled && (
                      <>
                        {day.slots.map((slot, slotIndex) => (
                          <Box 
                            key={slotIndex} 
                            sx={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              mb: slotIndex < day.slots.length - 1 ? 2 : 0 
                            }}
                          >
                            <FormControl sx={{ mr: 2, minWidth: 120 }} size="small">
                              <InputLabel id={`start-time-label-${day.day}-${slotIndex}`}>
                                Start Time
                              </InputLabel>
                              <Select
                                labelId={`start-time-label-${day.day}-${slotIndex}`}
                                id={`start-time-${day.day}-${slotIndex}`}
                                value={slot.start}
                                label="Start Time"
                                onChange={(e) => handleTimeChange(day.day, slotIndex, 'start', e.target.value)}
                              >
                                {timeSlots.map((time) => (
                                  <MenuItem 
                                    key={time} 
                                    value={time}
                                    disabled={
                                      timeSlots.indexOf(time) >= 
                                      timeSlots.indexOf(slot.end)
                                    }
                                  >
                                    {time}
                                  </MenuItem>
                                ))}
                              </Select>
                            </FormControl>
                            
                            <FormControl sx={{ mr: 2, minWidth: 120 }} size="small">
                              <InputLabel id={`end-time-label-${day.day}-${slotIndex}`}>
                                End Time
                              </InputLabel>
                              <Select
                                labelId={`end-time-label-${day.day}-${slotIndex}`}
                                id={`end-time-${day.day}-${slotIndex}`}
                                value={slot.end}
                                label="End Time"
                                onChange={(e) => handleTimeChange(day.day, slotIndex, 'end', e.target.value)}
                              >
                                {timeSlots.map((time) => (
                                  <MenuItem 
                                    key={time} 
                                    value={time}
                                    disabled={
                                      timeSlots.indexOf(time) <= 
                                      timeSlots.indexOf(slot.start)
                                    }
                                  >
                                    {time}
                                  </MenuItem>
                                ))}
                              </Select>
                            </FormControl>
                            
                            <Box sx={{ display: 'flex' }}>
                              {day.slots.length > 1 && (
                                <IconButton 
                                  size="small" 
                                  onClick={() => removeTimeSlot(day.day, slotIndex)}
                                  sx={{ color: 'error.main' }}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              )}
                              
                              {slotIndex === day.slots.length - 1 && (
                                <IconButton 
                                  size="small" 
                                  onClick={() => addTimeSlot(day.day)}
                                  sx={{ color: 'primary.main' }}
                                >
                                  <AddIcon fontSize="small" />
                                </IconButton>
                              )}
                            </Box>
                          </Box>
                        ))}
                      </>
                    )}
                  </Paper>
                ))}
              </CardContent>
            </Card>
          </Grid>
          
          {/* Blocked Dates Section */}
          <Grid item xs={12} lg={4}>
            <Card elevation={0} sx={{ borderRadius: 2 }}>
              <CardHeader 
                title={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <EventBusyIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6">Blocked Dates</Typography>
                  </Box>
                }
                sx={{ pb: 0 }}
              />
              <CardContent>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Block specific dates when you're unavailable
                </Typography>
                
                {/* Add new blocked date */}
                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 2, 
                    mb: 3, 
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'primary.light',
                    backgroundColor: 'white'
                  }}
                >
                  <Typography variant="subtitle2" sx={{ mb: 2 }}>Add Blocked Date</Typography>
                  
                  <DatePicker
                    label="Select Date"
                    value={newBlockedDate}
                    onChange={(date) => setNewBlockedDate(date)}
                    renderInput={(params) => 
                      <TextField 
                        {...params} 
                        fullWidth 
                        size="small" 
                        sx={{ mb: 2 }} 
                      />
                    }
                    disablePast
                  />
                  
                  <TextField
                    fullWidth
                    label="Reason"
                    value={newBlockReason}
                    onChange={(e) => setNewBlockReason(e.target.value)}
                    size="small"
                    sx={{ mb: 2 }}
                  />
                  
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={addBlockedDate}
                    disabled={!newBlockedDate || !newBlockReason}
                    fullWidth
                  >
                    Add Blocked Date
                  </Button>
                </Paper>
                
                {/* Blocked dates list */}
                <Typography variant="subtitle2" sx={{ mb: 2 }}>
                  Blocked Dates ({blockedDates.length})
                </Typography>
                
                {blockedDates.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No blocked dates added yet
                  </Typography>
                ) : (
                  <Stack spacing={1}>
                    {blockedDates.map((blockedDate, index) => (
                      <Paper
                        key={index}
                        elevation={0}
                        sx={{
                          p: 1.5,
                          borderRadius: 2,
                          border: '1px solid',
                          borderColor: 'divider',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                      >
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {blockedDate.date.toLocaleDateString('en-US', { 
                              weekday: 'short',
                              month: 'short', 
                              day: 'numeric', 
                              year: 'numeric' 
                            })}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {blockedDate.reason}
                          </Typography>
                        </Box>
                        <IconButton 
                          size="small" 
                          onClick={() => removeBlockedDate(index)}
                          sx={{ color: 'error.main' }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Paper>
                    ))}
                  </Stack>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        
        {/* Save Button */}
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<SaveIcon />}
            onClick={saveAvailability}
            sx={{ px: 4 }}
          >
            Save Availability
          </Button>
        </Box>
      </Box>
    </LocalizationProvider>
  );
};

export default AvailabilityPage;
