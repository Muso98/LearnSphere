"""
AI Assistant URL Configuration
"""
from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('chat/', views.chat_interface, name='chat_interface'),
    path('api/conversation/start/', views.start_conversation, name='start_conversation'),
    path('api/conversation/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('api/conversation/<int:conversation_id>/history/', views.get_conversation_history, name='conversation_history'),
]
