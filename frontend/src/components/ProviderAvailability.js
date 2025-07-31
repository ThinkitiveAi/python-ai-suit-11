import React, { useState } from 'react';
import {
  Box, Card, Typography, Button, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText, Divider, Grid, Tooltip, Avatar, Chip, MenuItem, Select, FormControl, InputLabel, TextField, Switch, FormControlLabel
} from '@mui/material';
import {
  CalendarMonth, CalendarToday, AccessTime, Add, Edit, Delete, Settings, EventAvailable, EventBusy, EventNote, ArrowBackIos, ArrowForwardIos, CheckCircle, Warning, Info, Block, Repeat, ContentCopy, Print, CloudUpload, Schedule, Person
} from '@mui/icons-material';

const VIEWS = ['Month', 'Week', 'Day'];
const STATUS_COLORS = {
  available: '#10b981', // green
  booked: '#3b82f6',   // blue
  blocked: '#ef4444',  // red
  pending: '#f59e0b',  // yellow
  break: '#6b7280',    // gray
};

const mockSlots = [
  { id: 1, date: '2024-07-24', start: '09:00', end: '10:00', status: 'available' },
  { id: 2, date: '2024-07-24', start: '10:00', end: '10:30', status: 'booked' },
  { id: 3, date: '2024-07-24', start: '11:00', end: '11:30', status: 'break' },
  { id: 4, date: '2024-07-24', start: '12:00', end: '12:30', status: 'pending' },
  { id: 5, date: '2024-07-24', start: '13:00', end: '14:00', status: 'blocked' },
];

export default function ProviderAvailability() {
  const [view, setView] = useState('Week');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState('2024-07-24');
  const [showAddForm, setShowAddForm] = useState(false);

  // Sidebar navigation
  const sidebar = (
    <Box sx={{ width: 260, p: 2, bgcolor: '#f9fafb', height: '100vh', borderRight: '1px solid #e5e7eb' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Avatar sx={{ bgcolor: '#3b82f6', mr: 1 }}><Person /></Avatar>
        <Box>
          <Typography fontWeight="bold">Dr. Jane Smith</Typography>
          <Typography variant="body2" color="text.secondary">Cardiologist</Typography>
        </Box>
      </Box>
      <Divider sx={{ mb: 2 }} />
      <List>
        <ListItem button selected={view === 'Month'} onClick={() => setView('Month')}>
          <ListItemIcon><CalendarMonth /></ListItemIcon>
          <ListItemText primary="Month View" />
        </ListItem>
        <ListItem button selected={view === 'Week'} onClick={() => setView('Week')}>
          <ListItemIcon><CalendarToday /></ListItemIcon>
          <ListItemText primary="Week View" />
        </ListItem>
        <ListItem button selected={view === 'Day'} onClick={() => setView('Day')}>
          <ListItemIcon><AccessTime /></ListItemIcon>
          <ListItemText primary="Day View" />
        </ListItem>
      </List>
      <Divider sx={{ my: 2 }} />
      <Typography variant="subtitle2" sx={{ mb: 1 }}>Availability Stats</Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <Chip label="Available" sx={{ bgcolor: STATUS_COLORS.available, color: '#fff' }} size="small" />
        <Chip label="Booked" sx={{ bgcolor: STATUS_COLORS.booked, color: '#fff' }} size="small" />
        <Chip label="Blocked" sx={{ bgcolor: STATUS_COLORS.blocked, color: '#fff' }} size="small" />
        <Chip label="Pending" sx={{ bgcolor: STATUS_COLORS.pending, color: '#fff' }} size="small" />
        <Chip label="Break" sx={{ bgcolor: STATUS_COLORS.break, color: '#fff' }} size="small" />
      </Box>
      <Divider sx={{ my: 2 }} />
      <Button startIcon={<EventAvailable />} variant="outlined" fullWidth sx={{ mb: 1 }} onClick={() => setShowAddForm(true)}>
        Add Availability
      </Button>
      <Button startIcon={<Settings />} variant="text" fullWidth>
        Settings
      </Button>
    </Box>
  );

  // Main calendar area (static mockup for now)
  const calendarHeader = (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <IconButton><ArrowBackIos /></IconButton>
        <Typography variant="h6" fontWeight="bold">{selectedDate}</Typography>
        <IconButton><ArrowForwardIos /></IconButton>
        <Button size="small" sx={{ ml: 2 }} startIcon={<CalendarToday />}>Today</Button>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Tooltip title="Print"><IconButton><Print /></IconButton></Tooltip>
        <Tooltip title="Export"><IconButton><CloudUpload /></IconButton></Tooltip>
        <Tooltip title="Templates"><IconButton><EventNote /></IconButton></Tooltip>
      </Box>
    </Box>
  );

  const timeSlotGrid = (
    <Grid container spacing={2}>
      {mockSlots.map(slot => (
        <Grid item xs={12} sm={6} md={4} key={slot.id}>
          <Card sx={{ p: 2, bgcolor: STATUS_COLORS[slot.status], color: '#fff', position: 'relative' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Schedule sx={{ mr: 1 }} />
              <Typography fontWeight="bold">{slot.start} - {slot.end}</Typography>
            </Box>
            <Typography variant="body2" sx={{ mb: 1 }}>{slot.status.charAt(0).toUpperCase() + slot.status.slice(1)}</Typography>
            <Box sx={{ position: 'absolute', top: 8, right: 8, display: 'flex', gap: 1 }}>
              <Tooltip title="Edit"><IconButton size="small" sx={{ color: '#fff' }}><Edit fontSize="small" /></IconButton></Tooltip>
              <Tooltip title="Delete"><IconButton size="small" sx={{ color: '#fff' }}><Delete fontSize="small" /></IconButton></Tooltip>
            </Box>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  // Add/Edit Availability Form (static for now)
  const addForm = showAddForm && (
    <Card sx={{ p: 3, maxWidth: 400, mx: 'auto', mt: 4, boxShadow: 4, borderRadius: 3, position: 'absolute', top: 80, left: '50%', transform: 'translateX(-50%)', zIndex: 10 }}>
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>Add Availability</Typography>
      <TextField label="Date" type="date" fullWidth sx={{ mb: 2 }} InputLabelProps={{ shrink: true }} />
      <TextField label="Start Time" type="time" fullWidth sx={{ mb: 2 }} InputLabelProps={{ shrink: true }} />
      <TextField label="End Time" type="time" fullWidth sx={{ mb: 2 }} InputLabelProps={{ shrink: true }} />
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Appointment Type</InputLabel>
        <Select label="Appointment Type" defaultValue="Consultation">
          <MenuItem value="Consultation">Consultation</MenuItem>
          <MenuItem value="Follow-up">Follow-up</MenuItem>
          <MenuItem value="Emergency">Emergency</MenuItem>
        </Select>
      </FormControl>
      <TextField label="Notes" fullWidth multiline rows={2} sx={{ mb: 2 }} />
      <FormControlLabel control={<Switch />} label="Recurring Weekly" sx={{ mb: 2 }} />
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button variant="contained" color="primary" startIcon={<Add />}>Save</Button>
        <Button variant="outlined" color="secondary" onClick={() => setShowAddForm(false)}>Cancel</Button>
      </Box>
    </Card>
  );

  // Legend
  const legend = (
    <Box sx={{ display: 'flex', gap: 2, mt: 2, mb: 1 }}>
      <Chip label="Available" sx={{ bgcolor: STATUS_COLORS.available, color: '#fff' }} size="small" />
      <Chip label="Booked" sx={{ bgcolor: STATUS_COLORS.booked, color: '#fff' }} size="small" />
      <Chip label="Blocked" sx={{ bgcolor: STATUS_COLORS.blocked, color: '#fff' }} size="small" />
      <Chip label="Pending" sx={{ bgcolor: STATUS_COLORS.pending, color: '#fff' }} size="small" />
      <Chip label="Break" sx={{ bgcolor: STATUS_COLORS.break, color: '#fff' }} size="small" />
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f4f8fb' }}>
      {/* Sidebar */}
      {sidebar}
      {/* Main Content */}
      <Box sx={{ flex: 1, p: 4, position: 'relative' }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box>
            <Typography variant="h5" fontWeight="bold">Provider Availability</Typography>
            <Typography variant="subtitle2" color="text.secondary">Manage your appointment schedule</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" color="text.secondary">{new Date().toLocaleString()}</Typography>
            <Button startIcon={<Add />} variant="contained" color="primary" onClick={() => setShowAddForm(true)}>
              Add Availability
            </Button>
          </Box>
        </Box>
        {/* Calendar Controls */}
        {calendarHeader}
        {/* Legend */}
        {legend}
        {/* Calendar Grid */}
        {timeSlotGrid}
        {/* Add/Edit Form */}
        {addForm}
      </Box>
    </Box>
  );
} 