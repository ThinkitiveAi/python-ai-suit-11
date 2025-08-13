from django.urls import path, include
from .views import ProviderRegisterView, ProviderLoginView
from .availability_views import (
    ProviderAvailabilityCreateView,
    ProviderAvailabilityListView,
    AvailabilitySlotUpdateView
)

urlpatterns = [
    # Authentication endpoints
    path('register', ProviderRegisterView.as_view(), name='provider-register'),  # /api/v1/provider/register
    path('login', ProviderLoginView.as_view(), name='provider-login'),  # /api/v1/provider/login
    
    # Availability management endpoints (individual provider)
    path('<uuid:provider_id>/availability', ProviderAvailabilityCreateView.as_view(), name='provider-availability-create'),  # /api/v1/provider/{id}/availability
    path('<uuid:provider_id>/availability', ProviderAvailabilityListView.as_view(), name='provider-availability-list'),  # /api/v1/provider/{id}/availability
    path('<uuid:provider_id>/availability/<uuid:slot_id>', AvailabilitySlotUpdateView.as_view(), name='availability-slot-update'),  # /api/v1/provider/{id}/availability/{slot_id}
    
    # All availability management endpoints (includes display/get all)
    path('', include('providers.availability_urls')),  # Include all availability URLs
    
    # Appointment booking endpoints
    path('', include('providers.appointment_urls')),  # Include appointment URLs
]
