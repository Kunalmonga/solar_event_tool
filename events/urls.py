from django.urls import path
from .views import create_event, all_events_and_changes

urlpatterns = [
    path('create/', create_event, name='create_event'),  # URL pattern for creating an event
    path('all/', all_events_and_changes, name='all_events_and_changes'),  # URL pattern for viewing all events and changes
]
