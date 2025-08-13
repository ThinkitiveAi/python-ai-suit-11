"""
API views for appointment booking and management
"""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime, date

from .appointment_models import Appointment, AppointmentHistory
from .appointment_serializers import (
    AppointmentCreateSerializer,
    AppointmentListSerializer,
    AppointmentDetailSerializer,
    AppointmentUpdateSerializer,
    AppointmentHistorySerializer,
    AppointmentCreateResponseSerializer,
    AppointmentListResponseSerializer,
    AppointmentErrorResponseSerializer,
)
from .availability_models import AppointmentSlot
from .patient_models import Patient
from .models import Provider

logger = logging.getLogger(__name__)


class AppointmentCreateView(APIView):
    """API view for creating new appointments"""
    
    @swagger_auto_schema(
        operation_description="Create a new appointment booking",
        request_body=AppointmentCreateSerializer,
        responses={
            201: AppointmentCreateResponseSerializer,
            400: AppointmentErrorResponseSerializer,
            404: AppointmentErrorResponseSerializer,
        },
        tags=['Appointments']
    )
    def post(self, request):
        """Create a new appointment"""
        try:
            with transaction.atomic():
                serializer = AppointmentCreateSerializer(
                    data=request.data,
                    context={'created_by': 'api_user'}
                )
                
                if serializer.is_valid():
                    appointment = serializer.save()
                    
                    logger.info(f"Appointment created successfully: {appointment.appointment_number}")
                    
                    return Response({
                        'success': True,
                        'message': 'Appointment created successfully',
                        'data': AppointmentDetailSerializer(appointment).data
                    }, status=status.HTTP_201_CREATED)
                
                else:
                    logger.warning(f"Appointment creation failed: {serializer.errors}")
                    return Response({
                        'success': False,
                        'message': 'Appointment creation failed',
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error creating appointment: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentListView(APIView):
    """API view for listing appointments"""
    
    @swagger_auto_schema(
        operation_description="Get list of appointments with optional filtering",
        manual_parameters=[
            openapi.Parameter('patient_id', openapi.IN_QUERY, description="Filter by patient ID", type=openapi.TYPE_STRING),
            openapi.Parameter('provider_id', openapi.IN_QUERY, description="Filter by provider ID", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by appointment status", type=openapi.TYPE_STRING),
            openapi.Parameter('appointment_date', openapi.IN_QUERY, description="Filter by appointment date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('appointment_mode', openapi.IN_QUERY, description="Filter by appointment mode", type=openapi.TYPE_STRING),
            openapi.Parameter('limit', openapi.IN_QUERY, description="Limit number of results", type=openapi.TYPE_INTEGER),
            openapi.Parameter('offset', openapi.IN_QUERY, description="Offset for pagination", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: AppointmentListResponseSerializer,
            400: AppointmentErrorResponseSerializer,
        },
        tags=['Appointments']
    )
    def get(self, request):
        """Get list of appointments with filtering"""
        try:
            # Get query parameters
            patient_id = request.query_params.get('patient_id')
            provider_id = request.query_params.get('provider_id')
            appointment_status = request.query_params.get('status')
            appointment_date = request.query_params.get('appointment_date')
            appointment_mode = request.query_params.get('appointment_mode')
            limit = request.query_params.get('limit', 50)
            offset = request.query_params.get('offset', 0)
            
            # Convert limit and offset to integers
            try:
                limit = int(limit)
                offset = int(offset)
                if limit > 500:  # Maximum limit
                    limit = 500
            except ValueError:
                limit = 50
                offset = 0
            
            # Build queryset
            queryset = Appointment.objects.select_related('patient', 'provider').all()
            
            # Apply filters
            if patient_id:
                queryset = queryset.filter(patient_id=patient_id)
            
            if provider_id:
                queryset = queryset.filter(provider_id=provider_id)
            
            if appointment_status:
                queryset = queryset.filter(status=appointment_status)
            
            if appointment_date:
                try:
                    date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
                    queryset = queryset.filter(appointment_date=date_obj)
                except ValueError:
                    return Response({
                        'success': False,
                        'message': 'Invalid date format. Use YYYY-MM-DD',
                        'errors': {'appointment_date': ['Invalid date format']}
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if appointment_mode:
                queryset = queryset.filter(appointment_mode=appointment_mode)
            
            # Get total count
            total_count = queryset.count()
            
            # Apply pagination
            appointments = queryset[offset:offset + limit]
            
            # Serialize data
            serializer = AppointmentListSerializer(appointments, many=True)
            
            return Response({
                'success': True,
                'message': 'Appointments retrieved successfully',
                'count': total_count,
                'limit': limit,
                'offset': offset,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error retrieving appointments: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentDetailView(APIView):
    """API view for appointment details"""
    
    @swagger_auto_schema(
        operation_description="Get appointment details by ID",
        responses={
            200: AppointmentCreateResponseSerializer,
            404: AppointmentErrorResponseSerializer,
        },
        tags=['Appointments']
    )
    def get(self, request, appointment_id):
        """Get appointment details"""
        try:
            appointment = Appointment.objects.select_related(
                'patient', 'provider', 'appointment_slot'
            ).get(id=appointment_id)
            
            serializer = AppointmentDetailSerializer(appointment)
            
            return Response({
                'success': True,
                'message': 'Appointment details retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Appointment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Appointment not found',
                'errors': {'appointment_id': ['Appointment not found']}
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Error retrieving appointment details: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentUpdateView(APIView):
    """API view for updating appointments"""
    
    @swagger_auto_schema(
        operation_description="Update appointment details",
        request_body=AppointmentUpdateSerializer,
        responses={
            200: AppointmentCreateResponseSerializer,
            400: AppointmentErrorResponseSerializer,
            404: AppointmentErrorResponseSerializer,
        },
        tags=['Appointments']
    )
    def put(self, request, appointment_id):
        """Update appointment"""
        try:
            with transaction.atomic():
                appointment = Appointment.objects.get(id=appointment_id)
                
                serializer = AppointmentUpdateSerializer(
                    appointment,
                    data=request.data,
                    partial=True,
                    context={'updated_by': 'api_user'}
                )
                
                if serializer.is_valid():
                    updated_appointment = serializer.save()
                    
                    logger.info(f"Appointment updated successfully: {updated_appointment.appointment_number}")
                    
                    return Response({
                        'success': True,
                        'message': 'Appointment updated successfully',
                        'data': AppointmentDetailSerializer(updated_appointment).data
                    }, status=status.HTTP_200_OK)
                
                else:
                    logger.warning(f"Appointment update failed: {serializer.errors}")
                    return Response({
                        'success': False,
                        'message': 'Appointment update failed',
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        except Appointment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Appointment not found',
                'errors': {'appointment_id': ['Appointment not found']}
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Error updating appointment: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentCancelView(APIView):
    """API view for cancelling appointments"""
    
    @swagger_auto_schema(
        operation_description="Cancel an appointment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'cancellation_reason': openapi.Schema(type=openapi.TYPE_STRING, description='Reason for cancellation'),
                'cancelled_by': openapi.Schema(type=openapi.TYPE_STRING, description='Who is cancelling the appointment'),
            },
            required=['cancellation_reason']
        ),
        responses={
            200: AppointmentCreateResponseSerializer,
            400: AppointmentErrorResponseSerializer,
            404: AppointmentErrorResponseSerializer,
        },
        tags=['Appointments']
    )
    def post(self, request, appointment_id):
        """Cancel appointment"""
        try:
            with transaction.atomic():
                appointment = Appointment.objects.get(id=appointment_id)
                
                # Check if appointment can be cancelled
                if not appointment.can_be_cancelled:
                    return Response({
                        'success': False,
                        'message': 'Appointment cannot be cancelled',
                        'errors': {'status': ['Appointment cannot be cancelled in current status']}
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update appointment status
                appointment.status = 'cancelled'
                appointment.cancelled_at = timezone.now()
                appointment.cancellation_reason = request.data.get('cancellation_reason', '')
                appointment.cancelled_by = request.data.get('cancelled_by', 'api_user')
                appointment.save()
                
                # Update appointment slot if linked
                if appointment.appointment_slot:
                    appointment.appointment_slot.status = 'available'
                    appointment.appointment_slot.patient_id = None
                    appointment.appointment_slot.save()
                
                # Create history entry
                AppointmentHistory.objects.create(
                    appointment=appointment,
                    action='cancelled',
                    description=f'Appointment cancelled: {appointment.cancellation_reason}',
                    performed_by=appointment.cancelled_by,
                    previous_values={'status': 'scheduled'},
                    new_values={'status': 'cancelled', 'cancelled_at': str(appointment.cancelled_at)}
                )
                
                logger.info(f"Appointment cancelled successfully: {appointment.appointment_number}")
                
                return Response({
                    'success': True,
                    'message': 'Appointment cancelled successfully',
                    'data': AppointmentDetailSerializer(appointment).data
                }, status=status.HTTP_200_OK)
        
        except Appointment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Appointment not found',
                'errors': {'appointment_id': ['Appointment not found']}
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Error cancelling appointment: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentHistoryView(APIView):
    """API view for appointment history"""
    
    @swagger_auto_schema(
        operation_description="Get appointment history",
        responses={
            200: openapi.Response(
                description="Appointment history retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            404: AppointmentErrorResponseSerializer,
        },
        tags=['Appointments']
    )
    def get(self, request, appointment_id):
        """Get appointment history"""
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            history = AppointmentHistory.objects.filter(appointment=appointment)
            
            serializer = AppointmentHistorySerializer(history, many=True)
            
            return Response({
                'success': True,
                'message': 'Appointment history retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Appointment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Appointment not found',
                'errors': {'appointment_id': ['Appointment not found']}
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Error retrieving appointment history: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailableSlotSearchView(APIView):
    """API view for searching available appointment slots"""
    
    @swagger_auto_schema(
        operation_description="Search for available appointment slots",
        manual_parameters=[
            openapi.Parameter('provider_id', openapi.IN_QUERY, description="Provider ID", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('appointment_type', openapi.IN_QUERY, description="Appointment type", type=openapi.TYPE_STRING),
            openapi.Parameter('duration_minutes', openapi.IN_QUERY, description="Required duration in minutes", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Available slots retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            400: AppointmentErrorResponseSerializer,
        },
        tags=['Appointments']
    )
    def get(self, request):
        """Search for available appointment slots"""
        try:
            # Get query parameters
            provider_id = request.query_params.get('provider_id')
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to', date_from)
            appointment_type = request.query_params.get('appointment_type')
            duration_minutes = request.query_params.get('duration_minutes')
            
            # Validate required parameters
            if not provider_id or not date_from:
                return Response({
                    'success': False,
                    'message': 'Missing required parameters',
                    'errors': {'detail': 'provider_id and date_from are required'}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate provider exists
            try:
                provider = Provider.objects.get(id=provider_id, is_active=True)
            except Provider.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Provider not found',
                    'errors': {'provider_id': ['Provider not found or inactive']}
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Parse dates
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid date format',
                    'errors': {'date': ['Use YYYY-MM-DD format']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Build queryset for available slots
            queryset = AppointmentSlot.objects.filter(
                provider=provider,
                status='available',
                slot_start_time__date__gte=date_from_obj,
                slot_start_time__date__lte=date_to_obj,
                slot_start_time__gte=timezone.now()  # Only future slots
            ).order_by('slot_start_time')
            
            # Filter by appointment type if provided
            if appointment_type:
                queryset = queryset.filter(appointment_type=appointment_type)
            
            # Filter by duration if provided
            if duration_minutes:
                try:
                    duration = int(duration_minutes)
                    # Find slots that have at least the required duration
                    from django.db.models import F
                    from datetime import timedelta
                    
                    queryset = queryset.extra(
                        where=["EXTRACT(EPOCH FROM (slot_end_time - slot_start_time))/60 >= %s"],
                        params=[duration]
                    )
                except ValueError:
                    pass
            
            # Limit results
            slots = queryset[:100]  # Limit to 100 slots
            
            # Format response data
            slot_data = []
            for slot in slots:
                slot_data.append({
                    'id': slot.id,
                    'slot_start_time': slot.slot_start_time,
                    'slot_end_time': slot.slot_end_time,
                    'local_start_time': slot.get_local_start_time(),
                    'local_end_time': slot.get_local_end_time(),
                    'duration_minutes': int((slot.slot_end_time - slot.slot_start_time).total_seconds() / 60),
                    'appointment_type': slot.appointment_type,
                    'provider_name': f"{provider.first_name} {provider.last_name}",
                })
            
            return Response({
                'success': True,
                'message': f'Found {len(slot_data)} available slots',
                'data': slot_data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error searching available slots: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
