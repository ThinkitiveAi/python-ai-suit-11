"""
JWT Token Management Views
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .jwt_utils import refresh_access_token
import logging

logger = logging.getLogger(__name__)

class TokenRefreshView(APIView):
    """
    JWT Token Refresh API
    
    Refresh an access token using a valid refresh token.
    """
    
    @swagger_auto_schema(
        operation_description="Refresh access token using a valid refresh token",
        operation_summary="Refresh Access Token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Valid refresh token'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Token refreshed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
                                'access_token_expires_at': openapi.Schema(type=openapi.TYPE_STRING),
                                'refresh_token_expires_at': openapi.Schema(type=openapi.TYPE_STRING),
                                'token_type': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'errors': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: openapi.Response(
                description="Invalid or expired refresh token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'errors': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        },
        tags=['Token Management']
    )
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                "success": False,
                "message": "Refresh token is required",
                "errors": {"refresh_token": ["This field is required"]}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate new tokens
            tokens = refresh_access_token(refresh_token)
            
            logger.info(f"Token refresh successful, ip: {request.META.get('REMOTE_ADDR')}")
            
            return Response({
                "success": True,
                "message": "Token refreshed successfully",
                "data": tokens
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.warning(f"Token refresh failed: {str(e)}, ip: {request.META.get('REMOTE_ADDR')}")
            
            return Response({
                "success": False,
                "message": "Token refresh failed",
                "errors": {"refresh_token": [str(e)]}
            }, status=status.HTTP_401_UNAUTHORIZED)

class TokenValidateView(APIView):
    """
    JWT Token Validation API
    
    Validate an access token and return user information.
    """
    
    @swagger_auto_schema(
        operation_description="Validate an access token and return user information",
        operation_summary="Validate Access Token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['access_token'],
            properties={
                'access_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Access token to validate'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Token is valid",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                                'user_type': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'token_type': openapi.Schema(type=openapi.TYPE_STRING),
                                'expires_at': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'errors': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: openapi.Response(
                description="Invalid or expired token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'errors': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        },
        tags=['Token Management']
    )
    def post(self, request):
        access_token = request.data.get('access_token')
        
        if not access_token:
            return Response({
                "success": False,
                "message": "Access token is required",
                "errors": {"access_token": ["This field is required"]}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .jwt_utils import decode_token
            
            # Decode and validate token
            payload = decode_token(access_token)
            
            logger.info(f"Token validation successful for user: {payload.get('email')}, ip: {request.META.get('REMOTE_ADDR')}")
            
            return Response({
                "success": True,
                "message": "Token is valid",
                "data": {
                    "user_id": payload.get('user_id'),
                    "user_type": payload.get('user_type'),
                    "email": payload.get('email'),
                    "first_name": payload.get('first_name'),
                    "last_name": payload.get('last_name'),
                    "token_type": payload.get('token_type'),
                    "expires_at": payload.get('exp')
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.warning(f"Token validation failed: {str(e)}, ip: {request.META.get('REMOTE_ADDR')}")
            
            return Response({
                "success": False,
                "message": "Token validation failed",
                "errors": {"access_token": [str(e)]}
            }, status=status.HTTP_401_UNAUTHORIZED)
