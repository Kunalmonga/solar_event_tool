from django.db import models
from django.utils import timezone

class Event(models.Model):
    event_date = models.DateField()
    event_name = models.CharField(max_length=255)
    event_description = models.TextField()
    tags = models.CharField(max_length=255)  # Tags related to the event
    additional_info_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.event_name

class WikipediaArticle(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return self.title

class WikipediaChange(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='changes')
    page_title = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    user = models.CharField(max_length=255)
    comment = models.TextField()
    matched_content = models.TextField()

    def __str__(self):
        return f"Change on {self.page_title} at {self.timestamp}"
