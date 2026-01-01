# admin_panel/forms.py
from django import forms
from .models import Event, Movie, LiveConcert

from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'location', 'date', 'time', 
                  'total_seats', 'available_seats', 'ticket_price', 'image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'total_seats': 'Total Seats',
            'available_seats': 'Available Seats (leave empty to auto-set)',
            'ticket_price': 'Ticket Price (₹)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        total_seats = cleaned_data.get('total_seats')
        available_seats = cleaned_data.get('available_seats')
        
        if available_seats and available_seats > total_seats:
            raise forms.ValidationError(
                "Available seats cannot exceed total seats."
            )
        
        if not available_seats and total_seats:
            cleaned_data['available_seats'] = total_seats
        
        return cleaned_data

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'image', 'location', 'date', 'time', 'language', 'genre', 'ticket_price', 'available_seats']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'cast': forms.Textarea(attrs={'rows': 3}),
        }

class ConcertForm(forms.ModelForm):
    class Meta:
        model = LiveConcert
        fields = ['title', 'description', 'image', 'location', 'date', 'time', 'artist_name', 'music_genre', 'available_seats']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }