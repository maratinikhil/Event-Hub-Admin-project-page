from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Sum, Q, Avg
from .models import Event, BookingsEvent, Movie, User
from .forms import EventForm, MovieForm

# Custom login view to add messages
class AdminLoginView(LoginView):
    template_name = 'admin_panel/login.html'
    redirect_authenticated_user = True
    authentication_form = AuthenticationForm

    def get_success_url(self):
        return reverse_lazy('admin_dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Welcome back! You have successfully logged in.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)

# Custom logout view
def admin_logout(request):
    """Custom logout view to show logout confirmation"""
    if request.user.is_authenticated:
        messages.success(request, 'You have been successfully logged out.')
    logout(request)
    return render(request, 'admin_panel/logout.html')

# Dashboard view (with login required)
@login_required(login_url='/admin-panel/login/')
def dashboard(request):
    """Admin dashboard homepage"""
    # Get event stats
    total_events = Event.objects.count() if hasattr(Event, 'objects') else 0
    upcoming_events = Event.objects.filter(date__gte=timezone.now().date()).count() if hasattr(Event, 'objects') else 0
    
    context = {
        'page_title': 'Dashboard',
        'current_date': timezone.now().strftime('%A, %d %B %Y'),
        'dashboard_stats': {
            'total_events': total_events,
            'total_users': User.objects.count() if hasattr(User, 'objects') else 89,
            'upcoming_events': upcoming_events,
        },
        'events_count': total_events,
        'upcoming_count': upcoming_events,
    }
    return render(request, 'admin_panel/dashboard.html', context)

# ========= EVENT MANAGEMENT VIEWS =========

@login_required(login_url='/admin-panel/login/')
def admin_event_bookings(request):
    """Admin view for event bookings"""
    bookings = BookingsEvent.objects.select_related('event', 'user').order_by('-booking_date')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        bookings = bookings.filter(
            Q(event__name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(booking_id__icontains=search_query)
        )
    
    # Stats
    total_bookings = bookings.count()
    pending_bookings = bookings.filter(status='pending').count()
    confirmed_bookings = bookings.filter(status='confirmed').count()
    cancelled_bookings = bookings.filter(status='cancelled').count()
    
    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'status_filter': status_filter,
        'search_query': search_query,
        'page_title': 'Event Bookings',
    }
    return render(request, 'admin_panel/events/bookings_list.html', context)

@login_required(login_url='/admin-panel/login/')
def admin_event_booking_detail(request, booking_id):
    """Admin view for booking detail"""
    booking = get_object_or_404(BookingsEvent.objects.select_related('event', 'user'), id=booking_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in ['pending', 'confirmed', 'cancelled']:
            booking.status = new_status
            booking.save()
            messages.success(request, f'Booking status updated to {new_status}')
            return redirect('admin_event_booking_detail', booking_id=booking_id)
    
    context = {
        'booking': booking,
        'page_title': f'Booking #{booking.booking_id}',
    }
    return render(request, 'admin_panel/events/event_detail.html', context)

@login_required(login_url='/admin-panel/login/')
def admin_events_list(request):
    """Custom admin view for events list"""
    today = date.today()
    events = Event.objects.annotate(
        booking_count=Count('bookingsevent')
    ).order_by('-date')
    
    # Filtering
    event_type = request.GET.get('type', '')
    if event_type:
        events = events.filter(event_type=event_type)
    
    status_filter = request.GET.get('status', '')
    if status_filter == 'upcoming':
        events = events.filter(date__gte=today)
    elif status_filter == 'past':
        events = events.filter(date__lt=today)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Stats
    total_events = events.count()
    upcoming_events = events.filter(date__gte=today).count()
    past_events = events.filter(date__lt=today).count()
    
    context = {
        'events': events,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'today': today,
        'event_type': event_type,
        'status_filter': status_filter,
        'search_query': search_query,
        'page_title': 'Manage Events',
    }
    return render(request, 'admin_panel/events/events.html', context)

@login_required(login_url='/admin-panel/login/')
def admin_event_detail(request, event_id):
    """Custom admin view for event details"""
    event = get_object_or_404(Event.objects.annotate(
        booking_count=Count('bookingsevent')
    ), id=event_id)
    
    # Get bookings for this event
    bookings = BookingsEvent.objects.filter(event=event).select_related('user').order_by('-booking_date')
    
    # Calculate stats
    total_bookings = bookings.count()
    total_revenue = bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    available_seats = event.capacity - total_bookings if event.capacity else 0
    
    context = {
        'event': event,
        'bookings': bookings,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'available_seats': available_seats,
        'today': date.today(),
        'page_title': f'Event: {event.name}',
    }
    return render(request, 'admin_panel/events/event_detail.html', context)



@login_required(login_url='/admin-panel/login/')
def create_event(request):
    """Create new event"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.name}" created successfully!')
            return redirect('admin_event_detail', event_id=event.id)
    else:
        form = EventForm()
    
    # Get stats for sidebar
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gte=date.today()).count()
    avg_price = Event.objects.aggregate(avg=Avg('ticket_price'))['avg'] or 0
    avg_seats = Event.objects.aggregate(avg=Avg('total_seats'))['avg'] or 0
    
    context = {
        'form': form,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'avg_price': avg_price,
        'avg_seats': avg_seats,
        'page_title': 'Create Event',
    }
    return render(request, 'admin_panel/events/create_event.html', context)

@login_required(login_url='/admin-panel/login/')
def edit_event(request, event_id):
    """Edit existing event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.name}" updated successfully!')
            return redirect('admin_event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'page_title': f'Edit Event: {event.name}',
    }
    return render(request, 'admin_panel/events/create_event.html', context)

# ========= OTHER VIEWS =========

@login_required(login_url='/admin-panel/login/')
def event_report(request):
    """Event analytics report"""
    today = date.today()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    events_data = {
        'total': Event.objects.count(),
        'this_week': Event.objects.filter(date__gte=last_week).count(),
        'this_month': Event.objects.filter(date__gte=last_month).count(),
        'upcoming': Event.objects.filter(date__gte=today).count(),
    }
    
    # Booking stats
    bookings_data = {
        'total': BookingsEvent.objects.count(),
        'this_week': BookingsEvent.objects.filter(booking_date__gte=last_week).count(),
        'this_month': BookingsEvent.objects.filter(booking_date__gte=last_month).count(),
        'revenue': BookingsEvent.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
    }
    
    return render(request, 'admin_panel/reports/events.html', {
        'events_data': events_data,
        'bookings_data': bookings_data,
        'page_title': 'Event Reports'
    })

@login_required(login_url='/admin-panel/login/')
def create_movie(request):
    """Quick movie creation"""
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Movie created successfully!')
            return redirect('admin_dashboard')
    else:
        form = MovieForm()
    return render(request, 'admin_panel/quick_create.html', {'form': form, 'type': 'Movie'})

@login_required(login_url='/admin-panel/login/')
def create_concert(request):
    """Quick concert creation"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.type = 'concert'
            event.save()
            messages.success(request, 'Concert created successfully!')
            return redirect('admin_dashboard')
    else:
        form = EventForm()
    return render(request, 'admin_panel/quick_create.html', {'form': form, 'type': 'Concert'})