from django.urls import path
from .slot_debug_views import (
    AvailableSlotIdsView,
    SlotValidationView
)

urlpatterns = [
    # Debug endpoints for slot troubleshooting
    path('debug/available-slot-ids', AvailableSlotIdsView.as_view(), name='debug-available-slot-ids'),
    path('debug/validate-slot', SlotValidationView.as_view(), name='debug-validate-slot'),
]
