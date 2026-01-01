from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from .models import (
    User, Event, BookingsEvent, Movie, MovieScreen, TheaterSeat,
    TicketBooking, ComedyShow, BookingComedyShow, LiveConcert,
    LiveConcertTicketBooking, AmusementPark, AmusementTicket,
    AmusementBooking, AmusementBookingItem, OtherAmusementBooking
)

# =============================================
# ⭐ WRITE-ABLE MODELS (managed=True)
# =============================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):  
    list_display = ('email', 'firstname', 'lastname', 'mobile', 'reset_token_status')
    search_fields = ('email', 'firstname', 'lastname', 'mobile')
    readonly_fields = ('password', 'reset_token', 'reset_token_created_at')
    list_filter = ('email',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('firstname', 'lastname', 'email', 'mobile')
        }),
        ('Security', {
            'fields': ('password', 'reset_token', 'reset_token_created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def reset_token_status(self, obj):
        if obj.reset_token:
            return "Active Token"
        return "No Token"
    reset_token_status.short_description = 'Reset Status'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'language', 'genre', 'ticket_price', 'available_seats', 'rating')
    list_filter = ('language', 'genre', 'date', 'rating')
    search_fields = ('title', 'director', 'cast', 'description')
    list_editable = ('ticket_price', 'available_seats', 'rating')
    ordering = ('-date',)
    
    fieldsets = (
        ('Movie Details', {
            'fields': ('title', 'description', 'image', 'language', 'genre')
        }),
        ('Show Information', {
            'fields': ('date', 'time', 'location', 'duration')
        }),
        ('Cast & Crew', {
            'fields': ('director', 'cast')
        }),
        ('Pricing & Rating', {
            'fields': ('ticket_price', 'available_seats', 'rating', 'popularity')
        }),
    )


@admin.register(MovieScreen)
class MovieScreenAdmin(admin.ModelAdmin):
    list_display = ('screen_name', 'movie', 'total_rows', 'seats_per_row', 'total_seats')
    list_filter = ('screen_name',)
    search_fields = ('screen_name', 'movie__title')
    autocomplete_fields = ['movie']
    
    def total_seats(self, obj):
        return obj.total_rows * obj.seats_per_row
    total_seats.short_description = 'Total Seats'


@admin.register(TheaterSeat)
class TheaterSeatAdmin(admin.ModelAdmin):
    list_display = ('seat_number', 'screen', 'seat_type', 'price', 'status')
    list_filter = ('seat_type', 'status', 'screen__screen_name')
    search_fields = ('row', 'number', 'screen__movie__title')
    
    def seat_number(self, obj):
        return f"{obj.row}{obj.number}"
    seat_number.short_description = 'Seat'


@admin.register(ComedyShow)
class ComedyShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'comedian_name', 'date', 'time', 'location', 'ticket_price', 'available_seats')
    list_filter = ('comedy_type', 'date', 'popularity')
    search_fields = ('title', 'comedian_name', 'description', 'location')
    list_editable = ('ticket_price', 'available_seats')
    
    fieldsets = (
        ('Show Details', {
            'fields': ('title', 'description', 'image', 'comedian_name', 'experience')
        }),
        ('Show Information', {
            'fields': ('date', 'time', 'location', 'comedy_type', 'duration')
        }),
        ('Audience & Pricing', {
            'fields': ('age_limit', 'total_seats', 'available_seats', 'ticket_price')
        }),
        ('Ratings', {
            'fields': ('rating', 'popularity')
        }),
    )


@admin.register(LiveConcert)
class LiveConcertAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist_name', 'date', 'time', 'music_genre', 'available_seats')
    list_filter = ('music_genre', 'date')
    search_fields = ('title', 'artist_name', 'description', 'location')
    
    fieldsets = (
        ('Concert Details', {
            'fields': ('title', 'description', 'image', 'artist_name', 'music_genre')
        }),
        ('Show Information', {
            'fields': ('date', 'time', 'location')
        }),
        ('Ticket Pricing', {
            'fields': ('vvip_ticket_price', 'vip_ticket_price', 'couples_ticket_price', 'normal_ticket_price')
        }),
        ('Fees & Taxes', {
            'fields': ('gst_percentage', 'province_fee', 'convenience_fee', 'charity_fee')
        }),
        ('Availability', {
            'fields': ('available_seats',)
        }),
    )


@admin.register(AmusementPark)
class AmusementParkAdmin(admin.ModelAdmin):
    list_display = ('park_name', 'date', 'time', 'location', 'rides_available', 'ticket_price', 'available_seats')
    list_filter = ('family_friendly', 'date')
    search_fields = ('park_name', 'description', 'location')
    list_editable = ('ticket_price', 'available_seats')
    
    fieldsets = (
        ('Park Information', {
            'fields': ('park_name', 'description', 'image')
        }),
        ('Location & Timing', {
            'fields': ('date', 'time', 'location')
        }),
        ('Park Features', {
            'fields': ('rides_available', 'family_friendly')
        }),
        ('Pricing', {
            'fields': ('ticket_price', 'available_seats')
        }),
    )


@admin.register(AmusementTicket)
class AmusementTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_display', 'amusement_park', 'base_price', 'discount_percent', 'grand_total')
    list_filter = ('category', 'sub_category')
    search_fields = ('amusement_park__park_name', 'category', 'sub_category')
    autocomplete_fields = ['amusement_park']
    
    def ticket_display(self, obj):
        return f"{obj.category} - {obj.sub_category}"
    ticket_display.short_description = 'Ticket Type'


# =============================================
# ⭐ READ-ONLY MODELS (managed=False)
# =============================================




@admin.register(BookingsEvent)
class BookingsEventAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'event', 'number_of_tickets', 'total_amount', 'status_display', 'payment_status_display', 'booking_date')
    list_filter = ('status', 'payment_status', 'booking_date')
    search_fields = ('booking_id', 'customer_name', 'customer_email', 'customer_phone', 'event__name')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'booking_id')
    date_hierarchy = 'booking_date'
    
    def status_display(self, obj):
        color_map = {
            'confirmed': 'green',
            'pending': 'orange',
            'cancelled': 'red',
            'completed': 'blue'
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_display.short_description = 'Status'
    
    def payment_status_display(self, obj):
        if obj.payment_status:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ PAID</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ PENDING</span>'
        )
    payment_status_display.short_description = 'Payment'


@admin.register(TicketBooking)
class TicketBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'movie', 'screen', 'grand_total', 'payment_status_display', 'booked_at')
    list_filter = ('payment_status', 'booked_at')
    search_fields = ('user__email', 'movie__title', 'screen__screen_name')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    
    def payment_status_display(self, obj):
        if obj.payment_status:
            return "✅ Paid"
        return "❌ Pending"
    payment_status_display.short_description = 'Payment'


@admin.register(BookingComedyShow)
class BookingComedyShowAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'comedy_show', 'number_of_tickets', 'total_price', 'payment_status_display')
    list_filter = ('payment_status', 'booking_date')
    search_fields = ('booking_id', 'user__username', 'comedy_show__title')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    
    def payment_status_display(self, obj):
        if obj.payment_status:
            return "✅ Paid"
        return "❌ Pending"
    payment_status_display.short_description = 'Payment'


@admin.register(LiveConcertTicketBooking)
class LiveConcertTicketBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'concert', 'quantity', 'total_amount', 'payment_status', 'booked_at')
    list_filter = ('payment_status', 'booked_at')
    search_fields = ('user__email', 'concert__title')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')


@admin.register(AmusementBooking)
class AmusementBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'amusement_park', 'grand_total', 'payment_status_display', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('booking_id', 'customer_name', 'customer_email', 'amusement_park__park_name')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    
    def payment_status_display(self, obj):
        if obj.payment_status:
            return "✅ Paid"
        return "❌ Pending"
    payment_status_display.short_description = 'Payment'


@admin.register(AmusementBookingItem)
class AmusementBookingItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_booking', 'ticket_type', 'quantity', 'total_with_gst')
    list_filter = ('booking__amusement_park',)
    search_fields = ('booking__booking_id', 'ticket_type__amusement_park__park_name')
    readonly_fields = ('subtotal', 'gst_amount', 'total_with_gst')
    
    def get_booking(self, obj):
        if obj.booking:
            return obj.booking.booking_id
        elif obj.other_booking:
            return obj.other_booking.booking_id
        return "No Booking"
    get_booking.short_description = 'Booking ID'


@admin.register(OtherAmusementBooking)
class OtherAmusementBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'amusement_park', 'quantity', 'grand_total', 'payment_status_display', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('booking_id', 'customer_name', 'customer_email', 'amusement_park__park_name')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    
    def payment_status_display(self, obj):
        if obj.payment_status:
            return "✅ Paid"
        return "❌ Pending"
    payment_status_display.short_description = 'Payment'


# =============================================
# ⭐ ADMIN SITE CUSTOMIZATION
# =============================================

# Remove default Group from admin
admin.site.unregister(Group)

# Customize admin site
admin.site.site_header = "🎪 EventProject - Admin Dashboard"
admin.site.site_title = "EventProject Admin Portal"
admin.site.index_title = "📊 Dashboard Overview"

# Custom admin ordering
admin.site._registry = dict(sorted(
    admin.site._registry.items(),
    key=lambda x: (
        0 if x[0].__name__ in ['Event', 'Movie', 'ComedyShow', 'LiveConcert', 'AmusementPark'] 
        else 1 if x[0].__name__ in ['CustomUser', 'BookingsEvent', 'TicketBooking']
        else 2
    )
))