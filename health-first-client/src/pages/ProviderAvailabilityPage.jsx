import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Tabs, 
  Tab, 
  Button, 
  IconButton, 
  Drawer,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Tooltip,
  Badge,
  Chip,
  Avatar,
  AppBar,
  Toolbar,
  TextField
} from '@mui/material';
import { 
  CalendarMonth, 
  CalendarViewWeek, 
  CalendarViewDay, 
  Today, 
  ChevronLeft, 
  ChevronRight,
  Add,
  Settings,
  Notifications,
  LocalHospital,
  AccessTime,
  Event,
  EventBusy,
  EventAvailable,
  EventNote,
  ContentCopy,
  Save,
  Print,
  FilterList,
  Refresh,
  MoreVert,
  Menu as MenuIcon
} from '@mui/icons-material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { format, addDays, startOfWeek, endOfWeek, addWeeks, subWeeks, addMonths, subMonths } from 'date-fns';

// Import components
import MonthlyCalendarView from '../components/availability/MonthlyCalendarView';
import WeeklyCalendarView from '../components/availability/WeeklyCalendarView';
import DailyCalendarView from '../components/availability/DailyCalendarView';
import AddAvailabilityForm from '../components/availability/AddAvailabilityForm';
import AvailabilityLegend from '../components/availability/AvailabilityLegend';

// Mock data for appointments and availability
import { mockAvailabilityData } from '../data/mockAvailabilityData';

const ProviderAvailabilityPage = () => {
  // State for calendar view and date
  const [calendarView, setCalendarView] = useState('week');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [formDrawerOpen, setFormDrawerOpen] = useState(false);
  const [availabilityData, setAvailabilityData] = useState(mockAvailabilityData);
  
  // Drawer width
  const drawerWidth = 240;
  
  // Handle calendar view change
  const handleViewChange = (event, newValue) => {
    setCalendarView(newValue);
  };
  
  // Navigate to today
  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDate(new Date());
  };
  
  // Navigate to previous period
  const goToPrevious = () => {
    if (calendarView === 'month') {
      setCurrentDate(subMonths(currentDate, 1));
    } else if (calendarView === 'week') {
      setCurrentDate(subWeeks(currentDate, 1));
    } else {
      setCurrentDate(addDays(currentDate, -1));
    }
  };
  
  // Navigate to next period
  const goToNext = () => {
    if (calendarView === 'month') {
      setCurrentDate(addMonths(currentDate, 1));
    } else if (calendarView === 'week') {
      setCurrentDate(addWeeks(currentDate, 1));
    } else {
      setCurrentDate(addDays(currentDate, 1));
    }
  };
  
  // Toggle drawer
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  // Toggle mobile drawer
  const toggleMobileDrawer = () => {
    setMobileDrawerOpen(!mobileDrawerOpen);
  };
  
  // Open form drawer
  const openFormDrawer = () => {
    setFormDrawerOpen(true);
  };
  
  // Close form drawer
  const closeFormDrawer = () => {
    setFormDrawerOpen(false);
  };
  
  // Get calendar title based on view and current date
  const getCalendarTitle = () => {
    if (calendarView === 'month') {
      return format(currentDate, 'MMMM yyyy');
    } else if (calendarView === 'week') {
      const weekStart = startOfWeek(currentDate, { weekStartsOn: 0 });
      const weekEnd = endOfWeek(currentDate, { weekStartsOn: 0 });
      return `${format(weekStart, 'MMM d')} - ${format(weekEnd, 'MMM d, yyyy')}`;
    } else {
      return format(currentDate, 'EEEE, MMMM d, yyyy');
    }
  };
  
  // Handle date selection
  const handleDateSelect = (date) => {
    setSelectedDate(date);
    if (calendarView === 'month') {
      setCalendarView('day');
      setCurrentDate(date);
    }
  };
  
  // Handle add availability
  const handleAddAvailability = (newAvailability) => {
    setAvailabilityData([...availabilityData, newAvailability]);
    closeFormDrawer();
  };
  
  // Render calendar view based on selected view
  const renderCalendarView = () => {
    switch (calendarView) {
      case 'month':
        return (
          <MonthlyCalendarView 
            currentDate={currentDate}
            availabilityData={availabilityData}
            onDateSelect={handleDateSelect}
          />
        );
      case 'week':
        return (
          <WeeklyCalendarView 
            currentDate={currentDate}
            availabilityData={availabilityData}
            onDateSelect={handleDateSelect}
            onAddAvailability={openFormDrawer}
          />
        );
      case 'day':
        return (
          <DailyCalendarView 
            currentDate={currentDate}
            availabilityData={availabilityData}
            onAddAvailability={openFormDrawer}
          />
        );
      default:
        return null;
    }
  };
  
  // Sidebar content
  const sidebarContent = (
    <>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
        <LocalHospital sx={{ color: '#2563eb', mr: 1 }} />
        <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
          Health First
        </Typography>
      </Box>
      <Divider />
      <Box sx={{ p: 2 }}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <DatePicker
            value={selectedDate}
            onChange={(newDate) => {
              setSelectedDate(newDate);
              setCurrentDate(newDate);
            }}
            renderInput={(params) => <TextField {...params} fullWidth />}
          />
        </LocalizationProvider>
      </Box>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton 
            selected={calendarView === 'month'} 
            onClick={() => setCalendarView('month')}
          >
            <ListItemIcon>
              <CalendarMonth color={calendarView === 'month' ? 'primary' : 'inherit'} />
            </ListItemIcon>
            <ListItemText primary="Month View" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton 
            selected={calendarView === 'week'} 
            onClick={() => setCalendarView('week')}
          >
            <ListItemIcon>
              <CalendarViewWeek color={calendarView === 'week' ? 'primary' : 'inherit'} />
            </ListItemIcon>
            <ListItemText primary="Week View" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton 
            selected={calendarView === 'day'} 
            onClick={() => setCalendarView('day')}
          >
            <ListItemIcon>
              <CalendarViewDay color={calendarView === 'day' ? 'primary' : 'inherit'} />
            </ListItemIcon>
            <ListItemText primary="Day View" />
          </ListItemButton>
        </ListItem>
      </List>
      <Divider />
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Availability Templates
        </Typography>
        <List dense>
          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <EventAvailable fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Regular Hours" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <EventNote fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Morning Only" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <EventNote fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Afternoon Only" />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
      <Divider />
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Availability Stats
        </Typography>
        <Grid container spacing={1}>
          <Grid item xs={6}>
            <Paper 
              elevation={0} 
              sx={{ 
                p: 1, 
                textAlign: 'center', 
                bgcolor: '#e6f7ff',
                borderRadius: 1
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Available
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                24h
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={6}>
            <Paper 
              elevation={0} 
              sx={{ 
                p: 1, 
                textAlign: 'center', 
                bgcolor: '#fff1e6',
                borderRadius: 1
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Booked
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                12h
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          bgcolor: '#fff',
          color: 'text.primary',
          boxShadow: 1
        }}
      >
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={toggleMobileDrawer}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ display: { xs: 'none', sm: 'flex' }, alignItems: 'center' }}>
            <IconButton color="inherit" onClick={toggleDrawer}>
              <MenuIcon />
            </IconButton>
          </Box>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Provider Availability
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Notifications">
              <IconButton color="inherit">
                <Badge badgeContent={4} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Settings">
              <IconButton color="inherit">
                <Settings />
              </IconButton>
            </Tooltip>
            
            <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
              <Avatar sx={{ bgcolor: '#2563eb', width: 32, height: 32 }}>
                DR
              </Avatar>
              <Box sx={{ ml: 1, display: { xs: 'none', md: 'block' } }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Dr. Sarah Reynolds
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Cardiologist
                </Typography>
              </Box>
            </Box>
          </Box>
        </Toolbar>
      </AppBar>
      
      <Drawer
        variant="persistent"
        anchor="left"
        open={drawerOpen}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            top: '64px',
            height: 'calc(100% - 64px)'
          },
        }}
      >
        {sidebarContent}
      </Drawer>
      
      <Drawer
        variant="temporary"
        anchor="left"
        open={mobileDrawerOpen}
        onClose={toggleMobileDrawer}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { width: drawerWidth },
        }}
      >
        {sidebarContent}
      </Drawer>
      
      <Drawer
        anchor="right"
        open={formDrawerOpen}
        onClose={closeFormDrawer}
        sx={{
          '& .MuiDrawer-paper': { width: { xs: '100%', sm: 400 } },
        }}
      >
        <AddAvailabilityForm 
          onClose={closeFormDrawer} 
          onSubmit={handleAddAvailability}
          selectedDate={selectedDate}
        />
      </Drawer>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerOpen ? drawerWidth : 0}px)` },
          ml: { sm: drawerOpen ? `${drawerWidth}px` : 0 },
          mt: '64px',
          transition: (theme) => theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  {getCalendarTitle()}
                </Typography>
                <IconButton size="small" onClick={goToToday}>
                  <Today fontSize="small" />
                </IconButton>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' }, gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={openFormDrawer}
                  sx={{ 
                    borderColor: '#2563eb',
                    color: '#2563eb',
                    '&:hover': {
                      borderColor: '#1e40af',
                      bgcolor: 'rgba(37, 99, 235, 0.04)'
                    }
                  }}
                >
                  Add Availability
                </Button>
                
                <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
                  <IconButton onClick={goToPrevious}>
                    <ChevronLeft />
                  </IconButton>
                  
                  <IconButton onClick={goToNext}>
                    <ChevronRight />
                  </IconButton>
                </Box>
              </Box>
            </Grid>
          </Grid>
          
          <Box sx={{ mt: 2 }}>
            <Tabs 
              value={calendarView} 
              onChange={handleViewChange}
              aria-label="calendar view tabs"
              sx={{
                '& .MuiTab-root': {
                  minWidth: 100,
                },
                '& .Mui-selected': {
                  color: '#2563eb',
                },
                '& .MuiTabs-indicator': {
                  backgroundColor: '#2563eb',
                },
              }}
            >
              <Tab 
                icon={<CalendarMonth />} 
                label="Month" 
                value="month" 
                iconPosition="start"
              />
              <Tab 
                icon={<CalendarViewWeek />} 
                label="Week" 
                value="week" 
                iconPosition="start"
              />
              <Tab 
                icon={<CalendarViewDay />} 
                label="Day" 
                value="day" 
                iconPosition="start"
              />
            </Tabs>
          </Box>
        </Box>
        
        {/* Calendar Legend */}
        <Box sx={{ mb: 3 }}>
          <AvailabilityLegend />
        </Box>
        
        {/* Calendar View */}
        <Paper 
          elevation={0} 
          sx={{ 
            p: 2, 
            border: '1px solid #e0e0e0',
            borderRadius: 2,
            height: 'calc(100vh - 280px)',
            overflow: 'auto'
          }}
        >
          {renderCalendarView()}
        </Paper>
        
        {/* Mobile Add Button */}
        <Box
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            display: { xs: 'block', sm: 'none' }
          }}
        >
          <Button
            variant="contained"
            color="primary"
            onClick={openFormDrawer}
            sx={{
              width: 56,
              height: 56,
              borderRadius: '50%',
              bgcolor: '#10b981',
              '&:hover': {
                bgcolor: '#059669',
              }
            }}
          >
            <Add />
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default ProviderAvailabilityPage;
