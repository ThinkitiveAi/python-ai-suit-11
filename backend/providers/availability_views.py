from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .availability_models import Availability, AppointmentSlot
from .availability_serializers import (
    AvailabilityCreateSerializer,
    AvailabilityDetailSerializer,
    AppointmentSlotSerializer,
    ProviderAvailabilitySerializer,
    AvailabilityUpdateSerializer,
    AvailabilitySearchResponseSerializer,
    SlotSearchSerializer,
    AllProviderAvailabilitySerializer
)
from .models import Provider
from .authentication import JWTAuthentication
from .permissions import IsProviderAuthenticated


class ProviderAvailabilityCreateView(APIView):
    """Create availability slots for a provider"""

    @swagger_auto_schema(
        request_body=AvailabilityCreateSerializer,
        responses={
            201: openapi.Response(
                description="Availability slots created successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Availability slots created successfully",
                        "data": {
                            "availability_id": "uuid-here",
                            "slots_created": 32,
                            "date_range": {
                                "start": "2024-02-15",
                                "end": "2024-08-15"
                            },
                            "total_appointments_available": 224
                        }
                    }
                }
            ),
            400: "Bad Request - Validation errors"
        }
    )
    def post(self, request, provider_id):
        """Create new availability slots"""
        # Get the provider object
        try:
            provider = Provider.objects.get(id=provider_id, is_active=True)
        except Provider.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Provider not found or inactive',
                'errors': {'provider_id': ['Provider not found']}
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AvailabilityCreateSerializer(data=request.data, context={'request': request, 'provider': provider})
        
        if serializer.is_valid():
            # Check for conflicts with existing availability
            conflicts = self._check_conflicts(provider, serializer.validated_data)
            
            if conflicts:
                return Response({
                    'success': False,
                    'message': 'Conflicting availability slots found',
                    'conflicts': conflicts
                }, status=status.HTTP_400_BAD_REQUEST)
            
            availability = serializer.save()
            
            # Count generated slots
            slots_count = AppointmentSlot.objects.filter(availability=availability).count()
            
            # Calculate date range
            date_range = {
                'start': availability.date.strftime('%Y-%m-%d'),
                'end': availability.recurrence_end_date.strftime('%Y-%m-%d') if availability.recurrence_end_date else availability.date.strftime('%Y-%m-%d')
            }
            
            return Response({
                'success': True,
                'message': 'Availability slots created successfully',
                'data': {
                    'availability_id': str(availability.id),
                    'slots_created': slots_count,
                    'date_range': date_range,
                    'total_appointments_available': slots_count * availability.max_appointments_per_slot
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def _check_conflicts(self, provider, validated_data):
        """Check for conflicting availability slots"""
        conflicts = []
        
        # Get existing slots for the provider on the same date
        existing_slots = AppointmentSlot.objects.filter(
            provider=provider,
            slot_start_time__date=validated_data['date'],
            status__in=['available', 'booked']
        )
        
        if existing_slots.exists():
            # Convert new availability times to UTC for comparison
            provider_tz = pytz.timezone(validated_data['timezone'])
            new_start = provider_tz.localize(
                datetime.combine(validated_data['date'], validated_data['start_time'])
            ).astimezone(pytz.UTC)
            new_end = provider_tz.localize(
                datetime.combine(validated_data['date'], validated_data['end_time'])
            ).astimezone(pytz.UTC)
            
            for slot in existing_slots:
                # Check for overlap
                if (slot.slot_start_time < new_end and slot.slot_end_time > new_start):
                    conflicts.append({
                        'slot_id': str(slot.id),
                        'conflicting_time': f"{slot.slot_start_time} - {slot.slot_end_time}",
                        'status': slot.status
                    })
        
        return conflicts


class ProviderAvailabilityListView(APIView):
    """Get provider availability"""

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('provider_id', openapi.IN_PATH, description="Provider UUID", type=openapi.TYPE_STRING),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status", type=openapi.TYPE_STRING),
            openapi.Parameter('appointment_type', openapi.IN_QUERY, description="Filter by appointment type", type=openapi.TYPE_STRING),
            openapi.Parameter('timezone', openapi.IN_QUERY, description="Timezone for response", type=openapi.TYPE_STRING),
        ],
        responses={200: "Success"}
    )
    def get(self, request, provider_id):
        """Get availability for a specific provider"""
        # Validate required parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'success': False,
                'message': 'start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get provider
        provider = get_object_or_404(Provider, id=provider_id)
        
        # Build query filters
        filters = Q(
            provider=provider,
            slot_start_time__date__gte=start_date,
            slot_start_time__date__lte=end_date
        )
        
        # Add optional filters
        if request.query_params.get('status'):
            filters &= Q(status=request.query_params.get('status'))
        
        if request.query_params.get('appointment_type'):
            filters &= Q(appointment_type=request.query_params.get('appointment_type'))
        
        # Get slots
        slots = AppointmentSlot.objects.filter(filters).select_related(
            'availability', 'provider'
        ).order_by('slot_start_time')
        
        # Group slots by date
        availability_by_date = {}
        total_slots = 0
        available_slots = 0
        booked_slots = 0
        cancelled_slots = 0
        
        for slot in slots:
            local_start = slot.get_local_start_time()
            date_str = local_start.strftime('%Y-%m-%d')
            
            if date_str not in availability_by_date:
                availability_by_date[date_str] = []
            
            availability_by_date[date_str].append(slot)
            
            # Count slots by status
            total_slots += 1
            if slot.status == 'available':
                available_slots += 1
            elif slot.status == 'booked':
                booked_slots += 1
            elif slot.status == 'cancelled':
                cancelled_slots += 1
        
        # Format response
        availability_data = []
        for date_str, date_slots in availability_by_date.items():
            slots_data = []
            for slot in date_slots:
                local_start = slot.get_local_start_time()
                local_end = slot.get_local_end_time()
                
                slots_data.append({
                    'slot_id': str(slot.id),
                    'start_time': local_start.strftime('%H:%M'),
                    'end_time': local_end.strftime('%H:%M'),
                    'status': slot.status,
                    'appointment_type': slot.appointment_type,
                    'location': slot.availability.location,
                    'pricing': slot.availability.pricing
                })
            
            availability_data.append({
                'date': date_str,
                'slots': slots_data
            })
        
        return Response({
            'success': True,
            'data': {
                'provider_id': str(provider.id),
                'availability_summary': {
                    'total_slots': total_slots,
                    'available_slots': available_slots,
                    'booked_slots': booked_slots,
                    'cancelled_slots': cancelled_slots
                },
                'availability': availability_data
            }
        })


class AvailabilitySlotUpdateView(APIView):
    """Update or delete specific availability slot"""

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['available', 'booked', 'cancelled', 'blocked']),
                'notes': openapi.Schema(type=openapi.TYPE_STRING),
                'pricing': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'base_fee': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'insurance_accepted': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'currency': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            }
        ),
        responses={200: "Slot updated successfully", 404: "Slot not found"}
    )
    def put(self, request, provider_id, slot_id):
        """Update a specific availability slot"""
        # Get the provider object
        try:
            provider = Provider.objects.get(id=provider_id, is_active=True)
        except Provider.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Provider not found or inactive',
                'errors': {'provider_id': ['Provider not found']}
            }, status=status.HTTP_404_NOT_FOUND)
        
        slot = get_object_or_404(AppointmentSlot, id=slot_id, provider=provider)
        
        # Update slot fields
        if 'status' in request.data:
            new_status = request.data['status']
            
            # Validate status change
            if slot.status == 'booked' and new_status != 'booked' and not request.data.get('force_update', False):
                return Response({
                    'success': False,
                    'message': 'Cannot change status of booked slot without force_update=true'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            slot.status = new_status
        
        # Update availability notes if provided
        if 'notes' in request.data:
            slot.availability.notes = request.data['notes']
            slot.availability.save()
        
        # Update pricing if provided
        if 'pricing' in request.data:
            slot.availability.pricing = request.data['pricing']
            slot.availability.save()
        
        slot.save()
        
        return Response({
            'success': True,
            'message': 'Slot updated successfully',
            'data': {
                'slot_id': str(slot.id),
                'status': slot.status,
                'updated_at': slot.updated_at
            }
        })

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('delete_recurring', openapi.IN_QUERY, description="Delete all recurring instances", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('reason', openapi.IN_QUERY, description="Reason for deletion", type=openapi.TYPE_STRING),
        ],
        responses={200: "Slot deleted successfully", 404: "Slot not found"}
    )
    def delete(self, request, provider_id, slot_id):
        """Delete a specific availability slot"""
        # Get the provider object
        try:
            provider = Provider.objects.get(id=provider_id, is_active=True)
        except Provider.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Provider not found or inactive',
                'errors': {'provider_id': ['Provider not found']}
            }, status=status.HTTP_404_NOT_FOUND)
        
        slot = get_object_or_404(AppointmentSlot, id=slot_id, provider=provider)
        
        # Check if slot is booked
        if slot.status == 'booked':
            return Response({
                'success': False,
                'message': 'Cannot delete booked slot. Cancel the appointment first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        delete_recurring = request.query_params.get('delete_recurring', 'false').lower() == 'true'
        reason = request.query_params.get('reason', '')
        
        deleted_count = 1
        
        if delete_recurring and slot.availability.is_recurring:
            # Delete all slots from the same recurring availability
            related_slots = AppointmentSlot.objects.filter(
                availability=slot.availability,
                status__in=['available', 'blocked', 'cancelled']
            )
            deleted_count = related_slots.count()
            related_slots.delete()
            
            # Also delete the availability record
            slot.availability.delete()
        else:
            slot.delete()
        
        return Response({
            'success': True,
            'message': f'Successfully deleted {deleted_count} slot(s)',
            'data': {
                'deleted_slots': deleted_count,
                'reason': reason
            }
        })


class AvailabilitySearchView(APIView):
    """Search for available appointment slots"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="Specific date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date for range", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date for range", type=openapi.TYPE_STRING),
            openapi.Parameter('specialization', openapi.IN_QUERY, description="Provider specialization", type=openapi.TYPE_STRING),
            openapi.Parameter('location', openapi.IN_QUERY, description="Location (city, state, zip)", type=openapi.TYPE_STRING),
            openapi.Parameter('appointment_type', openapi.IN_QUERY, description="Type of appointment", type=openapi.TYPE_STRING),
            openapi.Parameter('insurance_accepted', openapi.IN_QUERY, description="Insurance accepted", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('timezone', openapi.IN_QUERY, description="Timezone for results", type=openapi.TYPE_STRING),
            openapi.Parameter('available_only', openapi.IN_QUERY, description="Show only available slots", type=openapi.TYPE_BOOLEAN, default=True),
        ],
        responses={200: "Search results"}
    )
    def get(self, request):
        """Search for available appointment slots"""
        # Parse date parameters
        date_filter = None
        if request.query_params.get('date'):
            try:
                specific_date = datetime.strptime(request.query_params.get('date'), '%Y-%m-%d').date()
                date_filter = Q(slot_start_time__date=specific_date)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        elif request.query_params.get('start_date') and request.query_params.get('end_date'):
            try:
                start_date = datetime.strptime(request.query_params.get('start_date'), '%Y-%m-%d').date()
                end_date = datetime.strptime(request.query_params.get('end_date'), '%Y-%m-%d').date()
                date_filter = Q(slot_start_time__date__gte=start_date, slot_start_time__date__lte=end_date)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to next 30 days
            today = timezone.now().date()
            end_date = today + timedelta(days=30)
            date_filter = Q(slot_start_time__date__gte=today, slot_start_time__date__lte=end_date)
        
        # Build query filters
        filters = date_filter
        
        # Filter by availability status
        available_only = request.query_params.get('available_only', 'true').lower() == 'true'
        if available_only:
            filters &= Q(status='available')
        
        # Filter by appointment type
        if request.query_params.get('appointment_type'):
            filters &= Q(appointment_type=request.query_params.get('appointment_type'))
        
        # Filter by provider specialization
        if request.query_params.get('specialization'):
            filters &= Q(provider__specialization__icontains=request.query_params.get('specialization'))
        
        # Filter by location
        if request.query_params.get('location'):
            location_query = request.query_params.get('location')
            filters &= (
                Q(availability__location__address__icontains=location_query) |
                Q(provider__clinic_address__address__icontains=location_query)
            )
        
        # Filter by insurance acceptance
        if request.query_params.get('insurance_accepted'):
            insurance_accepted = request.query_params.get('insurance_accepted').lower() == 'true'
            filters &= Q(availability__pricing__insurance_accepted=insurance_accepted)
        
        # Filter by maximum price
        if request.query_params.get('max_price'):
            try:
                max_price = float(request.query_params.get('max_price'))
                filters &= Q(availability__pricing__base_fee__lte=max_price)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid max_price format'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get slots with related data
        slots = AppointmentSlot.objects.filter(filters).select_related(
            'provider', 'availability'
        ).order_by('provider_id', 'slot_start_time')[:100]  # Limit results
        
        # Group slots by provider
        providers_data = {}
        for slot in slots:
            provider_id = str(slot.provider.id)
            if provider_id not in providers_data:
                providers_data[provider_id] = {
                    'provider': slot.provider,
                    'slots': []
                }
            providers_data[provider_id]['slots'].append(slot)
        
        # Format response
        results = []
        for provider_data in providers_data.values():
            provider = provider_data['provider']
            available_slots = []
            
            for slot in provider_data['slots']:
                local_start = slot.get_local_start_time()
                local_end = slot.get_local_end_time()
                
                available_slots.append({
                    'slot_id': str(slot.id),
                    'date': local_start.strftime('%Y-%m-%d'),
                    'start_time': local_start.strftime('%H:%M'),
                    'end_time': local_end.strftime('%H:%M'),
                    'appointment_type': slot.appointment_type,
                    'location': slot.availability.location,
                    'pricing': slot.availability.pricing,
                    'special_requirements': slot.availability.special_requirements or []
                })
            
            results.append({
                'provider': {
                    'id': str(provider.id),
                    'name': f"Dr. {provider.first_name} {provider.last_name}",
                    'specialization': provider.specialization,
                    'years_of_experience': provider.years_of_experience,
                    'rating': 4.5,  # TODO: Calculate from reviews
                    'clinic_address': provider.clinic_address.get('address', '') if provider.clinic_address else ''
                },
                'available_slots': available_slots
            })
        
        # Build search criteria for response
        search_criteria = {}
        if request.query_params.get('date'):
            search_criteria['date'] = request.query_params.get('date')
        if request.query_params.get('specialization'):
            search_criteria['specialization'] = request.query_params.get('specialization')
        if request.query_params.get('location'):
            search_criteria['location'] = request.query_params.get('location')
        
        return Response({
            'success': True,
            'data': {
                'search_criteria': search_criteria,
                'total_results': len(results),
                'results': results
            }
        })


class AllProviderAvailabilityListView(APIView):
    """Get all provider availability data with comprehensive filtering and pagination"""
    permission_classes = [permissions.AllowAny]  # Can be restricted based on requirements
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('provider_id', openapi.IN_QUERY, description="Filter by provider ID (UUID)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Filter from date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Filter to date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('appointment_type', openapi.IN_QUERY, description="Filter by appointment type", type=openapi.TYPE_STRING),
            openapi.Parameter('specialization', openapi.IN_QUERY, description="Filter by provider specialization", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by availability status", type=openapi.TYPE_STRING),
            openapi.Parameter('location_type', openapi.IN_QUERY, description="Filter by location type (clinic, hospital, telemedicine, home_visit)", type=openapi.TYPE_STRING),
            openapi.Parameter('verified_only', openapi.IN_QUERY, description="Show only verified providers", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('is_recurring', openapi.IN_QUERY, description="Filter by recurring availability", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('limit', openapi.IN_QUERY, description="Number of results per page (default: 50, max: 500)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('offset', openapi.IN_QUERY, description="Offset for pagination", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sort_by', openapi.IN_QUERY, description="Sort by field (date, provider_name, appointment_type, status, created_at)", type=openapi.TYPE_STRING),
            openapi.Parameter('order', openapi.IN_QUERY, description="Sort order (asc, desc)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="All provider availability data retrieved successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Retrieved 150 availability records",
                        "data": {
                            "total_count": 1000,
                            "filtered_count": 150,
                            "limit": 50,
                            "offset": 0,
                            "has_next": True,
                            "has_previous": False,
                            "availability_records": []
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid parameters"
        }
    )
    def get(self, request):
        """Get all provider availability data with filtering and pagination"""
        try:
            # Start with all availability records
            queryset = Availability.objects.select_related('provider').prefetch_related('slots')
            
            # Apply filters
            filters = Q()
            
            # Filter by provider ID
            provider_id = request.query_params.get('provider_id')
            if provider_id:
                try:
                    filters &= Q(provider_id=provider_id)
                except ValueError:
                    return Response({
                        'success': False,
                        'message': 'Invalid provider_id format'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Filter by date range
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            if date_from:
                try:
                    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                    filters &= Q(date__gte=date_from)
                except ValueError:
                    return Response({
                        'success': False,
                        'message': 'Invalid date_from format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if date_to:
                try:
                    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                    filters &= Q(date__lte=date_to)
                except ValueError:
                    return Response({
                        'success': False,
                        'message': 'Invalid date_to format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Filter by appointment type
            appointment_type = request.query_params.get('appointment_type')
            if appointment_type:
                filters &= Q(appointment_type=appointment_type)
            
            # Filter by provider specialization
            specialization = request.query_params.get('specialization')
            if specialization:
                filters &= Q(provider__specialization__icontains=specialization)
            
            # Filter by availability status
            availability_status = request.query_params.get('status')
            if availability_status:
                filters &= Q(status=availability_status)
            
            # Filter by location type
            location_type = request.query_params.get('location_type')
            if location_type:
                filters &= Q(location__type=location_type)
            
            # Filter by verified providers only
            verified_only = request.query_params.get('verified_only')
            if verified_only and verified_only.lower() == 'true':
                filters &= Q(provider__is_verified=True)
            
            # Filter by recurring availability
            is_recurring = request.query_params.get('is_recurring')
            if is_recurring is not None:
                is_recurring_bool = is_recurring.lower() == 'true'
                filters &= Q(is_recurring=is_recurring_bool)
            
            # Apply filters to queryset
            queryset = queryset.filter(filters)
            
            # Get total count before pagination
            total_count = Availability.objects.count()
            filtered_count = queryset.count()
            
            # Sorting
            sort_by = request.query_params.get('sort_by', 'date')
            order = request.query_params.get('order', 'asc')
            
            # Map sort fields
            sort_mapping = {
                'date': 'date',
                'provider_name': 'provider__first_name',
                'appointment_type': 'appointment_type',
                'status': 'status',
                'created_at': 'created_at'
            }
            
            if sort_by in sort_mapping:
                sort_field = sort_mapping[sort_by]
                if order.lower() == 'desc':
                    sort_field = f'-{sort_field}'
                queryset = queryset.order_by(sort_field)
            else:
                queryset = queryset.order_by('date')
            
            # Pagination
            limit = min(int(request.query_params.get('limit', 50)), 500)  # Max 500
            offset = int(request.query_params.get('offset', 0))
            
            # Calculate pagination info
            has_next = (offset + limit) < filtered_count
            has_previous = offset > 0
            
            # Apply pagination
            paginated_queryset = queryset[offset:offset + limit]
            
            # Serialize data
            serializer = AllProviderAvailabilitySerializer(paginated_queryset, many=True)
            
            return Response({
                'success': True,
                'message': f'Retrieved {len(serializer.data)} availability records',
                'data': {
                    'total_count': total_count,
                    'filtered_count': filtered_count,
                    'limit': limit,
                    'offset': offset,
                    'has_next': has_next,
                    'has_previous': has_previous,
                    'availability_records': serializer.data
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in AllProviderAvailabilityListView: {str(e)}")
            
            return Response({
                'success': False,
                'message': 'An error occurred while fetching availability data',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailabilitySlotListView(APIView):
    """Get available appointment slots for a specific availability record"""
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('availability_id', openapi.IN_PATH, description="Availability record ID", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by slot status (available, booked, cancelled)", type=openapi.TYPE_STRING),
            openapi.Parameter('date', openapi.IN_QUERY, description="Filter by specific date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('limit', openapi.IN_QUERY, description="Number of slots to return (default: 50)", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Available appointment slots retrieved successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Retrieved 15 available slots",
                        "data": {
                            "availability_id": "uuid-here",
                            "total_slots": 192,
                            "available_slots": 15,
                            "slots": []
                        }
                    }
                }
            ),
            404: "Availability record not found"
        }
    )
    def get(self, request, availability_id):
        """Get available appointment slots for a specific availability record"""
        try:
            # Get the availability record
            try:
                availability = Availability.objects.get(id=availability_id)
            except Availability.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Availability record not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get slots for this availability
            slots_queryset = AppointmentSlot.objects.filter(availability=availability)
            
            # Apply filters
            slot_status = request.query_params.get('status', 'available')
            if slot_status:
                slots_queryset = slots_queryset.filter(status=slot_status)
            
            # Filter by date if provided
            date_filter = request.query_params.get('date')
            if date_filter:
                try:
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    slots_queryset = slots_queryset.filter(slot_start_time__date=filter_date)
                except ValueError:
                    return Response({
                        'success': False,
                        'message': 'Invalid date format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Limit results
            limit = int(request.query_params.get('limit', 50))
            slots_queryset = slots_queryset.order_by('slot_start_time')[:limit]
            
            # Serialize slots
            slots_data = []
            for slot in slots_queryset:
                local_start = slot.get_local_start_time()
                local_end = slot.get_local_end_time()
                
                slots_data.append({
                    'slot_id': str(slot.id),
                    'date': local_start.strftime('%Y-%m-%d'),
                    'start_time': local_start.strftime('%H:%M'),
                    'end_time': local_end.strftime('%H:%M'),
                    'status': slot.status,
                    'appointment_type': slot.appointment_type,
                    'booking_reference': slot.booking_reference,
                    'utc_start_time': slot.slot_start_time.isoformat(),
                    'utc_end_time': slot.slot_end_time.isoformat()
                })
            
            # Get total counts
            total_slots = AppointmentSlot.objects.filter(availability=availability).count()
            available_slots = AppointmentSlot.objects.filter(availability=availability, status='available').count()
            
            return Response({
                'success': True,
                'message': f'Retrieved {len(slots_data)} slots',
                'data': {
                    'availability_id': str(availability.id),
                    'provider': {
                        'id': str(availability.provider.id),
                        'name': f"Dr. {availability.provider.first_name} {availability.provider.last_name}",
                        'specialization': availability.provider.specialization
                    },
                    'availability_date': availability.date.strftime('%Y-%m-%d'),
                    'total_slots': total_slots,
                    'available_slots': available_slots,
                    'filtered_slots_count': len(slots_data),
                    'slots': slots_data
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in AvailabilitySlotListView: {str(e)}")
            
            return Response({
                'success': False,
                'message': 'An error occurred while fetching slots',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# URL patterns for the availability views
from django.urls import path

availability_urlpatterns = [
    path('availability', ProviderAvailabilityCreateView.as_view(), name='provider-availability-create'),
    path('<uuid:provider_id>/availability', ProviderAvailabilityListView.as_view(), name='provider-availability-list'),
    path('availability/<uuid:slot_id>', AvailabilitySlotUpdateView.as_view(), name='availability-slot-update'),
]

# Search endpoint (separate from provider-specific endpoints)
search_urlpatterns = [
    path('availability/search', AvailabilitySearchView.as_view(), name='availability-search'),
]
