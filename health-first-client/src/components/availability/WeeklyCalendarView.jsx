import React from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Grid, 
  Tooltip,
  Divider
} from '@mui/material';
import { 
  format, 
  startOfWeek, 
  endOfWeek, 
  eachDayOfInterval, 
  isSameDay,
  isToday,
  addHours,
  setHours,
  setMinutes,
  getHours,
  getMinutes,
  differenceInMinutes
} from 'date-fns';

const WeeklyCalendarView = ({ currentDate, availabilityData, onDateSelect, onAddAvailability }) => {
  // Get days for the week view
  const weekStart = startOfWeek(currentDate, { weekStartsOn: 0 });
  const weekEnd = endOfWeek(currentDate, { weekStartsOn: 0 });
  const days = eachDayOfInterval({ start: weekStart, end: weekEnd });
  
  // Generate time slots for the day (30-minute intervals)
  const startHour = 8; // 8 AM
  const endHour = 18; // 6 PM
  const timeSlots = [];
  
  for (let hour = startHour; hour <= endHour; hour++) {
    timeSlots.push(setMinutes(setHours(new Date(), hour), 0));
    if (hour < endHour) {
      timeSlots.push(setMinutes(setHours(new Date(), hour), 30));
    }
  }
  
  // Get availability for a specific day and time
  const getSlotAvailability = (day, timeSlot) => {
    const slotStart = new Date(day);
    slotStart.setHours(getHours(timeSlot));
    slotStart.setMinutes(getMinutes(timeSlot));
    
    return availabilityData.filter(slot => {
      const slotStartTime = new Date(slot.start);
      const slotEndTime = new Date(slot.end);
      
      return isSameDay(slotStartTime, day) && 
             slotStartTime <= slotStart && 
             slotEndTime > slotStart;
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
    return (durationMinutes / 30) * 40; // 40px per 30 minutes
  };
  
  // Handle click on a time slot
  const handleTimeSlotClick = (day, timeSlot) => {
    const slotStart = new Date(day);
    slotStart.setHours(getHours(timeSlot));
    slotStart.setMinutes(getMinutes(timeSlot));
    
    // Check if slot is already booked
    const existingSlots = getSlotAvailability(day, timeSlot);
    
    if (existingSlots.length === 0) {
      // If no existing slot, allow adding new availability
      onAddAvailability();
    }
  };
  
  return (
    <Box sx={{ width: '100%', overflowX: 'auto' }}>
      <Grid container spacing={0}>
        {/* Time column */}
        <Grid item xs={1}>
          <Box sx={{ pr: 1, pt: 5 }}>
            {timeSlots.map((timeSlot, index) => (
              <Box 
                key={index} 
                sx={{ 
                  height: 40, 
                  display: 'flex', 
                  alignItems: 'flex-start',
                  justifyContent: 'flex-end',
                  borderBottom: index < timeSlots.length - 1 ? '1px dashed #e0e0e0' : 'none',
                  position: 'relative'
                }}
              >
                <Typography 
                  variant="caption" 
                  sx={{ 
                    position: 'absolute',
                    top: -10,
                    right: 8,
                    color: 'text.secondary'
                  }}
                >
                  {format(timeSlot, 'h:mm a')}
                </Typography>
              </Box>
            ))}
          </Box>
        </Grid>
        
        {/* Day columns */}
        {days.map((day, dayIndex) => (
          <Grid item xs={11/7} key={dayIndex}>
            {/* Day header */}
            <Box 
              sx={{ 
                p: 1, 
                textAlign: 'center',
                fontWeight: 600,
                borderBottom: '1px solid #e0e0e0',
                bgcolor: isToday(day) ? '#fff8e6' : 'background.paper',
                cursor: 'pointer',
                '&:hover': {
                  bgcolor: '#f0f9ff',
                }
              }}
              onClick={() => onDateSelect(day)}
            >
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {format(day, 'EEE')}
              </Typography>
              <Typography 
                variant="body1" 
                sx={{ 
                  fontWeight: isToday(day) ? 700 : 600,
                  color: isToday(day) ? '#3b82f6' : 'text.primary'
                }}
              >
                {format(day, 'd')}
              </Typography>
            </Box>
            
            {/* Time slots */}
            <Box sx={{ position: 'relative' }}>
              {timeSlots.map((timeSlot, timeIndex) => {
                const slotAvailability = getSlotAvailability(day, timeSlot);
                
                return (
                  <Box 
                    key={timeIndex} 
                    sx={{ 
                      height: 40, 
                      borderBottom: timeIndex < timeSlots.length - 1 ? '1px dashed #e0e0e0' : 'none',
                      borderRight: '1px solid #e0e0e0',
                      cursor: 'pointer',
                      '&:hover': {
                        bgcolor: '#f9fafb',
                      }
                    }}
                    onClick={() => handleTimeSlotClick(day, timeSlot)}
                  >
                    {slotAvailability.map((slot, slotIndex) => (
                      <Tooltip
                        key={slotIndex}
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
                      >
                        <Paper
                          elevation={2}
                          sx={{
                            position: 'absolute',
                            width: 'calc(100% - 4px)',
                            height: getSlotHeight(slot),
                            bgcolor: getAvailabilityColor(slot.type),
                            color: '#fff',
                            p: 0.5,
                            borderRadius: 1,
                            overflow: 'hidden',
                            zIndex: 1,
                            left: 2,
                            top: `calc(${timeIndex * 40}px + 2px)`,
                            opacity: 0.9,
                            '&:hover': {
                              opacity: 1,
                              zIndex: 2
                            }
                          }}
                        >
                          <Typography variant="caption" sx={{ fontWeight: 600 }}>
                            {slot.title}
                          </Typography>
                          <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem' }}>
                            {format(new Date(slot.start), 'h:mm a')} - {format(new Date(slot.end), 'h:mm a')}
                          </Typography>
                        </Paper>
                      </Tooltip>
                    ))}
                  </Box>
                );
              })}
            </Box>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default WeeklyCalendarView;
