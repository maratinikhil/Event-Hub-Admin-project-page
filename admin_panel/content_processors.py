from datetime import date
from django.db.models import Sum, Count
from .models import (
    Event, BookingsEvent, Movie, ComedyShow, 
    LiveConcert, AmusementPark, User
)

def dashboard_stats(request):
    """Add dashboard statistics to all admin templates"""
    stats = {}
    
    if request.user.is_authenticated:
        try:
            # Events
            stats['total_events'] = Event.objects.count()
            stats['active_events'] = Event.objects.filter(date__gte=date.today()).count()
            stats['total_event_bookings'] = BookingsEvent.objects.count()
            stats['event_revenue'] = BookingsEvent.objects.filter(
                payment_status=True
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            # Movies
            stats['total_movies'] = Movie.objects.count()
            stats['movies_today'] = Movie.objects.filter(date=date.today()).count()
            
            # Comedy Shows
            stats['total_comedy_shows'] = ComedyShow.objects.count()
            
            # Concerts
            stats['total_concerts'] = LiveConcert.objects.count()
            
            # Parks
            stats['total_parks'] = AmusementPark.objects.count()
            
            # Users
            stats['total_users'] = User.objects.count()
            stats['new_users_today'] = User.objects.filter(
                date_joined__date=date.today()
            ).count() if hasattr(User, 'date_joined') else 0
            
            # Recent bookings
            stats['recent_bookings'] = BookingsEvent.objects.order_by('-booking_date')[:5]
            
            # Upcoming events
            stats['upcoming_events'] = Event.objects.filter(
                date__gte=date.today()
            ).order_by('date')[:5]
            
        except:
            # If tables don't exist yet, return empty stats
            pass
    
    return {'dashboard_stats': stats}