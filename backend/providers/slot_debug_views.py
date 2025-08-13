from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .availability_models import AppointmentSlot
from .models import Provider
import logging

logger = logging.getLogger(__name__)

class AvailableSlotIdsView(APIView):
    """
    Debug API to show all available appointment slot IDs
    This helps debug appointment creation issues
    """
    
    @swagger_auto_schema(
        operation_description="Get all available appointment slot IDs for debugging",
        operation_summary="Debug - Available Slot IDs",
        manual_parameters=[
            openapi.Parameter(
                'provider_id',
                openapi.IN_QUERY,
                description="Filter by specific provider ID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=False
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by slot status (default: available)",
                type=openapi.TYPE_STRING,
                default='available'
            ),
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Limit number of results (default: 20)",
                type=openapi.TYPE_INTEGER,
                default=20
            )
        ],
        responses={
            200: openapi.Response(
                description="Available slot IDs retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total_slots': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'available_slots': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'slots': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'slot_id': openapi.Schema(type=openapi.TYPE_STRING),
                                            'provider_id': openapi.Schema(type=openapi.TYPE_STRING),
                                            'provider_name': openapi.Schema(type=openapi.TYPE_STRING),
                                            'slot_start_time': openapi.Schema(type=openapi.TYPE_STRING),
                                            'slot_end_time': openapi.Schema(type=openapi.TYPE_STRING),
                                            'status': openapi.Schema(type=openapi.TYPE_STRING),
                                            'appointment_type': openapi.Schema(type=openapi.TYPE_STRING)
                                        }
                                    )
                                )
                            }
                        )
                    }
                )
            ),
            500: openapi.Response(description="Internal server error")
        },
        tags=['Debug']
    )
    def get(self, request):
        try:
            # Get query parameters
            provider_id = request.GET.get('provider_id')
            slot_status = request.GET.get('status', 'available')
            limit = min(int(request.GET.get('limit', 20)), 100)  # Max 100 results
            
            # Build queryset
            queryset = AppointmentSlot.objects.select_related('provider').all()
            
            # Apply filters
            if provider_id:
                queryset = queryset.filter(provider_id=provider_id)
            
            if slot_status:
                queryset = queryset.filter(status=slot_status)
            
            # Get counts
            total_slots = AppointmentSlot.objects.count()
            available_slots = queryset.count()
            
            # Get limited results
            slots = queryset.order_by('slot_start_time')[:limit]
            
            # Format response data
            slot_data = []
            for slot in slots:
                slot_data.append({
                    'slot_id': str(slot.id),
                    'provider_id': str(slot.provider.id),
                    'provider_name': f"{slot.provider.first_name} {slot.provider.last_name}",
                    'slot_start_time': slot.slot_start_time.isoformat(),
                    'slot_end_time': slot.slot_end_time.isoformat(),
                    'status': slot.status,
                    'appointment_type': slot.appointment_type
                })
            
            logger.info(f"Debug: Retrieved {len(slot_data)} slot IDs (total: {total_slots}, available: {available_slots})")
            
            return Response({
                'success': True,
                'message': f'Found {available_slots} slots matching criteria',
                'data': {
                    'total_slots': total_slots,
                    'available_slots': available_slots,
                    'slots': slot_data
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching available slot IDs: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to fetch available slot IDs',
                'errors': {'general': [str(e)]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SlotValidationView(APIView):
    """
    Debug API to validate a specific slot ID
    """
    
    @swagger_auto_schema(
        operation_description="Validate if a specific slot ID exists and is available",
        operation_summary="Debug - Validate Slot ID",
        manual_parameters=[
            openapi.Parameter(
                'slot_id',
                openapi.IN_QUERY,
                description="Slot ID to validate",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Slot validation result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'slot_exists': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'slot_available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'slot_details': openapi.Schema(type=openapi.TYPE_OBJECT)
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description="Bad request - Missing slot_id"),
            500: openapi.Response(description="Internal server error")
        },
        tags=['Debug']
    )
    def get(self, request):
        try:
            slot_id = request.GET.get('slot_id')
            
            if not slot_id:
                return Response({
                    'success': False,
                    'message': 'slot_id parameter is required',
                    'errors': {'slot_id': ['This field is required']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                slot = AppointmentSlot.objects.select_related('provider').get(id=slot_id)
                
                slot_details = {
                    'slot_id': str(slot.id),
                    'provider_id': str(slot.provider.id),
                    'provider_name': f"{slot.provider.first_name} {slot.provider.last_name}",
                    'slot_start_time': slot.slot_start_time.isoformat(),
                    'slot_end_time': slot.slot_end_time.isoformat(),
                    'status': slot.status,
                    'appointment_type': slot.appointment_type,
                    'created_at': slot.created_at.isoformat(),
                    'updated_at': slot.updated_at.isoformat()
                }
                
                is_available = slot.status == 'available'
                
                return Response({
                    'success': True,
                    'message': f'Slot {"exists and is available" if is_available else "exists but is not available"}',
                    'data': {
                        'slot_exists': True,
                        'slot_available': is_available,
                        'slot_details': slot_details
                    }
                }, status=status.HTTP_200_OK)
                
            except AppointmentSlot.DoesNotExist:
                return Response({
                    'success': True,
                    'message': 'Slot does not exist',
                    'data': {
                        'slot_exists': False,
                        'slot_available': False,
                        'slot_details': None
                    }
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error validating slot ID: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to validate slot ID',
                'errors': {'general': [str(e)]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
