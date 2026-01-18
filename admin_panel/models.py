from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User

from django.apps import AppConfig

class AdminPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel'
    verbose_name = 'Admin Panel'

# =============================================
# ⭐ READ-ONLY MODELS (Keep managed=False)
# =============================================

class User(models.Model):
    firstname = models.CharField(max_length=50,null=True,blank=True)
    lastname = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10,unique=True)
    password = models.CharField(max_length=255)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_created_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        managed = False  
        db_table = 'eventapp_user'  
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class BookingsEvent(models.Model):
    STATUS_CHOICES = [
        ('confirmed','Confirmed'),
        ('pending','Pending'),
        ('cancelled','Cancelled'),
        ('completed','Completed'),
    ]

    event = models.ForeignKey('Event',on_delete=models.DO_NOTHING,db_constraint=False)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,blank=True,db_constraint=False)
    booking_date = models.DateTimeField()
    number_of_tickets = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES)
    booking_id = models.CharField(max_length=20,unique=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15,blank=True,null=True)
    special_request = models.TextField(blank=True,null=True)
    payment_status = models.BooleanField(default=False)


    class Meta:
        managed = False
        db_table = "eventapp_bookingsevent"  # ⚠️ Check if plural or singular
        ordering = ['-booking_date']
        verbose_name = "Event Booking"
        verbose_name_plural = "Event Bookings"

    def __str__(self):
        return f"{self.booking_id} - {self.customer_name}"


class TicketBooking(models.Model):
    user = models.ForeignKey(User ,on_delete=models.DO_NOTHING, db_constraint=False)
    movie = models.ForeignKey('Movie', on_delete=models.DO_NOTHING, db_constraint=False)
    screen = models.ForeignKey('MovieScreen', on_delete=models.DO_NOTHING, db_constraint=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("2.00"))
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("18.00"))
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))    
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    booked_at = models.DateTimeField()
    razorpay_order_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.BooleanField(default=False)

    class Meta:
        managed = False  
        db_table = 'eventapp_ticketbooking'  
        verbose_name = 'Ticket Booking'
        verbose_name_plural = 'Ticket Bookings'

    def __str__(self):
        return f"TicketBooking #{self.id}"


class BookingComedyShow(models.Model):
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING, db_constraint=False)
    comedy_show = models.ForeignKey('ComedyShow', on_delete=models.DO_NOTHING, db_constraint=False)
    number_of_tickets = models.PositiveIntegerField(default=1)
    booking_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.BooleanField(default=False)
    
    class Meta:
        managed = False  
        db_table = 'eventapp_bookingcomedyshow'  
        verbose_name = 'Booking Comedy Show'
        verbose_name_plural = 'Booking Comedy Shows'

    def __str__(self):
        return f"{self.booking_id} - {self.user.username} - {self.number_of_tickets} tickets"


class LiveConcertTicketBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="bookings")
    concert = models.ForeignKey('LiveConcert', on_delete=models.DO_NOTHING, related_name="bookings")
    quantity = models.PositiveIntegerField(default=1)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    booked_at = models.DateTimeField()
    payment_status = models.CharField(max_length=20)
    razorpay_order_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False  
        db_table = 'eventapp_liveconcertticketbooking'  
        verbose_name = 'Live Concert Ticket Booking'
        verbose_name_plural = 'Live Concert Ticket Bookings'

    def __str__(self):
        return f"{self.user.email} - Ticket for {self.concert.title}"


class AmusementBooking(models.Model):
    booking_id = models.CharField(max_length=12, editable=False)
    amusement_park = models.ForeignKey('AmusementPark',on_delete=models.DO_NOTHING,related_name='bookings')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    total_gst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    grand_total = models.DecimalField(max_digits=10,decimal_places=2,default=2)
    created_at = models.DateTimeField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer_name}"
    
    class Meta:
        managed = False  
        db_table = 'eventapp_amusementbooking'  
        verbose_name = 'Amusement Booking'
        verbose_name_plural = 'Amusement Bookings'


class AmusementBookingItem(models.Model):
    booking = models.ForeignKey(AmusementBooking, on_delete=models.DO_NOTHING, related_name='items', null=True, blank=True)
    other_booking = models.ForeignKey('OtherAmusementBooking', on_delete=models.DO_NOTHING, db_constraint=False)
    ticket_type = models.ForeignKey('AmusementTicket', on_delete=models.DO_NOTHING, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, editable=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    total_with_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
        
    class Meta:
        managed = False  
        db_table = 'eventapp_amusementbookingitem'  
        verbose_name = 'Amusement Booking Item' 
        verbose_name_plural = 'Amusement Booking Items'


class OtherAmusementBooking(models.Model):
    booking_id = models.CharField(max_length=12, unique=True, editable=False)
    amusement_park = models.ForeignKey('AmusementPark', on_delete=models.DO_NOTHING)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    quantity = models.PositiveIntegerField(default=1)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"OtherBooking {self.booking_id} - {self.customer_name}"

    class Meta:
        managed = False  
        db_table = 'eventapp_otheramusementbooking'  
        verbose_name = 'Other Amusement Booking'
        verbose_name_plural = 'Other Amusement Bookings'


# =============================================
# ⭐ WRITE-ABLE MODELS (Change to managed=True)
# =============================================

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField(default=0)
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2)
    # ⭐ CHANGED: CharField → ImageField (for uploads)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    
    class Meta:
        managed = True  # ⭐ CHANGED: Can create/update
        db_table = 'eventapp_event' 
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Simple save logic for admin uploads"""
        if self.pk is None:  # New event
            self.available_seats = self.total_seats
        super().save(*args, **kwargs)


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    language = models.CharField(max_length=50)
    duration = models.DurationField()
    director = models.CharField(max_length=100, blank=True, null=True)
    cast = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=100)
    ticket_price = models.DecimalField(max_digits=8,decimal_places=2)
    available_seats = models.PositiveIntegerField()
    # ⭐ CHANGED: CharField → ImageField (for uploads)
    image = models.ImageField(upload_to='movies/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    popularity = models.CharField(max_length=20, default='Hot')
    
    class Meta:
        managed = True  # ⭐ CHANGED: Can create/update
        db_table = 'eventapp_movie'  
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'

    def __str__(self):
        return f"{self.title}"


class MovieScreen(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)  # ⭐ CHANGED: CASCADE for proper relationships
    screen_name = models.CharField(max_length=100, default="Screen 1")
    total_rows = models.PositiveIntegerField(default=10)
    seats_per_row = models.PositiveIntegerField(default=12)
    premium_price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('750.00'))
    executive_price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('500.00'))
    normal_price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('350.00'))
    premium_rows_end = models.PositiveIntegerField(default=3)
    executive_rows_end = models.PositiveIntegerField(default=6)

    class Meta:
        managed = True  # ⭐ CHANGED: Can create/update
        db_table = 'eventapp_moviescreen' 
        verbose_name = 'Movie Screen'
        verbose_name_plural = 'Movie Screens'

    def __str__(self):
        return f"{self.screen_name} - {self.movie.title}"


class TheaterSeat(models.Model):
    screen = models.ForeignKey(MovieScreen, on_delete=models.CASCADE)  # ⭐ CHANGED: CASCADE
    row = models.CharField(max_length=2)
    number = models.PositiveIntegerField()  # ⭐ CHANGED: PositiveBigIntegerField → PositiveIntegerField
    seat_type = models.CharField(max_length=20, default='normal')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default="Available")
    
    class Meta:
        managed = True  # ⭐ CHANGED: Can create/update
        db_table = 'eventapp_theaterseat'  
        verbose_name = 'Theater Seat'
        verbose_name_plural = 'Theater Seats'

    def __str__(self):
        return f"{self.row}{self.number}"


class ComedyShow(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    comedian_name = models.CharField(max_length=100)
    age_limit = models.PositiveIntegerField(default=18)
    total_seats = models.PositiveIntegerField()
    ticket_price = models.DecimalField(max_digits=8,decimal_places=2)
    available_seats = models.PositiveIntegerField()
    # ⭐ CHANGED: CharField → ImageField (for uploads)
    image = models.ImageField(upload_to='comedy/', blank=True, null=True)
    comedy_type = models.CharField(max_length=50, default='Stand-up')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    duration = models.PositiveIntegerField(default=90)
    popularity = models.CharField(max_length=20, default='Popular')
    experience = models.CharField(max_length=100, default='Professional Comedian')

    class Meta:
        managed = True  # ⭐ CHANGED: Can create/update
        db_table = 'eventapp_comedyshow'  
        verbose_name = 'Comedy Show'
        verbose_name_plural = 'Comedy Shows'

    def __str__(self):
        return self.title


class LiveConcert(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    artist_name = models.CharField(max_length=100)
    music_genre = models.CharField(max_length=100)
    vvip_ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=2500)
    vip_ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=2000)
    couples_ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=1800)
    normal_ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=1500)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18) 
    gst_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    province_fee = models.DecimalField(max_digits=8, decimal_places=2, default=2)
    convenience_fee = models.DecimalField(max_digits=8, decimal_places=2, default=5)
    charity_fee = models.DecimalField(max_digits=8, decimal_places=2, default=2)
    available_seats = models.PositiveIntegerField()
    # ⭐ CHANGED: CharField → ImageField (for uploads)
    image = models.ImageField(upload_to='concerts/', blank=True, null=True)

    class Meta:
        managed = True  # ⭐ CHANGED: Can create/update
        db_table = 'eventapp_liveconcert'  
        verbose_name = 'Live Concert'
        verbose_name_plural = 'Live Concerts'

    def __str__(self):
        return f"{self.title} by {self.artist_name}"


class AmusementPark(models.Model):
    park_name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    rides_available = models.IntegerField()
    family_friendly = models.BooleanField(default=True)
    ticket_price = models.DecimalField(max_digits=8,decimal_places=2)
    available_seats = models.PositiveIntegerField()
    # ⭐ CHANGED: CharField → ImageField (for uploads)
    image = models.ImageField(upload_to='amusement_parks/', blank=True, null=True)

    class Meta:
        managed = True  # ⭐ CHANGED: Can create/update
        db_table = 'eventapp_amusementpark'  
        verbose_name = 'Amusement Park'
        verbose_name_plural = 'Amusement Parks'

    def __str__(self):
        return self.park_name


class AmusementTicket(models.Model):
    amusement_park = models.ForeignKey(AmusementPark, on_delete=models.CASCADE)  # ⭐ CHANGED: CASCADE
    category = models.CharField(max_length=20)
    sub_category = models.CharField(max_length=50)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0, help_text="Discount %")
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    gst_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    age_limit = models.CharField(max_length=100, blank=True, null=True)
    height_limit = models.CharField(max_length=100, blank=True, null=True)
    id_proof_required = models.BooleanField(default=False)

    class Meta:
        managed = True  # ⭐ CHANGED: Can create/update
        db_table = 'eventapp_amusementticket'  
        verbose_name = 'Amusement Ticket'
        verbose_name_plural = 'Amusement Tickets'

    def __str__(self):
        return f"{self.amusement_park.park_name} – {self.category} – {self.sub_category}"