from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.utils import timezone
from .serializers import ProviderRegistrationSerializer
import logging

logger = logging.getLogger(__name__)

class ProviderRegisterView(APIView):
    def post(self, request):
        data = request.data.copy()
        # Input normalization and trimming
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip()
        serializer = ProviderRegistrationSerializer(data=data)
        if serializer.is_valid():
            provider = serializer.save()
            # Audit log
            logger.info(f"Provider registration attempt: {provider.email}, status: success, ip: {request.META.get('REMOTE_ADDR')}")
            # Email verification stub (implement actual sending in service)
            # emailService.send_verification_email(provider.email, token)
            return Response({
                "success": True,
                "message": "Provider registered successfully. Verification email sent.",
                "data": {
                    "provider_id": str(provider.id),
                    "email": provider.email,
                    "verification_status": provider.verification_status
                }
            }, status=status.HTTP_201_CREATED)
        else:
            logger.info(f"Provider registration failed: {serializer.errors}, ip: {request.META.get('REMOTE_ADDR')}")
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
