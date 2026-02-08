from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """Store chat conversations between users and AI agents"""
    AGENT_TYPES = [
        ('teacher', 'Teacher Assistant'),
        ('parent', 'Parent Monitor'),
        ('student', 'Student Tutor'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_conversations')
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPES)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_agent_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"


class Message(models.Model):
    """Individual messages in a conversation"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    tokens_used = models.IntegerField(default=0, help_text="Number of tokens used for this message")
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class AgentContext(models.Model):
    """Cache frequently accessed data for faster agent responses"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='context_cache')
    context_key = models.CharField(max_length=100, help_text="e.g., 'recent_grades', 'class_schedule'")
    context_data = models.JSONField(help_text="Cached data in JSON format")
    cached_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this cache should be invalidated")
    
    class Meta:
        unique_together = ['conversation', 'context_key']
    
    def __str__(self):
        return f"{self.conversation.id} - {self.context_key}"


class AgentAction(models.Model):
    """Log autonomous actions performed by AI agents"""
    ACTION_TYPES = [
        ('notification_sent', 'Notification Sent'),
        ('report_generated', 'Report Generated'),
        ('data_analyzed', 'Data Analyzed'),
        ('resource_recommended', 'Resource Recommended'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    action_data = models.JSONField(null=True, blank=True, help_text="Additional action metadata")
    performed_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-performed_at']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.performed_at.strftime('%Y-%m-%d %H:%M')}"
