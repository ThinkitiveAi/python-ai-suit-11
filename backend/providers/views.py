from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    ProviderRegistrationSerializer,
    ProviderLoginSerializer,
    ProviderRegistrationResponseSerializer,
    ProviderLoginResponseSerializer,
    ErrorResponseSerializer
)
from .models import Provider
from .jwt_utils import generate_provider_tokens
import bcrypt
import logging

logger = logging.getLogger(__name__)

class ProviderRegisterView(APIView):
    """
    Provider Registration API
    
    Register a new healthcare provider with comprehensive validation.
    """
    
    @swagger_auto_schema(
        operation_description="Register a new healthcare provider",
        operation_summary="Provider Registration",
        request_body=ProviderRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Provider registered successfully",
                schema=ProviderRegistrationResponseSerializer
            ),
            422: openapi.Response(
                description="Validation errors",
                schema=ErrorResponseSerializer
            ),
            400: openapi.Response(
                description="Bad request",
                schema=ErrorResponseSerializer
            )
        },
        tags=['Provider Authentication']
    )
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


class ProviderLoginView(APIView):
    """
    Provider Login API
    
    Authenticate a healthcare provider and return access tokens.
    """
    
    @swagger_auto_schema(
        operation_description="Login a healthcare provider with email and password",
        operation_summary="Provider Login",
        request_body=ProviderLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=ProviderLoginResponseSerializer
            ),
            401: openapi.Response(
                description="Invalid credentials",
                schema=ErrorResponseSerializer
            ),
            400: openapi.Response(
                description="Bad request",
                schema=ErrorResponseSerializer
            )
        },
        tags=['Provider Authentication']
    )
    def post(self, request):
        serializer = ProviderLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower().strip()
            password = serializer.validated_data['password']
            
            try:
                provider = Provider.objects.get(email=email, is_active=True)
                
                # Verify password
                if bcrypt.checkpw(password.encode('utf-8'), provider.password_hash.encode('utf-8')):
                    # Update login tracking
                    provider.last_login = timezone.now()
                    provider.login_count = (provider.login_count or 0) + 1
                    provider.failed_login_attempts = 0
                    provider.save()
                    
                    logger.info(f"Provider login successful: {email}, ip: {request.META.get('REMOTE_ADDR')}")
                    
                    # Generate JWT tokens
                    tokens = generate_provider_tokens(provider)
                    
                    return Response({
                        "success": True,
                        "message": "Login successful",
                        "data": {
                            "provider_id": str(provider.id),
                            "email": provider.email,
                            "first_name": provider.first_name,
                            "last_name": provider.last_name,
                            "specialization": provider.specialization,
                            "verification_status": provider.verification_status,
                            "tokens": tokens
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    # Update failed login attempts
                    provider.failed_login_attempts = (provider.failed_login_attempts or 0) + 1
                    provider.save()
                    
                    logger.warning(f"Provider login failed - invalid password: {email}, ip: {request.META.get('REMOTE_ADDR')}")
                    
                    return Response({
                        "success": False,
                        "message": "Invalid email or password",
                        "errors": {"credentials": ["Invalid email or password"]}
                    }, status=status.HTTP_401_UNAUTHORIZED)
                    
            except Provider.DoesNotExist:
                logger.warning(f"Provider login failed - user not found: {email}, ip: {request.META.get('REMOTE_ADDR')}")
                return Response({
                    "success": False,
                    "message": "Invalid email or password",
                    "errors": {"credentials": ["Invalid email or password"]}
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        else:
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
