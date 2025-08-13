import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  IconButton, 
  FormControl,
  FormControlLabel,
  FormHelperText,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  Divider,
  Grid,
  Switch,
  Tooltip,
  CircularProgress
} from '@mui/material';
import { 
  Close, 
  EventAvailable,
  EventRepeat,
  AccessTime,
  Notes,
  Save
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker, TimePicker } from '@mui/x-date-pickers';
import { format, addMinutes, isBefore, isAfter, setHours, setMinutes } from 'date-fns';

// Import mock data
import { appointmentTypes, slotDurations, recurringOptions } from '../../data/mockAvailabilityData';

// Validation schema
const availabilitySchema = Yup.object().shape({
  date: Yup.date()
    .required('Date is required')
    .min(new Date(), 'Date cannot be in the past'),
  startTime: Yup.date()
    .required('Start time is required'),
  endTime: Yup.date()
    .required('End time is required')
    .test('is-after-start', 'End time must be after start time', function(endTime) {
      const { startTime } = this.parent;
      if (!startTime || !endTime) return true;
      return isAfter(endTime, startTime);
    }),
  appointmentTypeId: Yup.number()
    .required('Appointment type is required'),
  slotDuration: Yup.number()
    .required('Slot duration is required'),
  notes: Yup.string()
    .max(200, 'Notes cannot exceed 200 characters'),
  recurring: Yup.string(),
  isEmergency: Yup.boolean(),
  bufferTime: Yup.number()
    .min(0, 'Buffer time cannot be negative')
    .max(60, 'Buffer time cannot exceed 60 minutes')
});

const AddAvailabilityForm = ({ onClose, onSubmit, selectedDate }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  // Initialize form with selected date
  const initialDate = selectedDate || new Date();
  const initialStartTime = setHours(setMinutes(new Date(), 0), 9); // 9:00 AM
  const initialEndTime = setHours(setMinutes(new Date(), 0), 17); // 5:00 PM
  
  const formik = useFormik({
    initialValues: {
      date: initialDate,
      startTime: initialStartTime,
      endTime: initialEndTime,
      appointmentTypeId: 1, // Default to General Consultation
      slotDuration: 30, // Default to 30 minutes
      notes: '',
      recurring: 'none',
      isEmergency: false,
      bufferTime: 0
    },
    validationSchema: availabilitySchema,
    onSubmit: (values) => {
      setIsLoading(true);
      
      // Create a new availability object
      const newAvailability = {
        id: Date.now(), // Generate a unique ID
        title: values.isEmergency ? 'Emergency Slot' : 'Available',
        start: new Date(values.date.setHours(
          values.startTime.getHours(),
          values.startTime.getMinutes(),
          0,
          0
        )),
        end: new Date(values.date.setHours(
          values.endTime.getHours(),
          values.endTime.getMinutes(),
          0,
          0
        )),
        type: values.isEmergency ? 'emergency' : 'available',
        appointmentType: appointmentTypes.find(type => type.id === values.appointmentTypeId)?.name,
        slotDuration: values.slotDuration,
        notes: values.notes,
        recurring: values.recurring !== 'none',
        recurringPattern: values.recurring,
        bufferTime: values.bufferTime
      };
      
      // Simulate API call
      setTimeout(() => {
        onSubmit(newAvailability);
        setIsLoading(false);
      }, 1000);
    }
  });
  
  // Handle appointment type change
  const handleAppointmentTypeChange = (event) => {
    const typeId = event.target.value;
    formik.setFieldValue('appointmentTypeId', typeId);
    
    // Update slot duration based on appointment type
    const selectedType = appointmentTypes.find(type => type.id === typeId);
    if (selectedType) {
      formik.setFieldValue('slotDuration', selectedType.duration);
    }
  };
  
  // Calculate number of slots
  const calculateSlots = () => {
    const { startTime, endTime, slotDuration, bufferTime } = formik.values;
    if (!startTime || !endTime || !slotDuration) return 0;
    
    const totalMinutes = (endTime.getHours() * 60 + endTime.getMinutes()) - 
                         (startTime.getHours() * 60 + startTime.getMinutes());
    
    const effectiveSlotDuration = slotDuration + bufferTime;
    return Math.floor(totalMinutes / effectiveSlotDuration);
  };

  return (
    <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <EventAvailable sx={{ color: '#3b82f6', mr: 1 }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Add Availability
          </Typography>
        </Box>
        <IconButton onClick={onClose}>
          <Close />
        </IconButton>
      </Box>
      
      <Divider sx={{ mb: 3 }} />
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <form onSubmit={formik.handleSubmit}>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <DatePicker
                  label="Date"
                  value={formik.values.date}
                  onChange={(newValue) => {
                    formik.setFieldValue('date', newValue);
                  }}
                  renderInput={(params) => (
                    <TextField 
                      {...params} 
                      fullWidth
                      error={formik.touched.date && Boolean(formik.errors.date)}
                      helperText={formik.touched.date && formik.errors.date}
                    />
                  )}
                  disablePast
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TimePicker
                  label="Start Time"
                  value={formik.values.startTime}
                  onChange={(newValue) => {
                    formik.setFieldValue('startTime', newValue);
                  }}
                  renderInput={(params) => (
                    <TextField 
                      {...params} 
                      fullWidth
                      error={formik.touched.startTime && Boolean(formik.errors.startTime)}
                      helperText={formik.touched.startTime && formik.errors.startTime}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TimePicker
                  label="End Time"
                  value={formik.values.endTime}
                  onChange={(newValue) => {
                    formik.setFieldValue('endTime', newValue);
                  }}
                  renderInput={(params) => (
                    <TextField 
                      {...params} 
                      fullWidth
                      error={formik.touched.endTime && Boolean(formik.errors.endTime)}
                      helperText={formik.touched.endTime && formik.errors.endTime}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControl fullWidth error={formik.touched.appointmentTypeId && Boolean(formik.errors.appointmentTypeId)}>
                  <InputLabel>Appointment Type</InputLabel>
                  <Select
                    value={formik.values.appointmentTypeId}
                    onChange={handleAppointmentTypeChange}
                    label="Appointment Type"
                  >
                    {appointmentTypes.map((type) => (
                      <MenuItem key={type.id} value={type.id}>
                        {type.name} ({type.duration} min)
                      </MenuItem>
                    ))}
                  </Select>
                  {formik.touched.appointmentTypeId && formik.errors.appointmentTypeId && (
                    <FormHelperText>{formik.errors.appointmentTypeId}</FormHelperText>
                  )}
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <FormControl fullWidth error={formik.touched.slotDuration && Boolean(formik.errors.slotDuration)}>
                  <InputLabel>Slot Duration</InputLabel>
                  <Select
                    value={formik.values.slotDuration}
                    onChange={(e) => formik.setFieldValue('slotDuration', e.target.value)}
                    label="Slot Duration"
                  >
                    {slotDurations.map((duration) => (
                      <MenuItem key={duration.value} value={duration.value}>
                        {duration.label}
                      </MenuItem>
                    ))}
                  </Select>
                  {formik.touched.slotDuration && formik.errors.slotDuration && (
                    <FormHelperText>{formik.errors.slotDuration}</FormHelperText>
                  )}
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="bufferTime"
                  name="bufferTime"
                  label="Buffer Time (minutes)"
                  type="number"
                  value={formik.values.bufferTime}
                  onChange={formik.handleChange}
                  error={formik.touched.bufferTime && Boolean(formik.errors.bufferTime)}
                  helperText={formik.touched.bufferTime && formik.errors.bufferTime}
                  InputProps={{ inputProps: { min: 0, max: 60 } }}
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Recurring</InputLabel>
                  <Select
                    value={formik.values.recurring}
                    onChange={(e) => formik.setFieldValue('recurring', e.target.value)}
                    label="Recurring"
                  >
                    {recurringOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="notes"
                  name="notes"
                  label="Notes"
                  multiline
                  rows={3}
                  value={formik.values.notes}
                  onChange={formik.handleChange}
                  error={formik.touched.notes && Boolean(formik.errors.notes)}
                  helperText={formik.touched.notes && formik.errors.notes}
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.isEmergency}
                      onChange={(e) => formik.setFieldValue('isEmergency', e.target.checked)}
                      color="error"
                    />
                  }
                  label="Emergency Slot"
                />
                <FormHelperText>
                  Mark this as an emergency slot for urgent appointments only
                </FormHelperText>
              </Grid>
            </Grid>
          </LocalizationProvider>
          
          <Box sx={{ bgcolor: '#f0f9ff', p: 2, borderRadius: 1, mt: 3 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
              Summary
            </Typography>
            <Grid container spacing={1}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Date:
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {format(formik.values.date, 'EEEE, MMMM d, yyyy')}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Time:
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {format(formik.values.startTime, 'h:mm a')} - {format(formik.values.endTime, 'h:mm a')}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Appointment Type:
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {appointmentTypes.find(type => type.id === formik.values.appointmentTypeId)?.name}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Slot Duration:
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {formik.values.slotDuration} minutes
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  Number of Slots:
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {calculateSlots()} slots
                </Typography>
              </Grid>
            </Grid>
          </Box>
        </form>
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 3 }}>
        <Button 
          variant="outlined" 
          onClick={onClose}
        >
          Cancel
        </Button>
        <Button 
          variant="contained" 
          onClick={formik.handleSubmit}
          disabled={isLoading}
          startIcon={isLoading ? <CircularProgress size={20} /> : <Save />}
          sx={{ 
            bgcolor: '#3b82f6',
            '&:hover': {
              bgcolor: '#2563eb',
            }
          }}
        >
          {isLoading ? 'Saving...' : 'Save Availability'}
        </Button>
      </Box>
    </Box>
  );
};

export default AddAvailabilityForm;
