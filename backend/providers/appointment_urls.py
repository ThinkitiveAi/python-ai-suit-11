"""
URL patterns for appointment booking APIs
"""
from django.urls import path
from .appointment_views import (
    AppointmentCreateView,
    AppointmentListView,
    AppointmentDetailView,
    AppointmentUpdateView,
    AppointmentCancelView,
    AppointmentHistoryView,
    AvailableSlotSearchView,
)

urlpatterns = [
    # Appointment CRUD operations
    path('appointments/', AppointmentCreateView.as_view(), name='appointment-create'),
    path('appointments/list/', AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/<uuid:appointment_id>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<uuid:appointment_id>/update/', AppointmentUpdateView.as_view(), name='appointment-update'),
    path('appointments/<uuid:appointment_id>/cancel/', AppointmentCancelView.as_view(), name='appointment-cancel'),
    path('appointments/<uuid:appointment_id>/history/', AppointmentHistoryView.as_view(), name='appointment-history'),
    
    # Available slot search
    path('appointments/slots/search/', AvailableSlotSearchView.as_view(), name='available-slots-search'),
]
