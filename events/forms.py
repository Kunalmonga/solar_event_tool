from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_date', 'event_name', 'event_description', 'tags', 'additional_info_link']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'event_name': forms.TextInput(attrs={'maxlength': 255}),
            'event_description': forms.Textarea(),
            'tags': forms.TextInput(attrs={'maxlength': 255}),
            'additional_info_link': forms.URLInput()
        }
