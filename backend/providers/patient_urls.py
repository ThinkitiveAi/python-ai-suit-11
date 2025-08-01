from django.urls import path
from .patient_views import PatientRegisterView, PatientLoginView

urlpatterns = [
    path('register/', PatientRegisterView.as_view(), name='patient-register'),  # /api/v1/patient/register/
    path('login/', PatientLoginView.as_view(), name='patient-login'),  # /api/v1/patient/login/
]
