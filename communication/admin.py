from django.contrib import admin
from .models import Conversation, Message, OnlineMeeting

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(OnlineMeeting)
