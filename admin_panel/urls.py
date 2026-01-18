# from django.urls import path
# from django.contrib.auth import views as auth_views
# from . import views

# urlpatterns = [
#     # Dashboard
  
    
#     # Quick Actions (redirect to Django admin)
#     path('create/event/', views.create_event, name='quick_create_event'),
#     path('create/movie/', views.create_movie, name='quick_create_movie'),
#     path('create/concert/', views.create_concert, name='quick_create_concert'),
    
#     # Reports
#     path('reports/events/', views.event_report, name='event_report'),

#     path('event-bookings/', views.admin_event_bookings, name='admin_event_bookings'),
#     path('event-bookings/<int:booking_id>/', views.admin_event_booking_detail, name='admin_event_booking_detail'),
#     path('events/', views.admin_events_list, name='admin_events_list'),
#     path('events/create/', views.create_event, name='admin_create_event'),
#     path('events/<int:event_id>/', views.admin_event_detail, name='admin_event_detail'),
#     path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
#     path('events/reports/', views.event_report, name='event_report'),
#     # path('reports/bookings/', views.booking_report, name='booking_report'),
#     # path('reports/revenue/', views.revenue_report, name='revenue_report'),
# ]

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    # Dashboard and Auth
    # path('', views.dashboard, name='admin_dashboard'),
    # path('login/', views.AdminLoginView.as_view(), name='admin_login'),
    # path('logout/', views.admin_logout, name='admin_logout'),

    path('', views.dashboard, name='admin_dashboard'),
    
    # Authentication
    path('admin-panel/login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    
    # Event Management
    path('event-bookings/', views.admin_event_bookings, name='admin_event_bookings'),
    path('event-bookings/<int:booking_id>/', views.admin_event_booking_detail, name='admin_event_booking_detail'),
    path('events/', views.admin_events_list, name='admin_events_list'),
    path('events/create/', views.create_event, name='admin_create_event'),
    path('events/<int:event_id>/', views.admin_event_detail, name='admin_event_detail'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/reports/', views.event_report, name='event_report'),

    path('event/book/', views.event_book, name='event_book'),
    path('event/book/add/', views.event_book_add, name='event_book_add'),
    path('event/bookings/', views.event_bookings_list, name='event_bookings_list'),
    path('event/booking/<str:booking_id>/', views.event_booking_detail, name='event_booking_detail'),
    path('event/booking/<str:booking_id>/cancel/', views.event_booking_cancel, name='event_booking_cancel'),
    
    # Other views
    path('movies/create/', views.create_movie, name='create_movie'),
    path('concerts/create/', views.create_concert, name='create_concert'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)