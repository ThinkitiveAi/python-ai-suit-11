import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .patient_serializers import PatientRegistrationSerializer
from django.utils import timezone
from .patient_models import Patient

logger = logging.getLogger(__name__)

class PatientRegisterView(APIView):
    def post(self, request):
        data = request.data.copy()
        # Normalize input
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip()
        serializer = PatientRegistrationSerializer(data=data)
        if serializer.is_valid():
            patient = serializer.save()
            logger.info(f"Patient registration attempt: {patient.email}, status: success, ip: {request.META.get('REMOTE_ADDR')}")
            return Response({
                "success": True,
                "message": "Patient registered successfully. Verification email sent.",
                "data": {
                    "patient_id": str(patient.id),
                    "email": patient.email,
                    "phone_number": patient.phone_number,
                    "email_verified": patient.email_verified,
                    "phone_verified": patient.phone_verified
                }
            }, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"Patient registration failed: {serializer.errors}, ip: {request.META.get('REMOTE_ADDR')}")
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=422)
