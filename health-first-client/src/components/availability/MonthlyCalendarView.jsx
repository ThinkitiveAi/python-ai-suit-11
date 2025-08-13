import React from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Grid, 
  Badge,
  Tooltip
} from '@mui/material';
import { 
  format, 
  startOfMonth, 
  endOfMonth, 
  eachDayOfInterval, 
  isSameMonth, 
  isSameDay,
  startOfWeek,
  endOfWeek,
  isToday,
  addDays
} from 'date-fns';

const MonthlyCalendarView = ({ currentDate, availabilityData, onDateSelect }) => {
  // Get days for the month view
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const startDate = startOfWeek(monthStart);
  const endDate = endOfWeek(monthEnd);
  
  const days = eachDayOfInterval({ start: startDate, end: endDate });
  
  // Get availability for a specific day
  const getDayAvailability = (day) => {
    return availabilityData.filter(slot => isSameDay(new Date(slot.start), day));
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
  
  // Render day cell
  const renderDayCell = (day) => {
    const dayAvailability = getDayAvailability(day);
    const isCurrentMonth = isSameMonth(day, currentDate);
    const isSelected = isSameDay(day, currentDate);
    const dayIsToday = isToday(day);
    
    // Group availability by type
    const availabilityByType = dayAvailability.reduce((acc, slot) => {
      if (!acc[slot.type]) {
        acc[slot.type] = [];
      }
      acc[slot.type].push(slot);
      return acc;
    }, {});
    
    return (
      <Paper
        elevation={isSelected ? 3 : 0}
        sx={{
          height: '100%',
          p: 1,
          border: '1px solid #e0e0e0',
          borderRadius: 1,
          bgcolor: isSelected ? '#e6f7ff' : (dayIsToday ? '#fff8e6' : 'background.paper'),
          opacity: isCurrentMonth ? 1 : 0.5,
          cursor: 'pointer',
          '&:hover': {
            bgcolor: '#f0f9ff',
          },
          position: 'relative',
          overflow: 'hidden'
        }}
        onClick={() => onDateSelect(day)}
      >
        <Typography 
          variant="body2" 
          sx={{ 
            fontWeight: dayIsToday ? 700 : (isCurrentMonth ? 500 : 400),
            color: dayIsToday ? '#3b82f6' : 'text.primary',
            mb: 1
          }}
        >
          {format(day, 'd')}
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          {Object.keys(availabilityByType).map((type, typeIndex) => (
            <Tooltip 
              key={typeIndex}
              title={`${availabilityByType[type].length} ${type} ${availabilityByType[type].length === 1 ? 'slot' : 'slots'}`}
              arrow
            >
              <Badge 
                badgeContent={availabilityByType[type].length} 
                color="primary"
                sx={{ 
                  '& .MuiBadge-badge': { 
                    bgcolor: getAvailabilityColor(type),
                    color: '#fff'
                  }
                }}
              >
                <Box 
                  sx={{ 
                    height: 4, 
                    width: '100%', 
                    bgcolor: getAvailabilityColor(type),
                    borderRadius: 1
                  }} 
                />
              </Badge>
            </Tooltip>
          ))}
        </Box>
      </Paper>
    );
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Grid container spacing={0}>
        {/* Day headers */}
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, index) => (
          <Grid item xs={12/7} key={index}>
            <Box 
              sx={{ 
                p: 1, 
                textAlign: 'center',
                fontWeight: 600,
                borderBottom: '1px solid #e0e0e0'
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {day}
              </Typography>
            </Box>
          </Grid>
        ))}
        
        {/* Calendar days */}
        {days.map((day, index) => (
          <Grid item xs={12/7} key={index} sx={{ height: 100 }}>
            {renderDayCell(day)}
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default MonthlyCalendarView;
