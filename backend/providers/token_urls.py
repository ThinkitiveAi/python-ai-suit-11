"""
URL Configuration for JWT Token Management
"""

from django.urls import path
from .token_views import TokenRefreshView, TokenValidateView

urlpatterns = [
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('validate/', TokenValidateView.as_view(), name='token-validate'),
]
