from django.urls import path
from .availability_views import (
    ProviderAvailabilityCreateView,
    ProviderAvailabilityListView,
    AvailabilitySlotUpdateView,
    AvailabilitySearchView,
    AllProviderAvailabilityListView,
    AvailabilitySlotListView
)

urlpatterns = [
    # Provider availability management endpoints
    path('availability', ProviderAvailabilityCreateView.as_view(), name='provider-availability-create'),
    path('<uuid:provider_id>/availability', ProviderAvailabilityListView.as_view(), name='provider-availability-list'),
    path('availability/<uuid:slot_id>', AvailabilitySlotUpdateView.as_view(), name='availability-slot-update'),
    
    # GET endpoint to display all provider availability data
    path('availability/display', AllProviderAvailabilityListView.as_view(), name='provider-availability-display'),
    
    # Get all provider availability data (alternative endpoint)
    path('availability/all', AllProviderAvailabilityListView.as_view(), name='all-provider-availability-list'),
    
    # Get available slots for a specific availability record
    path('availability/<uuid:availability_id>/slots', AvailabilitySlotListView.as_view(), name='availability-slots-list'),
    
    # Public search endpoint
    path('availability/search', AvailabilitySearchView.as_view(), name='availability-search'),
]
