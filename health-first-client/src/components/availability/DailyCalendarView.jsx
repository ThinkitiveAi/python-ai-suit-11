import React from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Grid, 
  Tooltip,
  Divider,
  IconButton,
  Button
} from '@mui/material';
import { 
  Edit,
  Delete,
  ContentCopy,
  MoreVert
} from '@mui/icons-material';
import { 
  format, 
  setHours, 
  setMinutes, 
  getHours, 
  getMinutes, 
  isSameDay,
  differenceInMinutes
} from 'date-fns';

const DailyCalendarView = ({ currentDate, availabilityData, onAddAvailability }) => {
  // Generate time slots for the day (15-minute intervals for more detailed view)
  const startHour = 7; // 7 AM
  const endHour = 19; // 7 PM
  const timeSlots = [];
  
  for (let hour = startHour; hour <= endHour; hour++) {
    for (let minute = 0; minute < 60; minute += 15) {
      if (hour === endHour && minute > 0) break;
      timeSlots.push(setMinutes(setHours(new Date(), hour), minute));
    }
  }
  
  // Get availability for the current day
  const dayAvailability = availabilityData.filter(slot => 
    isSameDay(new Date(slot.start), currentDate)
  );
  
  // Get availability for a specific time slot
  const getSlotAvailability = (timeSlot) => {
    const slotStart = new Date(currentDate);
    slotStart.setHours(getHours(timeSlot));
    slotStart.setMinutes(getMinutes(timeSlot));
    
    return dayAvailability.filter(slot => {
      const slotStartTime = new Date(slot.start);
      const slotEndTime = new Date(slot.end);
      
      return slotStartTime <= slotStart && slotEndTime > slotStart;
    });
  };
  
  // Get color for availability type
  const getAvailabilityColor = (type) => {
    switch (type) {
      case 'available':
        return '#10b981'; // Green
      case 'booked':
        return '#3b82f6'; // Blue
      case 'blocked':
        return '#ef4444'; // Red
      case 'tentative':
        return '#f59e0b'; // Yellow
      case 'break':
        return '#6b7280'; // Gray
      case 'emergency':
        return '#8b5cf6'; // Purple
      default:
        return '#d1d5db'; // Light gray
    }
  };
  
  // Calculate slot height based on duration
  const getSlotHeight = (slot) => {
    const start = new Date(slot.start);
    const end = new Date(slot.end);
    const durationMinutes = differenceInMinutes(end, start);
    return (durationMinutes / 15) * 25; // 25px per 15 minutes
  };
  
  // Calculate slot position
  const getSlotPosition = (slot) => {
    const slotStart = new Date(slot.start);
    const dayStart = new Date(currentDate);
    dayStart.setHours(startHour, 0, 0, 0);
    
    const minutesSinceDayStart = differenceInMinutes(slotStart, dayStart);
    return (minutesSinceDayStart / 15) * 25; // 25px per 15 minutes
  };
  
  // Handle click on a time slot
  const handleTimeSlotClick = (timeSlot) => {
    const slotStart = new Date(currentDate);
    slotStart.setHours(getHours(timeSlot));
    slotStart.setMinutes(getMinutes(timeSlot));
    
    // Check if slot is already booked
    const existingSlots = getSlotAvailability(timeSlot);
    
    if (existingSlots.length === 0) {
      // If no existing slot, allow adding new availability
      onAddAvailability();
    }
  };
  
  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        {format(currentDate, 'EEEE, MMMM d, yyyy')}
      </Typography>
      
      <Grid container spacing={2}>
        {/* Time slots column */}
        <Grid item xs={12} md={9}>
          <Paper 
            elevation={0} 
            sx={{ 
              border: '1px solid #e0e0e0',
              borderRadius: 2,
              overflow: 'hidden'
            }}
          >
            <Box sx={{ display: 'flex' }}>
              {/* Time labels */}
              <Box sx={{ width: 80, flexShrink: 0 }}>
                {timeSlots.map((timeSlot, index) => (
                  <Box 
                    key={index} 
                    sx={{ 
                      height: 25, 
                      display: 'flex', 
                      alignItems: 'center',
                      justifyContent: 'flex-end',
                      pr: 1,
                      borderBottom: index < timeSlots.length - 1 ? '1px dashed #e0e0e0' : 'none',
                      bgcolor: index % 4 === 0 ? '#f9fafb' : 'transparent'
                    }}
                  >
                    {index % 4 === 0 && (
                      <Typography variant="caption" color="text.secondary">
                        {format(timeSlot, 'h:mm a')}
                      </Typography>
                    )}
                  </Box>
                ))}
              </Box>
              
              {/* Availability slots */}
              <Box sx={{ flexGrow: 1, position: 'relative' }}>
                {/* Background grid */}
                {timeSlots.map((timeSlot, index) => (
                  <Box 
                    key={index} 
                    sx={{ 
                      height: 25, 
                      borderBottom: index < timeSlots.length - 1 ? '1px dashed #e0e0e0' : 'none',
                      bgcolor: index % 4 === 0 ? '#f9fafb' : 'transparent',
                      cursor: 'pointer',
                      '&:hover': {
                        bgcolor: '#f0f9ff',
                      }
                    }}
                    onClick={() => handleTimeSlotClick(timeSlot)}
                  />
                ))}
                
                {/* Availability slots */}
                {dayAvailability.map((slot, index) => (
                  <Tooltip
                    key={index}
                    title={
                      <Box>
                        <Typography variant="subtitle2">{slot.title}</Typography>
                        <Typography variant="body2">
                          {format(new Date(slot.start), 'h:mm a')} - {format(new Date(slot.end), 'h:mm a')}
                        </Typography>
                        {slot.appointmentType && (
                          <Typography variant="body2">Type: {slot.appointmentType}</Typography>
                        )}
                        {slot.notes && (
                          <Typography variant="body2">Notes: {slot.notes}</Typography>
                        )}
                      </Box>
                    }
                    arrow
                    placement="right"
                  >
                    <Paper
                      elevation={3}
                      sx={{
                        position: 'absolute',
                        width: 'calc(100% - 16px)',
                        height: getSlotHeight(slot),
                        bgcolor: getAvailabilityColor(slot.type),
                        color: '#fff',
                        p: 1,
                        borderRadius: 1,
                        overflow: 'hidden',
                        zIndex: 1,
                        left: 8,
                        top: getSlotPosition(slot),
                        opacity: 0.9,
                        '&:hover': {
                          opacity: 1,
                          zIndex: 2
                        },
                        display: 'flex',
                        flexDirection: 'column'
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {slot.title}
                          </Typography>
                          <Typography variant="caption" sx={{ display: 'block' }}>
                            {format(new Date(slot.start), 'h:mm a')} - {format(new Date(slot.end), 'h:mm a')}
                          </Typography>
                          {slot.appointmentType && (
                            <Typography variant="caption" sx={{ display: 'block' }}>
                              {slot.appointmentType}
                            </Typography>
                          )}
                        </Box>
                        
                        {getSlotHeight(slot) > 50 && (
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <IconButton size="small" sx={{ color: '#fff', p: 0.5 }}>
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton size="small" sx={{ color: '#fff', p: 0.5 }}>
                              <Delete fontSize="small" />
                            </IconButton>
                          </Box>
                        )}
                      </Box>
                      
                      {slot.notes && getSlotHeight(slot) > 80 && (
                        <Typography variant="caption" sx={{ mt: 1, fontSize: '0.7rem' }}>
                          {slot.notes}
                        </Typography>
                      )}
                    </Paper>
                  </Tooltip>
                ))}
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        {/* Summary column */}
        <Grid item xs={12} md={3}>
          <Paper 
            elevation={0} 
            sx={{ 
              border: '1px solid #e0e0e0',
              borderRadius: 2,
              p: 2
            }}
          >
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Day Summary
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#10b981' }}>
                Available Slots
              </Typography>
              <Typography variant="body1">
                {dayAvailability.filter(slot => slot.type === 'available').length} slots
              </Typography>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#3b82f6' }}>
                Booked Appointments
              </Typography>
              <Typography variant="body1">
                {dayAvailability.filter(slot => slot.type === 'booked').length} appointments
              </Typography>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#f59e0b' }}>
                Tentative Appointments
              </Typography>
              <Typography variant="body1">
                {dayAvailability.filter(slot => slot.type === 'tentative').length} appointments
              </Typography>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Total Hours
              </Typography>
              <Typography variant="body1">
                {dayAvailability.reduce((total, slot) => {
                  const start = new Date(slot.start);
                  const end = new Date(slot.end);
                  return total + (differenceInMinutes(end, start) / 60);
                }, 0).toFixed(1)} hours
              </Typography>
            </Box>
            
            <Button 
              variant="contained" 
              fullWidth 
              onClick={onAddAvailability}
              sx={{ 
                mt: 2,
                bgcolor: '#10b981',
                '&:hover': {
                  bgcolor: '#059669',
                }
              }}
            >
              Add Availability
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DailyCalendarView;
