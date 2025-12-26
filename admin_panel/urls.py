from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='admin_dashboard'),
    
    # Authentication
    path('admin-panel/login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    
    # Quick Actions (redirect to Django admin)
    path('create/event/', views.create_event, name='quick_create_event'),
    path('create/movie/', views.create_movie, name='quick_create_movie'),
    path('create/concert/', views.create_concert, name='quick_create_concert'),
    
    # Reports
    path('reports/events/', views.event_report, name='event_report'),
    # path('reports/bookings/', views.booking_report, name='booking_report'),
    # path('reports/revenue/', views.revenue_report, name='revenue_report'),
]