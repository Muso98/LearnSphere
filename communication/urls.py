from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:conversation_id>/', views.chat_detail, name='chat_detail'),
    path('meetings/', views.meeting_list, name='meeting_list'),
    path('meetings/create/', views.create_meeting, name='create_meeting'),
    path('broadcast/', views.broadcast_message, name='broadcast_message'),
]
