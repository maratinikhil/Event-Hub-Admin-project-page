# admin_panel/forms.py
from django import forms
from .models import Event, Movie, LiveConcert

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'image', 'location', 'date', 'time', 'total_seats', 'ticket_price']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

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