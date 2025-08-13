// Mock data for provider availability
export const mockAvailabilityData = [
  // Available slots
  {
    id: 1,
    title: 'Available',
    start: new Date(new Date().setHours(9, 0, 0, 0)),
    end: new Date(new Date().setHours(12, 0, 0, 0)),
    type: 'available',
    appointmentType: 'General Consultation',
    slotDuration: 30,
    notes: '',
    recurring: false
  },
  {
    id: 2,
    title: 'Available',
    start: new Date(new Date().setHours(14, 0, 0, 0)),
    end: new Date(new Date().setHours(17, 0, 0, 0)),
    type: 'available',
    appointmentType: 'General Consultation',
    slotDuration: 30,
    notes: '',
    recurring: false
  },
  
  // Tomorrow morning
  {
    id: 3,
    title: 'Available',
    start: new Date(new Date().setDate(new Date().getDate() + 1)).setHours(9, 0, 0, 0),
    end: new Date(new Date().setDate(new Date().getDate() + 1)).setHours(12, 0, 0, 0),
    type: 'available',
    appointmentType: 'General Consultation',
    slotDuration: 30,
    notes: '',
    recurring: false
  },
  
  // Booked appointments
  {
    id: 4,
    title: 'John Smith',
    start: new Date(new Date().setHours(10, 0, 0, 0)),
    end: new Date(new Date().setHours(10, 30, 0, 0)),
    type: 'booked',
    appointmentType: 'General Consultation',
    patientName: 'John Smith',
    patientId: '12345',
    notes: 'Follow-up appointment'
  },
  {
    id: 5,
    title: 'Emily Johnson',
    start: new Date(new Date().setHours(15, 0, 0, 0)),
    end: new Date(new Date().setHours(15, 30, 0, 0)),
    type: 'booked',
    appointmentType: 'General Consultation',
    patientName: 'Emily Johnson',
    patientId: '12346',
    notes: 'New patient consultation'
  },
  
  // Blocked time
  {
    id: 6,
    title: 'Lunch Break',
    start: new Date(new Date().setHours(12, 0, 0, 0)),
    end: new Date(new Date().setHours(14, 0, 0, 0)),
    type: 'break',
    notes: 'Lunch and administrative tasks'
  },
  
  // Blocked day next week
  {
    id: 7,
    title: 'Conference',
    start: new Date(new Date().setDate(new Date().getDate() + 7)).setHours(0, 0, 0, 0),
    end: new Date(new Date().setDate(new Date().getDate() + 7)).setHours(23, 59, 59, 0),
    type: 'blocked',
    notes: 'Medical conference attendance'
  },
  
  // Tentative appointment
  {
    id: 8,
    title: 'Tentative: Sarah Williams',
    start: new Date(new Date().setHours(16, 0, 0, 0)),
    end: new Date(new Date().setHours(16, 30, 0, 0)),
    type: 'tentative',
    appointmentType: 'General Consultation',
    patientName: 'Sarah Williams',
    patientId: '12347',
    notes: 'Awaiting confirmation'
  },
  
  // Emergency slot
  {
    id: 9,
    title: 'Emergency Slot',
    start: new Date(new Date().setDate(new Date().getDate() + 1)).setHours(17, 0, 0, 0),
    end: new Date(new Date().setDate(new Date().getDate() + 1)).setHours(18, 0, 0, 0),
    type: 'emergency',
    appointmentType: 'Emergency Consultation',
    slotDuration: 60,
    notes: 'Reserved for urgent cases only'
  }
];

// Appointment types
export const appointmentTypes = [
  { id: 1, name: 'General Consultation', duration: 30 },
  { id: 2, name: 'Follow-up', duration: 15 },
  { id: 3, name: 'New Patient', duration: 45 },
  { id: 4, name: 'Procedure', duration: 60 },
  { id: 5, name: 'Emergency Consultation', duration: 60 }
];

// Slot durations
export const slotDurations = [
  { value: 15, label: '15 minutes' },
  { value: 30, label: '30 minutes' },
  { value: 45, label: '45 minutes' },
  { value: 60, label: '1 hour' }
];

// Recurring options
export const recurringOptions = [
  { value: 'none', label: 'None' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'biweekly', label: 'Bi-weekly' },
  { value: 'monthly', label: 'Monthly' }
];
