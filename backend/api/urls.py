"""
API URL Configuration
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Research endpoints
    path('research/submit/', views.ResearchSubmitView.as_view(), name='research-submit'),
    path('research/status/<uuid:task_id>/', views.ResearchStatusView.as_view(), name='research-status'),
    path('research/result/<uuid:task_id>/', views.ResearchResultView.as_view(), name='research-result'),
    path('research/list/', views.ResearchListView.as_view(), name='research-list'),
    path('research/stats/', views.ResearchStatsView.as_view(), name='research-stats'),
    path('research/cancel/<uuid:task_id>/', views.ResearchCancelView.as_view(), name='research-cancel'),
    
    # Error logging endpoint
    path('errors/log/', views.ErrorLogView.as_view(), name='error-log'),
    
    # Health check
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]
