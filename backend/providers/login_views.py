import logging
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Provider
from .login_serializers import ProviderLoginSerializer
from .auth_utils import check_password, create_access_token, create_refresh_token

logger = logging.getLogger(__name__)

LOGIN_ATTEMPT_LIMIT = 5
LOCKOUT_TIME = timedelta(minutes=30)
RATE_LIMIT_WINDOW = timedelta(minutes=15)
FAILED_ATTEMPT_RESET = timedelta(minutes=15)

class ProviderLoginView(APIView):
    def post(self, request):
        data = request.data
        serializer = ProviderLoginSerializer(data=data)
        if not serializer.is_valid():
            return Response({"success": False, "message": "Invalid request format", "errors": serializer.errors}, status=400)

        identifier = serializer.validated_data['identifier'].strip().lower()
        password = serializer.validated_data['password']
        remember_me = serializer.validated_data.get('remember_me', False)

        provider = Provider.objects.filter(email=identifier).first() or \
                   Provider.objects.filter(phone_number=identifier).first()

        if not provider:
            logger.info(f"Login failed: no provider found for identifier {identifier}")
            return Response({"success": False, "message": "Invalid credentials", "error_code": "INVALID_CREDENTIALS"}, status=401)

        now = timezone.now()
        # Account lockout check
        if provider.locked_until and provider.locked_until > now:
            return Response({"success": False, "message": "Account locked due to failed attempts. Try again later.", "error_code": "ACCOUNT_LOCKED"}, status=423)
        # Account active/verified check
        if not provider.is_active or provider.verification_status != 'verified':
            return Response({"success": False, "message": "Account not verified or inactive", "error_code": "ACCOUNT_NOT_VERIFIED"}, status=403)
        # Password check
        if not check_password(password, provider.password_hash):
            provider.failed_login_attempts += 1
            if provider.failed_login_attempts >= LOGIN_ATTEMPT_LIMIT:
                provider.locked_until = now + LOCKOUT_TIME
                provider.failed_login_attempts = 0
            provider.save(update_fields=["failed_login_attempts", "locked_until"])
            logger.info(f"Login failed: invalid password for {provider.email}")
            return Response({"success": False, "message": "Invalid credentials", "error_code": "INVALID_CREDENTIALS"}, status=401)
        # Reset failed attempts on success
        provider.failed_login_attempts = 0
        provider.locked_until = None
        provider.last_login = now
        provider.login_count = (provider.login_count or 0) + 1
        provider.save(update_fields=["failed_login_attempts", "locked_until", "last_login", "login_count"])
        # Generate tokens
        access_token, access_exp = create_access_token(provider, remember_me)
        refresh_token, refresh_exp = create_refresh_token(provider, remember_me)
        logger.info(f"Login success for {provider.email}")
        return Response({
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": int((access_exp - datetime.utcnow()).total_seconds()),
                "token_type": "Bearer",
                "provider": {
                    "id": str(provider.id),
                    "first_name": provider.first_name,
                    "last_name": provider.last_name,
                    "email": provider.email,
                    "specialization": provider.specialization,
                    "verification_status": provider.verification_status,
                    "is_active": provider.is_active
                }
            }
        }, status=200)
