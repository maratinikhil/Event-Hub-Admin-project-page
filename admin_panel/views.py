from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Sum, Q, Avg
from django.utils.dateparse import parse_duration  
from .models import Event, BookingsEvent, Movie, User, MovieScreen, TheaterSeat, TicketBooking, ComedyShow, BookingComedyShow
from .forms import EventForm, MovieForm
import uuid
import string



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
    return render(request, 'admin_panel/events/event_book_list.html', context)

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
    return render(request, 'admin_panel/events/event_booking_detail.html', context)


# In views.py

@login_required(login_url='/admin-panel/login/')
def admin_event_booking_edit(request, booking_id):
    """View to edit a specific booking"""
    booking = get_object_or_404(BookingsEvent, id=booking_id)
    
    if request.method == 'POST':
        try:
            # Update basic fields
            booking.customer_name = request.POST.get('customer_name')
            booking.customer_email = request.POST.get('customer_email')
            booking.customer_phone = request.POST.get('customer_phone')
            booking.special_request = request.POST.get('special_request')
            booking.status = request.POST.get('status')
            
            # Handle Checkbox for Payment Status
            booking.payment_status = request.POST.get('payment_status') == 'on'
            
            # Handle Ticket Update & Price Recalculation
            new_tickets = int(request.POST.get('number_of_tickets'))
            if new_tickets != booking.number_of_tickets:
                booking.number_of_tickets = new_tickets
                # Recalculate total amount based on event price
                booking.total_amount = booking.event.ticket_price * new_tickets
            
            booking.save()
            messages.success(request, f'Booking #{booking.booking_id} updated successfully!')
            return redirect('admin_event_bookings')
            
        except ValueError:
            messages.error(request, 'Invalid input for tickets.')
        except Exception as e:
            messages.error(request, f'Error updating booking: {str(e)}')
            
    context = {
        'booking': booking,
        'page_title': f'Edit Booking #{booking.booking_id}',
    }
    return render(request, 'admin_panel/events/event_book_edit.html', context)


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
    try:
        event = Event.objects.annotate(
            booking_count=Count('bookingsevent')
        ).get(id=event_id)
    except Event.DoesNotExist:
        messages.error(request, 'Event not found!')
        return redirect('admin_events_list')
    
    # Get bookings for this event
    bookings = BookingsEvent.objects.filter(event=event).select_related('user').order_by('-booking_date')
    
    # Calculate stats
    total_bookings = bookings.count()
    total_revenue = bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Calculate booked seats by summing up all tickets from confirmed bookings
    # Only count confirmed bookings (not pending or cancelled)
    confirmed_bookings = bookings.filter(status='confirmed')
    booked_seats = confirmed_bookings.aggregate(total_tickets=Sum('number_of_tickets'))['total_tickets'] or 0
    
    # Calculate available seats
    if event.total_seats is not None:
        available_seats = max(0, event.total_seats - booked_seats)
        
        # Calculate booking percentage
        if event.total_seats > 0:
            booking_percentage = (booked_seats / event.total_seats) * 100
        else:
            booking_percentage = 0
    else:
        available_seats = event.available_seats or 0
        booking_percentage = 0
    
    # Check if event is sold out
    is_sold_out = available_seats <= 0
    
    context = {
        'event': event,
        'bookings': bookings,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'available_seats': available_seats,
        'booked_seats': booked_seats,  # Add this to context
        'booking_percentage': booking_percentage,  # Add this to context
        'is_sold_out': is_sold_out,  # Add this to context
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
        'event': None, 
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



def generate_booking_id():
    """Generate a unique booking ID matching the model's format"""
    while True:
        booking_id = f"EVT{uuid.uuid4().hex[:8].upper()}"
        if not BookingsEvent.objects.filter(booking_id=booking_id).exists():
            return booking_id



@login_required
def event_book(request):
    events = Event.objects.filter(
        date__gte=timezone.now().date()  
    ).order_by('date', 'time')
    context = {
        'events': events,
        'current_date': timezone.now(),
    }
    return render(request, 'admin_panel/events/event_book.html', context)


@login_required(login_url='/admin-panel/login/')
def delete_event(request, event_id):
    """Delete an event"""
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('admin_events_list')
    return redirect('admin_events_list')


@login_required(login_url='/admin-panel/login/')
def admin_event_detail(request, event_id):
    try:
        # Get event with booking count annotation
        event = Event.objects.annotate(
            booking_count=Count('bookingsevent')
        ).get(id=event_id)
    except Event.DoesNotExist:
        messages.error(request, 'Event not found!')
        return redirect('admin_events_list')
    
    # Get all bookings for this specific event
    bookings = BookingsEvent.objects.filter(event=event).select_related('user').order_by('-booking_date')
    
    # --- STATISTICS CALCULATION ---
    total_bookings = bookings.count()
    
    # Calculate Total Revenue (handle None if no bookings)
    total_revenue = bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Calculate Booked Seats (only confirmed bookings count towards occupancy)
    confirmed_bookings = bookings.filter(status='confirmed')
    booked_seats = confirmed_bookings.aggregate(total_tickets=Sum('number_of_tickets'))['total_tickets'] or 0
    
    # Calculate Available Seats & Percentage
    if event.total_seats and event.total_seats > 0:
        available_seats = max(0, event.total_seats - booked_seats)
        booking_percentage = (booked_seats / event.total_seats) * 100
    else:
        # Fallback if total_seats is not set or 0
        available_seats = event.available_seats or 0
        booking_percentage = 0
        if available_seats == 0 and booked_seats > 0:
            booking_percentage = 100 # Assume full if no total set but seats sold

    is_sold_out = available_seats <= 0
    
    context = {
        'event': event,
        'bookings': bookings,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'available_seats': available_seats,
        'booked_seats': booked_seats,
        'booking_percentage': round(booking_percentage, 1),
        'is_sold_out': is_sold_out,
        'today': date.today(),
        'page_title': f'Event: {event.name}',
    }
    return render(request, 'admin_panel/events/event_detail.html', context)


@login_required
def event_book_add(request):
    """Handle the event booking form submission"""
    if request.method == 'POST':
        try:
            # Get form data
            event_id = request.POST.get('event')
            number_of_tickets = int(request.POST.get('number_of_tickets', 1))
            status = request.POST.get('status')
            payment_status = request.POST.get('payment_status') == 'on'
            customer_name = request.POST.get('customer_name')
            customer_email = request.POST.get('customer_email')
            customer_phone = request.POST.get('customer_phone', '')
            special_request = request.POST.get('special_request', '')
            
            # Validate required fields
            if not event_id or not status or not customer_name or not customer_email:
                messages.error(request, 'Please fill all required fields.')
                return redirect('event_book')
            
            # Get the event
            event = get_object_or_404(Event, id=event_id)
            
            # Check if enough seats are available
            if event.available_seats < number_of_tickets:
                messages.error(request, f'Only {event.available_seats} seats available for this event.')
                return redirect('event_book')
            
            # Calculate total amount
            total_amount = event.ticket_price * number_of_tickets
            
            # Generate unique booking ID
            booking_id = generate_booking_id()
            
            # Create booking WITHOUT user assignment for now
            booking = BookingsEvent.objects.create(
                event=event,
                # user=None,  # Leave it as None for now
                number_of_tickets=number_of_tickets,
                total_amount=total_amount,
                status=status,
                booking_id=booking_id,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                special_request=special_request,
                payment_status=payment_status
            )
            
            messages.success(request, f'Booking {booking.booking_id} created successfully!')
            
            # Handle different save actions
            if 'save_and_add' in request.POST:
                return redirect('event_book')
            elif 'save_and_continue' in request.POST:
                return redirect('event_book')
            else:
                return redirect('event_bookings_list')
                
        except Event.DoesNotExist:
            messages.error(request, 'Selected event does not exist.')
            return redirect('event_book')
        except ValueError as e:
            messages.error(request, f'Invalid input: {str(e)}')
            return redirect('event_book')
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('event_book')
    
    return redirect('event_book')
@login_required
def event_bookings_list(request):
    """Display list of all event bookings"""
    bookings = BookingsEvent.objects.select_related('event', 'user').all()
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Filter by payment status if provided
    payment_filter = request.GET.get('payment_status')
    if payment_filter == 'paid':
        bookings = bookings.filter(payment_status=True)
    elif payment_filter == 'unpaid':
        bookings = bookings.filter(payment_status=False)
    
    # Search by booking ID or customer name
    search_query = request.GET.get('search')
    if search_query:
        bookings = bookings.filter(
            models.Q(booking_id__icontains=search_query) |
            models.Q(customer_name__icontains=search_query) |
            models.Q(customer_email__icontains=search_query)
        )
    
    context = {
        'bookings': bookings,
        'status_choices': BookingsEvent.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/events/event_book_list.html', context)

@login_required
def event_booking_detail(request, booking_id):
    """Display details of a specific booking"""
    booking = get_object_or_404(BookingsEvent, booking_id=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'event_booking_detail.html', context)

@login_required
def event_booking_cancel(request, booking_id):
    """Cancel a booking"""
    if request.method == 'POST':
        booking = get_object_or_404(BookingsEvent, booking_id=booking_id)
        
        if booking.status == 'cancelled':
            messages.warning(request, 'Booking is already cancelled.')
        else:
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, f'Booking {booking.booking_id} has been cancelled.')
        
        return redirect('event_bookings_list')
    
    return redirect('event_bookings_list')


# Movie

def admin_movie_screen(request):
    # Fetch data for the list and the form dropdown
    screens = MovieScreen.objects.select_related('movie').all().order_by('-id')
    movies = Movie.objects.all()

    if request.method == "POST":
        try:
            # 1. Get Form Data
            movie_id = request.POST.get('movie')
            screen_name = request.POST.get('screen_name')
            total_rows = int(request.POST.get('total_rows'))
            seats_per_row = int(request.POST.get('seats_per_row'))
            
            # Pricing Multipliers
            prem_price = request.POST.get('premium_price')
            exec_price = request.POST.get('executive_price')
            norm_price = request.POST.get('normal_price')
            
            # Row Boundaries
            prem_end = int(request.POST.get('premium_rows_end'))
            exec_end = int(request.POST.get('executive_rows_end'))

            # 2. Create the Movie Screen
            movie_instance = get_object_or_404(Movie, id=movie_id)
            
            new_screen = MovieScreen.objects.create(
                movie=movie_instance,
                screen_name=screen_name,
                total_rows=total_rows,
                seats_per_row=seats_per_row,
                premium_price_multiplier=prem_price,
                executive_price_multiplier=exec_price,
                normal_price_multiplier=norm_price,
                premium_rows_end=prem_end,
                executive_rows_end=exec_end
            )

            # 3. AUTOMATICALLY GENERATE SEATS
            # Logic: Row 1 = A, Row 2 = B, etc.
            alphabet = list(string.ascii_uppercase) # ['A', 'B', 'C'...]
            seats_to_create = []

            for row_num in range(1, total_rows + 1):
                # Get Row Letter (handle AA, AB if rows > 26 if needed, simple version here)
                row_char = alphabet[row_num - 1] if row_num <= 26 else f"Z{row_num}"
                
                # Determine Type and Price based on Row Index
                if row_num <= prem_end:
                    s_type = 'Premium'
                    s_price = prem_price
                elif row_num <= exec_end:
                    s_type = 'Executive'
                    s_price = exec_price
                else:
                    s_type = 'Normal'
                    s_price = norm_price

                # Create Seat Objects for this Row
                for seat_num in range(1, seats_per_row + 1):
                    seats_to_create.append(
                        TheaterSeat(
                            screen=new_screen,
                            row=row_char,
                            number=seat_num,
                            seat_type=s_type,
                            price=s_price,
                            status="Available"
                        )
                    )
            
            # Bulk create for performance
            TheaterSeat.objects.bulk_create(seats_to_create)

            messages.success(request, f"Screen '{screen_name}' created with {len(seats_to_create)} seats generated!")
            return redirect('admin_movie_screen')

        except Exception as e:
            messages.error(request, f"Error creating screen: {str(e)}")

    context = {
        'screens': screens,
        'movies': movies
    }
    return render(request, 'admin_panel/movies/movie_screen.html', context)


def movie_catalog(request):
    # Fetch all movies, ordered by newest first (reverse ID)
    movies = Movie.objects.all().order_by('-id')
    
    context = {
        'movies': movies
    }
    return render(request, 'admin_panel/movies/movies.html', context)


def admin_movie_list(request):
    # Fetch all movies, newest first
    movies = Movie.objects.all().order_by('-id')

    if request.method == "POST":
        try:
            # 1. Extract Data
            title = request.POST.get('title')
            description = request.POST.get('description')
            location = request.POST.get('location')
            language = request.POST.get('language')
            director = request.POST.get('director')
            cast = request.POST.get('cast')
            genre = request.POST.get('genre')
            popularity = request.POST.get('popularity')
            
            # Numeric/Date conversions
            price = request.POST.get('ticket_price')
            seats = request.POST.get('available_seats')
            rating = request.POST.get('rating')
            date = request.POST.get('date')
            time = request.POST.get('time')
            duration = request.POST.get('duration') # Expecting HH:MM:SS format
            
            # 2. Handle Image Upload
            image = request.FILES.get('image')

            # 3. Create Movie Object
            Movie.objects.create(
                title=title,
                description=description,
                location=location,
                date=date,
                time=time,
                language=language,
                duration=duration,
                director=director,
                cast=cast,
                genre=genre,
                ticket_price=price,
                available_seats=seats,
                image=image,
                rating=rating,
                popularity=popularity
            )

            messages.success(request, f"Movie '{title}' added successfully!")
            return redirect('admin_movie_list')

        except Exception as e:
            messages.error(request, f"Error adding movie: {str(e)}")

    return render(request, 'admin_panel/movies/movies.html', {'movies': movies})


def movie_bookings_list(request):
    # Fetch all bookings with related data to avoid N+1 queries
    bookings = TicketBooking.objects.select_related('user', 'movie', 'screen').all().order_by('-booked_at')

    # Calculate some summary stats for the top of the page
    total_revenue = bookings.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_bookings = bookings.count()
    successful_bookings = bookings.filter(payment_status=True).count()

    context = {
        'bookings': bookings,
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'successful_bookings': successful_bookings
    }
    
    return render(request, 'admin_panel/movies/movie_bookings.html', context)



def add_movie(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            genre = request.POST.get('genre')
            language = request.POST.get('language')
            description = request.POST.get('description')
            director = request.POST.get('director')
            cast = request.POST.get('cast')
            release_date = request.POST.get('date')
            show_time = request.POST.get('time')
            location = request.POST.get('location')
            ticket_price = request.POST.get('ticket_price')
            available_seats = request.POST.get('available_seats')
            rating = request.POST.get('rating')
            popularity = request.POST.get('popularity')
            image = request.FILES.get('image')

            # 2. Get the duration string (e.g., "02:30:00")
            duration_str = request.POST.get('duration')
            
            # 3. Convert string to a timedelta object
            duration_val = parse_duration(duration_str) 
            if duration_val is None:
                raise ValueError("Invalid duration format. Use HH:MM:SS")

            # Create Movie
            movie = Movie(
                title=title,
                genre=genre,
                language=language,
                description=description,
                director=director,
                cast=cast,
                date=release_date,
                time=show_time,
                duration=duration_val,  
                location=location,
                ticket_price=ticket_price,
                available_seats=available_seats,
                rating=rating,
                popularity=popularity,
                image=image
            )
            movie.save()

            messages.success(request, f"Movie '{title}' added successfully!")
            return redirect('movies')

        except Exception as e:
            print(f"Error: {e}") 
            messages.error(request, f"Error adding movie: {e}")
            return redirect('add_movie')

    return render(request, 'admin_panel/movies/add_movies.html')


@login_required
def book_movie(request):
    movies = Movie.objects.all().order_by('date', 'time')
    
    context = {
        'movies': movies
    }
    return render(request, 'admin_panel/movies/book_movie.html', context)

# 2. The Seat Selection Page (When user clicks 'Book Ticket')
@login_required
def book_seat_selection(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    screen = MovieScreen.objects.filter(movie=movie).first()
    
    seats = []
    if screen:
        seats = TheaterSeat.objects.filter(screen=screen).order_by('row', 'number')

    context = {
        'movie': movie,
        'screen': screen,
        'seats': seats,
    }
    # You will need to create this template next
    return render(request, 'admin_panel/movies/booking_seat_layout.html', context)


def delete_movie_screen(request, screen_id):
    # Get the specific screen or show 404 if not found
    screen = get_object_or_404(MovieScreen, id=screen_id)
    
    if request.method == 'POST':
        screen_name = screen.screen_name
        screen.delete()
        messages.success(request, f"Screen '{screen_name}' deleted successfully!")
        return redirect('movie_screen') # Redirect back to the main list
        
    # Optional: If someone visits the URL directly without POST
    return redirect('movie_screen')

def edit_movie_screen(request, screen_id):
    screen = get_object_or_404(MovieScreen, id=screen_id)
    movies = Movie.objects.all() # We need the list of movies for the dropdown

    if request.method == 'POST':
        try:
            # Update fields
            movie_id = request.POST.get('movie')
            screen.movie = get_object_or_404(Movie, id=movie_id)
            
            screen.screen_name = request.POST.get('screen_name')
            screen.total_rows = int(request.POST.get('total_rows'))
            screen.seats_per_row = int(request.POST.get('seats_per_row'))
            
            # Pricing Update
            screen.premium_price_multiplier = request.POST.get('premium_price')
            screen.premium_rows_end = int(request.POST.get('premium_rows_end'))
            
            screen.executive_price_multiplier = request.POST.get('executive_price')
            screen.executive_rows_end = int(request.POST.get('executive_rows_end'))
            
            screen.normal_price_multiplier = request.POST.get('normal_price')
            
            screen.save()
            
            messages.success(request, f"Screen '{screen.screen_name}' updated successfully!")
            return redirect('movie_screen')
            
        except Exception as e:
            messages.error(request, f"Error updating screen: {e}")

    # Render the edit form with existing data
    context = {
        'screen': screen,
        'movies': movies
    }
    return render(request, 'admin_panel/movies/edit_movie_screen.html', context)


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def movies_booking_view(request, booking_id):
    booking = get_object_or_404(TicketBooking, id=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'admin_panel/movies/movies_booking_view.html', context)

@user_passes_test(is_admin)
def movies_booking_edit(request, booking_id):
    booking = get_object_or_404(TicketBooking, id=booking_id)
    
    if request.method == 'POST':
        booking.status = request.POST.get('status')
        booking.payment_status = request.POST.get('payment_status') == 'on'
        booking.save()
        
        messages.success(request, f"Booking #{booking.id} updated successfully.")
        return redirect('movies_bookings') # Redirect back to the list
    
    context = {
        'booking': booking,
    }
    return render(request, 'admin_panel/movies/movies_booking_edit.html', context)

@user_passes_test(is_admin)
def movies_booking_delete(request, booking_id):
    booking = get_object_or_404(TicketBooking, id=booking_id)
    
    if request.method == 'POST':
        booking.delete()
        messages.success(request, f"Booking #{booking_id} has been deleted permanently.")
        return redirect('movies_bookings') # Redirect back to the list
    
    messages.warning(request, "Invalid delete attempt.")
    return redirect('movies_bookings')


# comedy shows

def comedy_shows_list(request):
    shows = ComedyShow.objects.all().order_by('-date')
    context = {
        'page_title': 'Comedy Shows',
        'shows': shows
    }
    return render(request, 'admin_panel/comedys/comedy_shows_list.html', context)


def comedy_bookings(request):
    bookings = BookingComedyShow.objects.select_related('user', 'comedy_show').all().order_by('-booking_date')
    context = {
        'page_title': 'Comedy Bookings',
        'bookings': bookings
    }
    return render(request, 'admin_panel/comedys/comedy_bookings.html', context)

def book_comedy_show(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            show_id = request.POST.get('show_id')
            tickets = int(request.POST.get('tickets'))
            
            user = User.objects.get(id=user_id)
            show = ComedyShow.objects.get(id=show_id)
            
            # 1. Check Availability
            if show.available_seats < tickets:
                messages.error(request, f"Not enough seats! Only {show.available_seats} left.")
                return redirect('book_comedy_show')

            # 2. Calculate Totals
            total_price = show.ticket_price * tickets
            
            # 3. Create Booking ID
            booking_id = f"COM-{uuid.uuid4().hex[:8].upper()}"

            # 4. Create Record
            booking = BookingComedyShow(
                booking_id=booking_id,
                user=user,
                comedy_show=show,
                number_of_tickets=tickets,
                booking_date=timezone.now(),
                total_price=total_price,
                payment_status=True # Assuming admin booking is paid/manual
            )
            booking.save()

            # 5. Update Seats
            show.available_seats -= tickets
            show.save()

            messages.success(request, f"Booking {booking_id} created successfully!")
            return redirect('comedy_bookings')

        except Exception as e:
            messages.error(request, f"Error creating booking: {str(e)}")
            return redirect('book_comedy_show')

    # GET Request: Load forms
    users = User.objects.filter(is_superuser=False) # Usually bookings are for normal users
    shows = ComedyShow.objects.filter(available_seats__gt=0, date__gte=timezone.now())
    
    context = {
        'page_title': 'Book Comedy Show',
        'users': users,
        'shows': shows
    }
    return render(request, 'admin_panel/book_comedy_show.html', context)


def add_comedy_show(request):
    if request.method == 'POST':
        try:
            # Extract fields from the form
            title = request.POST.get('title')
            description = request.POST.get('description')
            location = request.POST.get('location')
            date = request.POST.get('date')
            time = request.POST.get('time')
            comedian_name = request.POST.get('comedian_name')
            age_limit = request.POST.get('age_limit')
            total_seats = int(request.POST.get('total_seats'))
            ticket_price = request.POST.get('ticket_price')
            
            # Additional fields
            comedy_type = request.POST.get('comedy_type')
            rating = request.POST.get('rating')
            duration = request.POST.get('duration')
            popularity = request.POST.get('popularity')
            experience = request.POST.get('experience')

            # Handle Image Upload
            image = request.FILES.get('image')

            # Create the ComedyShow object
            # Note: For a new show, we typically set available_seats = total_seats initially
            new_show = ComedyShow(
                title=title,
                description=description,
                location=location,
                date=date,
                time=time,
                comedian_name=comedian_name,
                age_limit=age_limit,
                total_seats=total_seats,
                ticket_price=ticket_price,
                available_seats=total_seats,  # Initialize availability
                image=image,
                comedy_type=comedy_type,
                rating=rating,
                duration=duration,
                popularity=popularity,
                experience=experience
            )
            new_show.save()

            messages.success(request, f"Comedy Show '{title}' created successfully!")
            return redirect('comedy_shows_list')

        except Exception as e:
            messages.error(request, f"Error creating show: {str(e)}")
            # In a real app, you might want to return the form with entered data here
            return redirect('add_comedy_show')

    # GET Request: Display the empty form
    context = {
        'page_title': 'Add Comedy Show'
    }
    return render(request, 'admin_panel/comedys/add_comedy_show.html', context)



def comedy_show_bookings_view(request, booking_id):
    booking = get_object_or_404(BookingComedyShow, id=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'admin_panel/comedys/comedy_show_bookings_view.html', context)


def comedy_show_bookings_edit(request, booking_id):
    booking = get_object_or_404(BookingComedyShow, id=booking_id)
    if request.method == 'POST':
        booking.number_of_tickets = request.POST.get('number_of_tickets')
        payment_status = request.POST.get('payment_status')
        if payment_status == 'Paid':
            booking.payment_status = True
        else:
            booking.payment_status = False
        booking.save()
        messages.success(request, 'Booking updated successfully!')
        return redirect('comedy_show_bookings') 

    context = {
        'booking': booking,
    }
    return render(request, 'admin_panel/comedys/comedy_show_bookings_edit.html', context)


def delete_comedy_show(request, show_id):
    # Fetch the show or return 404
    show = get_object_or_404(ComedyShow, id=show_id)

    if request.method == 'POST':
        # logic to delete the show
        show.delete()
        messages.success(request, 'Comedy show deleted successfully!')
        return redirect('comedy_shows') # Replace with your actual list view name

    # If GET request, render the confirmation page
    context = {
        'show': show
    }
    return render(request, 'admin_panel/comedy_show_delete_confirm.html', context)


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