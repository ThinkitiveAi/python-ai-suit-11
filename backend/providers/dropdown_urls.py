from django.urls import path
from .dropdown_views import ProviderListView, PatientListView

urlpatterns = [
    # Dropdown APIs
    path('providers', ProviderListView.as_view(), name='providers-dropdown'),  # /api/v1/dropdown/providers
    path('patients', PatientListView.as_view(), name='patients-dropdown'),    # /api/v1/dropdown/patients
]
