from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from .models import Hearing, HearingUpdate, UserRole
from .serializers import (
    HearingSerializer,
    HearingDetailSerializer,
    HearingUpdateSerializer,
    CreateHearingUpdateSerializer,
    UserSerializer
)


class HearingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing hearings.
    
    - list: Get all hearings for the current user
    - create: Create a new hearing
    - retrieve: Get a specific hearing
    - update/partial_update: Update hearing details
    - destroy: Delete a hearing
    - updates: Get all updates for a hearing
    - my_hearings: Get hearings for current user
    """
    permission_classes = [IsAuthenticated]
    queryset = Hearing.objects.all()
    serializer_class = HearingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'case_number']
    search_fields = ['title', 'case_number', 'description']
    ordering_fields = ['hearing_date', 'created_at']
    ordering = ['-hearing_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HearingDetailSerializer
        return HearingSerializer
    
    def get_queryset(self):
        """Return hearings for the current user (as advocate or client)"""
        user = self.request.user
        return Hearing.objects.filter(
            Q(advocate=user) | Q(client=user)
        ).distinct()
    
    def perform_create(self, serializer):
        """Ensure the user is an advocate when creating a hearing"""
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def updates(self, request, pk=None):
        """Get all updates for a specific hearing"""
        hearing = self.get_object()
        updates = hearing.updates.all()
        serializer = HearingUpdateSerializer(updates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_hearings(self, request):
        """Get hearings for the current user"""
        user = request.user
        hearings = self.get_queryset()
        
        # Separate by advocate and client
        as_advocate = hearings.filter(advocate=user)
        as_client = hearings.filter(client=user)
        
        serializer = self.get_serializer(hearings, many=True)
        return Response({
            'total_count': hearings.count(),
            'as_advocate': HearingSerializer(as_advocate, many=True).data,
            'as_client': HearingSerializer(as_client, many=True).data,
        })
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change the status of a hearing"""
        hearing = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = ['scheduled', 'completed', 'postponed', 'cancelled']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Valid options: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hearing.status = new_status
        hearing.save()
        return Response({
            'message': f'Hearing status changed to {new_status}',
            'hearing': HearingSerializer(hearing).data
        })
    

class HearingUpdateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing hearing updates.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = HearingUpdateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['hearing', 'update_type', 'is_important']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'is_important']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateHearingUpdateSerializer
        return HearingUpdateSerializer

    def get_queryset(self):
        """
        Return updates for hearings the authenticated user is involved in
        """
        user = self.request.user

        # Safety check (extra defensive)
        if not user.is_authenticated:
            return HearingUpdate.objects.none()

        return HearingUpdate.objects.filter(
            Q(hearing__advocate=user) |
            Q(hearing__client=user)
        ).distinct()

    def perform_create(self, serializer):
        """
        Automatically set updated_by field
        """
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required")

        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def hearing_updates(self, request):
        hearing_id = request.query_params.get('hearing_id')
        if not hearing_id:
            return Response(
                {'error': 'hearing_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        hearing = get_object_or_404(Hearing, id=hearing_id)

        # Authorization check
        if request.user not in [hearing.advocate, hearing.client]:
            raise PermissionDenied("You are not allowed to view this hearing")

        updates = hearing.updates.all()
        serializer = HearingUpdateSerializer(updates, many=True)

        return Response({
            'hearing': HearingSerializer(hearing).data,
            'updates': serializer.data,
            'count': len(serializer.data)
        })

    @action(detail=False, methods=['get'])
    def my_updates(self, request):
        updates = HearingUpdate.objects.filter(updated_by=request.user)
        serializer = HearingUpdateSerializer(updates, many=True)
        return Response({
            'count': len(serializer.data),
            'updates': serializer.data
        })

    @action(detail=True, methods=['post'])
    def mark_as_important(self, request, pk=None):
        update = self.get_object()
        update.is_important = True
        update.save()

        return Response({
            'message': 'Update marked as important',
            'update': HearingUpdateSerializer(update).data
        })

    @action(detail=True, methods=['post'])
    def visibility(self, request, pk=None):
        update = self.get_object()

        update.visible_to_advocate = request.data.get(
            'visible_to_advocate', update.visible_to_advocate
        )
        update.visible_to_client = request.data.get(
            'visible_to_client', update.visible_to_client
        )
        update.save()

        return Response({
            'message': 'Visibility updated',
            'update': HearingUpdateSerializer(update).data
        })


class HearingStatsView(viewsets.ViewSet):
    """
    View for getting hearing statistics and analytics.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get hearing statistics for the current user"""
        user = request.user
        
        user_hearings = Hearing.objects.filter(
            Q(advocate=user) | Q(client=user)
        ).distinct()
        
        stats = {
            'total_hearings': user_hearings.count(),
            'scheduled': user_hearings.filter(status='scheduled').count(),
            'completed': user_hearings.filter(status='completed').count(),
            'postponed': user_hearings.filter(status='postponed').count(),
            'cancelled': user_hearings.filter(status='cancelled').count(),
            'total_updates': HearingUpdate.objects.filter(
                hearing__in=user_hearings
            ).count(),
            'important_updates': HearingUpdate.objects.filter(
                hearing__in=user_hearings,
                is_important=True
            ).count(),
        }
        
        return Response(stats)
