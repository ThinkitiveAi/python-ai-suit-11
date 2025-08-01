import logging
import bcrypt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .patient_serializers import (
    PatientRegistrationSerializer, 
    PatientLoginSerializer, 
    PatientRegistrationResponseSerializer, 
    PatientLoginResponseSerializer, 
    PatientErrorResponseSerializer
)
from .patient_models import Patient
from .jwt_utils import generate_patient_tokens

logger = logging.getLogger(__name__)

class PatientRegisterView(APIView):
    """
    Patient Registration API
    
    Register a new patient with comprehensive validation and medical information.
    """
    
    @swagger_auto_schema(
        operation_description="Register a new patient with personal and medical information",
        operation_summary="Patient Registration",
        request_body=PatientRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Patient registered successfully",
                schema=PatientRegistrationResponseSerializer
            ),
            422: openapi.Response(
                description="Validation errors",
                schema=PatientErrorResponseSerializer
            ),
            400: openapi.Response(
                description="Bad request",
                schema=PatientErrorResponseSerializer
            )
        },
        tags=['Patient Authentication']
    )
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


class PatientLoginView(APIView):
    """
    Patient Login API
    
    Authenticate a patient and return access information.
    """
    
    @swagger_auto_schema(
        operation_description="Login a patient with email and password",
        operation_summary="Patient Login",
        request_body=PatientLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=PatientLoginResponseSerializer
            ),
            401: openapi.Response(
                description="Invalid credentials",
                schema=PatientErrorResponseSerializer
            ),
            400: openapi.Response(
                description="Bad request",
                schema=PatientErrorResponseSerializer
            )
        },
        tags=['Patient Authentication']
    )
    def post(self, request):
        serializer = PatientLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower().strip()
            password = serializer.validated_data['password']
            
            try:
                patient = Patient.objects.get(email=email, is_active=True)
                
                # Verify password
                if bcrypt.checkpw(password.encode('utf-8'), patient.password_hash.encode('utf-8')):
                    # Update login tracking
                    patient.last_login = timezone.now()
                    patient.login_count = (patient.login_count or 0) + 1
                    patient.failed_login_attempts = 0
                    patient.save()
                    
                    logger.info(f"Patient login successful: {email}, ip: {request.META.get('REMOTE_ADDR')}")
                    
                    # Generate JWT tokens
                    tokens = generate_patient_tokens(patient)
                    
                    return Response({
                        "success": True,
                        "message": "Login successful",
                        "data": {
                            "patient_id": str(patient.id),
                            "email": patient.email,
                            "first_name": patient.first_name,
                            "last_name": patient.last_name,
                            "phone_number": patient.phone_number,
                            "email_verified": patient.email_verified,
                            "phone_verified": patient.phone_verified,
                            "tokens": tokens
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    # Update failed login attempts
                    patient.failed_login_attempts = (patient.failed_login_attempts or 0) + 1
                    patient.save()
                    
                    logger.warning(f"Patient login failed - invalid password: {email}, ip: {request.META.get('REMOTE_ADDR')}")
                    
                    return Response({
                        "success": False,
                        "message": "Invalid email or password",
                        "errors": {"credentials": ["Invalid email or password"]}
                    }, status=status.HTTP_401_UNAUTHORIZED)
                    
            except Patient.DoesNotExist:
                logger.warning(f"Patient login failed - user not found: {email}, ip: {request.META.get('REMOTE_ADDR')}")
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
