from django.contrib import admin
from .models import Conversation, Message, AgentContext, AgentAction


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'agent_type', 'title', 'created_at', 'is_active']
    list_filter = ['agent_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'title']
    date_hierarchy = 'created_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'content_preview', 'timestamp', 'tokens_used']
    list_filter = ['role', 'timestamp']
    search_fields = ['content']
    date_hierarchy = 'timestamp'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(AgentContext)
class AgentContextAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'context_key', 'cached_at', 'expires_at']
    list_filter = ['context_key', 'cached_at']
    search_fields = ['context_key']


@admin.register(AgentAction)
class AgentActionAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'action_type', 'description_preview', 'performed_at', 'success']
    list_filter = ['action_type', 'success', 'performed_at']
    search_fields = ['description']
    date_hierarchy = 'performed_at'
    
    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description'
