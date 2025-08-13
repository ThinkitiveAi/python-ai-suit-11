import React from 'react';
import { 
  Box, 
  Typography, 
  Paper,
  Grid,
  Tooltip
} from '@mui/material';

const AvailabilityLegend = () => {
  // Define availability types with colors and descriptions
  const availabilityTypes = [
    {
      type: 'available',
      color: '#10b981', // Green
      label: 'Available',
      description: 'Time slots available for booking appointments'
    },
    {
      type: 'booked',
      color: '#3b82f6', // Blue
      label: 'Booked',
      description: 'Time slots that have been booked by patients'
    },
    {
      type: 'blocked',
      color: '#ef4444', // Red
      label: 'Blocked',
      description: 'Time slots that are unavailable for booking'
    },
    {
      type: 'tentative',
      color: '#f59e0b', // Yellow
      label: 'Tentative',
      description: 'Appointments that are not yet confirmed'
    },
    {
      type: 'break',
      color: '#6b7280', // Gray
      label: 'Break',
      description: 'Personal or lunch breaks'
    },
    {
      type: 'emergency',
      color: '#8b5cf6', // Purple
      label: 'Emergency',
      description: 'Slots reserved for emergency appointments'
    }
  ];

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 2, 
        border: '1px solid #e0e0e0',
        borderRadius: 2
      }}
    >
      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
        Availability Legend
      </Typography>
      
      <Grid container spacing={1}>
        {availabilityTypes.map((item) => (
          <Grid item xs={6} sm={4} md={2} key={item.type}>
            <Tooltip title={item.description} arrow placement="top">
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  cursor: 'help'
                }}
              >
                <Box 
                  sx={{ 
                    width: 16, 
                    height: 16, 
                    borderRadius: 1, 
                    bgcolor: item.color,
                    mr: 1
                  }} 
                />
                <Typography variant="body2">
                  {item.label}
                </Typography>
              </Box>
            </Tooltip>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default AvailabilityLegend;
