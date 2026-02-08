from django.db import models
from django.conf import settings
from core.models import Class

class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} ({', '.join([u.username for u in self.participants.all()])})"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"

class OnlineMeeting(models.Model):
    title = models.CharField(max_length=200)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='meetings', null=True, blank=True)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_meetings')
    start_time = models.DateTimeField()
    meeting_link = models.URLField(help_text="Zoom, Google Meet, or Jitsi link")
    created_at = models.DateTimeField(auto_now_add=True)

    AUDIENCE_CHOICES = (
        ('class', 'Specific Class'),
        ('teachers', 'All Teachers'),
        ('parents', 'All Parents'),
    )
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='class')

    def __str__(self):
        return f"{self.title} - {self.audience} - {self.start_time}"
