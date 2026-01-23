from django.urls import path,include
from . import views

urlpatterns = [
    # Hearing endpoints
    path('hearings/', views.HearingViewSet.as_view({'get': 'list', 'post': 'create'}), name='hearing-list'),
    path('hearings/<int:pk>/', views.HearingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='hearing-detail'),
    path('hearings/<int:pk>/updates/', views.HearingViewSet.as_view({'get': 'updates'}), name='hearing-updates'),
    path('hearings/<int:pk>/change-status/', views.HearingViewSet.as_view({'post': 'change_status'}), name='change-hearing-status'),
    path('hearings/my-hearings/', views.HearingViewSet.as_view({'get': 'my_hearings'}), name='my-hearings'),
    
    # Hearing Update endpoints
    path('updates/', views.HearingUpdateViewSet.as_view({'get': 'list', 'post': 'create'}), name='update-list'),
    path('updates/<int:pk>/', views.HearingUpdateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='update-detail'),
    path('updates/hearing-updates/', views.HearingUpdateViewSet.as_view({'get': 'hearing_updates'}), name='hearing-updates-list'),
    path('updates/my-updates/', views.HearingUpdateViewSet.as_view({'get': 'my_updates'}), name='my-updates'),
    path('updates/<int:pk>/mark-important/', views.HearingUpdateViewSet.as_view({'post': 'mark_as_important'}), name='mark-important'),
    path('updates/<int:pk>/visibility/', views.HearingUpdateViewSet.as_view({'post': 'visibility'}), name='update-visibility'),
    
    # Stats endpoint
    path('stats/', views.HearingStatsView.as_view({'get': 'stats'}), name='stats'),
]