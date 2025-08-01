import uuid
from django.db import models
from django.utils import timezone
from .patient_models import Patient

class PatientSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='sessions')
    refresh_token_hash = models.CharField(max_length=128)
    device_info = models.JSONField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.CharField(max_length=256, blank=True, null=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(blank=True, null=True)
    location_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Session for {self.patient.email} (revoked={self.is_revoked})"
