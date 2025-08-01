import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from .login_serializers import PatientLoginSerializer
from .services.patient_auth_service import PatientAuthService
from .utils.jwt_utils import generate_jwt_tokens
from .utils.device_utils import fingerprint_device
from .utils.security_utils import log_security_event

logger = logging.getLogger(__name__)

class PatientLoginView(APIView):
    def post(self, request):
        serializer = PatientLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        identifier = data['identifier']
        password = data['password']
        remember_me = data.get('remember_me', False)
        device_info = data.get('device_info', {})
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Authenticate patient
        patient, error_code, patient_obj = PatientAuthService.authenticate(
            identifier, password, ip_address, device_info, user_agent
        )

        # Handle errors
        if error_code == 'INVALID_CREDENTIALS':
            return Response({
                'success': False,
                'message': 'Invalid email/phone or password',
                'error_code': 'INVALID_CREDENTIALS'
            }, status=status.HTTP_401_UNAUTHORIZED)
        if error_code == 'EMAIL_NOT_VERIFIED':
            return Response({
                'success': False,
                'message': 'Please verify your email before logging in',
                'error_code': 'EMAIL_NOT_VERIFIED',
                'verification_required': True
            }, status=status.HTTP_403_FORBIDDEN)
        if error_code == 'ACCOUNT_LOCKED':
            locked_until = patient_obj.locked_until.isoformat() if patient_obj and patient_obj.locked_until else None
            return Response({
                'success': False,
                'message': 'Account temporarily locked due to failed login attempts',
                'error_code': 'ACCOUNT_LOCKED',
                'locked_until': locked_until
            }, status=423)
        if error_code == 'RATE_LIMITED':
            return Response({
                'success': False,
                'message': 'Too many login attempts. Please try again later.',
                'error_code': 'RATE_LIMITED'
            }, status=429)
        if error_code == 'ACCOUNT_INACTIVE':
            return Response({
                'success': False,
                'message': 'Account is not active',
                'error_code': 'ACCOUNT_INACTIVE'
            }, status=status.HTTP_403_FORBIDDEN)

        # Generate tokens
        access_token, refresh_token, expires_in, refresh_expires_in = generate_jwt_tokens(patient, remember_me)
        # Device fingerprinting
        device_fingerprint = fingerprint_device(device_info, user_agent)
        # Create session
        session = PatientAuthService.create_session(
            patient,
            refresh_token,
            device_info={**device_info, 'fingerprint': device_fingerprint},
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=timezone.now() + timezone.timedelta(seconds=refresh_expires_in)
        )
        # Log login event (HIPAA-safe)
        log_security_event(patient, ip_address, 'login_success', 'Patient login successful')

        # Prepare response
        resp = {
            'success': True,
            'message': 'Login successful',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': expires_in,
                'token_type': 'Bearer',
                'patient': {
                    'id': str(patient.id),
                    'first_name': patient.first_name,
                    'last_name': patient.last_name,
                    'email': patient.email,
                    'phone_number': patient.phone_number,
                    'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                    'email_verified': patient.email_verified,
                    'phone_verified': patient.phone_verified,
                    'is_active': patient.is_active,
                    'last_login': patient.last_login.isoformat() if patient.last_login else None
                }
            }
        }
        return Response(resp, status=status.HTTP_200_OK)
