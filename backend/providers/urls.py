from django.urls import path
from .views import ProviderRegisterView
from .login_views import ProviderLoginView
from .patient_views import PatientRegisterView
from .patient_auth_views import PatientLoginView

urlpatterns = [
    path('register', ProviderRegisterView.as_view(), name='provider-register'),
    path('login', ProviderLoginView.as_view(), name='provider-login'),
    path('patient/register', PatientRegisterView.as_view(), name='patient-register'),  # /api/v1/patient/register
    path('patient/login', PatientLoginView.as_view(), name='patient-login'),  # /api/v1/patient/login
]
