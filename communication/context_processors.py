from .models import Conversation, OnlineMeeting
from django.utils import timezone
from core.models import Class

def unread_messages(request):
    if not request.user.is_authenticated:
        return {
            'unread_messages_count': 0,
            'upcoming_meetings_count': 0
        }
    
    # Unread Messages Count
    msg_count = 0
    conversations = request.user.conversations.all()
    for c in conversations:
        msg_count += c.messages.exclude(sender=request.user).filter(is_read=False).count()

    # Upcoming Meetings Count
    now = timezone.now()
    meetings = OnlineMeeting.objects.none()
    
    if request.user.role == 'teacher':
        own_meetings = OnlineMeeting.objects.filter(organizer=request.user, start_time__gte=now)
        general_meetings = OnlineMeeting.objects.filter(audience='teachers', start_time__gte=now)
        meetings = (own_meetings | general_meetings).distinct()

    elif request.user.role == 'student':
        if request.user.student_class:
            class_meetings = OnlineMeeting.objects.filter(class_obj=request.user.student_class, audience='class', start_time__gte=now)
            meetings = class_meetings

    elif request.user.role == 'parent':
        children_classes = Class.objects.filter(students__in=request.user.children.all()).distinct()
        general_meetings = OnlineMeeting.objects.filter(audience='parents', start_time__gte=now)
        class_meetings = OnlineMeeting.objects.filter(class_obj__in=children_classes, audience='class', start_time__gte=now)
        meetings = (general_meetings | class_meetings).distinct()

    elif request.user.role in ['director', 'admin']:
         meetings = OnlineMeeting.objects.filter(start_time__gte=now)
        
    meeting_count = meetings.count() if hasattr(meetings, 'count') else 0
        
    return {
        'unread_messages_count': msg_count,
        'upcoming_meetings_count': meeting_count
    }
