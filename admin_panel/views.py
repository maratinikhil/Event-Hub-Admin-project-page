# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.utils import timezone
# from datetime import date, timedelta
# from .models import Event, BookingsEvent, Movie, User
# from .forms import EventForm, MovieForm  # We'll create forms

# # views.py - Update the dashboard view
# @login_required
# def dashboard(request):
#     """Admin dashboard homepage"""
#     context = {
#         'page_title': 'Dashboard',
#         'current_date': timezone.now().strftime('%A, %d %B %Y'),
#         # 'dashboard_stats': {
#         #     'total_events': 24,
#         #     'event_revenue': 125000,
#         #     'total_event_bookings': 156,
#         #     'total_users': 89,
#         #     'active_events': 8,
#         #     'new_users_today': 3,
#         # }
#     }
#     return render(request, 'admin_panel/dashboard.html', context)

# @login_required
# def create_event(request):
#     """Quick event creation"""
#     if request.method == 'POST':
#         form = EventForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Event created successfully!')
#             return redirect('admin_dashboard')
#     else:
#         form = EventForm()
#     return render(request, 'admin_panel/quick_create.html', {'form': form, 'type': 'Event'})

# # Add similar views for other quick actions

# @login_required
# def event_report(request):
#     """Event analytics report"""
#     today = date.today()
#     last_week = today - timedelta(days=7)
#     last_month = today - timedelta(days=30)
    
#     events_data = {
#         'total': Event.objects.count(),
#         'this_week': Event.objects.filter(date__gte=last_week).count(),
#         'this_month': Event.objects.filter(date__gte=last_month).count(),
#         'upcoming': Event.objects.filter(date__gte=today).count(),
#     }
    
#     return render(request, 'admin_panel/reports/events.html', {
#         'events_data': events_data,
#         'page_title': 'Event Reports'
#     })

# @login_required
# def create_movie(request):
#     """Quick movie creation"""
#     if request.method == 'POST':
#         form = MovieForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Movie created successfully!')
#             return redirect('admin_dashboard')
#     else:
#         form = MovieForm()
#     return render(request, 'admin_panel/quick_create.html', {'form': form, 'type': 'Movie'})

# @login_required
# def create_concert(request):
#     """Quick concert creation"""
#     # If you have a ConcertForm, use it. Otherwise, you might need to create one
#     if request.method == 'POST':
#         form = EventForm(request.POST, request.FILES)  # Or ConcertForm if you have it
#         if form.is_valid():
#             event = form.save(commit=False)
#             event.type = 'concert'  # Set event type if you have such field
#             event.save()
#             messages.success(request, 'Concert created successfully!')
#             return redirect('admin_dashboard')
#     else:
#         form = EventForm()  # Or ConcertForm if you have it
#     return render(request, 'admin_panel/quick_create.html', {'form': form, 'type': 'Concert'})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
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
    # Instead of redirecting, render the logout page
    return render(request, 'admin_panel/logout.html')

# Dashboard view (with login required)
@login_required(login_url='/admin-panel/login/')
def dashboard(request):
    """Admin dashboard homepage"""
    context = {
        'page_title': 'Dashboard',
        'current_date': timezone.now().strftime('%A, %d %B %Y'),
        'dashboard_stats': {
            'total_events': Event.objects.count() if hasattr(Event, 'objects') else 24,
            'total_users': User.objects.count() if hasattr(User, 'objects') else 89,
        }
    }
    return render(request, 'admin_panel/dashboard.html', context)

# Add login required decorator to all admin views
@login_required(login_url='/admin-panel/login/')
def create_event(request):
    """Quick event creation"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event created successfully!')
            return redirect('admin_dashboard')
    else:
        form = EventForm()
    return render(request, 'admin_panel/quick_create.html', {'form': form, 'type': 'Event'})

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
    
    return render(request, 'admin_panel/reports/events.html', {
        'events_data': events_data,
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