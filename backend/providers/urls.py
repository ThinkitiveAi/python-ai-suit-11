from django.urls import path
from .views import ProviderRegisterView, ProviderLoginView

urlpatterns = [
    path('register', ProviderRegisterView.as_view(), name='provider-register'),  # /api/v1/provider/register
    path('login', ProviderLoginView.as_view(), name='provider-login'),  # /api/v1/provider/login
]
