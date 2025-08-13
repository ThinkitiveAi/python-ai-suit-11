from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from .models import Provider
from .patient_models import Patient
from .dropdown_serializers import (
    ProviderDropdownSerializer,
    PatientDropdownSerializer,
    ProviderListResponseSerializer,
    PatientListResponseSerializer
)
from .serializers import ErrorResponseSerializer
import logging

logger = logging.getLogger(__name__)


class ProviderListView(APIView):
    """
    Provider List API for Dropdown
    
    Get all active and verified providers for dropdown selection.
    """
    
    @swagger_auto_schema(
        operation_description="Get list of all active providers for dropdown",
        operation_summary="Get Providers for Dropdown",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search providers by name, email, or specialization",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'specialization',
                openapi.IN_QUERY,
                description="Filter by specialization",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'verified_only',
                openapi.IN_QUERY,
                description="Show only verified providers (default: true)",
                type=openapi.TYPE_BOOLEAN,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Providers retrieved successfully",
                schema=ProviderListResponseSerializer
            ),
            400: openapi.Response(
                description="Bad request",
                schema=ErrorResponseSerializer
            )
        },
        tags=['Dropdown APIs']
    )
    def get(self, request):
        try:
            # Get query parameters
            search = request.query_params.get('search', '').strip()
            specialization = request.query_params.get('specialization', '').strip()
            verified_only = request.query_params.get('verified_only', 'true').lower() == 'true'
            
            # Base queryset - active providers only
            queryset = Provider.objects.filter(is_active=True)
            
            # Filter by verification status
            if verified_only:
                queryset = queryset.filter(verification_status='verified')
            
            # Filter by specialization
            if specialization:
                queryset = queryset.filter(specialization__icontains=specialization)
            
            # Search functionality
            if search:
                queryset = queryset.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(specialization__icontains=search)
                )
            
            # Order by name
            queryset = queryset.order_by('first_name', 'last_name')
            
            # Serialize data
            serializer = ProviderDropdownSerializer(queryset, many=True)
            
            logger.info(f"Provider list retrieved: {len(serializer.data)} providers, search: '{search}', specialization: '{specialization}'")
            
            return Response({
                "success": True,
                "message": "Providers retrieved successfully",
                "data": serializer.data,
                "count": len(serializer.data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving provider list: {str(e)}")
            return Response({
                "success": False,
                "message": "Failed to retrieve providers",
                "errors": {"general": [str(e)]}
            }, status=status.HTTP_400_BAD_REQUEST)


class PatientListView(APIView):
    """
    Patient List API for Dropdown
    
    Get all active patients for dropdown selection.
    """
    
    @swagger_auto_schema(
        operation_description="Get list of all active patients for dropdown",
        operation_summary="Get Patients for Dropdown",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search patients by name, email, or phone",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'verified_only',
                openapi.IN_QUERY,
                description="Show only email verified patients (default: false)",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Limit number of results (default: 100, max: 500)",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Patients retrieved successfully",
                schema=PatientListResponseSerializer
            ),
            400: openapi.Response(
                description="Bad request",
                schema=ErrorResponseSerializer
            )
        },
        tags=['Dropdown APIs']
    )
    def get(self, request):
        try:
            # Get query parameters
            search = request.query_params.get('search', '').strip()
            verified_only = request.query_params.get('verified_only', 'false').lower() == 'true'
            limit = int(request.query_params.get('limit', 100))
            
            # Validate limit
            if limit > 500:
                limit = 500
            elif limit < 1:
                limit = 100
            
            # Base queryset - active patients only
            queryset = Patient.objects.filter(is_active=True)
            
            # Filter by email verification status
            if verified_only:
                queryset = queryset.filter(email_verified=True)
            
            # Search functionality
            if search:
                queryset = queryset.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(middle_name__icontains=search) |
                    Q(preferred_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(phone_number__icontains=search)
                )
            
            # Order by name and limit results
            queryset = queryset.order_by('first_name', 'last_name')[:limit]
            
            # Serialize data
            serializer = PatientDropdownSerializer(queryset, many=True)
            
            logger.info(f"Patient list retrieved: {len(serializer.data)} patients, search: '{search}', verified_only: {verified_only}")
            
            return Response({
                "success": True,
                "message": "Patients retrieved successfully",
                "data": serializer.data,
                "count": len(serializer.data)
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Invalid parameter in patient list request: {str(e)}")
            return Response({
                "success": False,
                "message": "Invalid parameters",
                "errors": {"parameters": [str(e)]}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error retrieving patient list: {str(e)}")
            return Response({
                "success": False,
                "message": "Failed to retrieve patients",
                "errors": {"general": [str(e)]}
            }, status=status.HTTP_400_BAD_REQUEST)
