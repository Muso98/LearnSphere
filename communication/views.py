from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.models import User
from core.models import Class
from .models import Conversation, Message, OnlineMeeting
from django.utils import timezone

@login_required
def chat_list(request):
    conversations = request.user.conversations.all().order_by('-updated_at')
    
    # For starting new chats: show relevant users based on role
    available_users = []
    if request.user.role == 'teacher':
        # Teachers can chat with parents of their students (this logic can be complex, simplifying for MVP to all parents)
        # Ideally: filter parents whose children are in classes the teacher teaches
        available_users = User.objects.filter(role='parent')
    elif request.user.role == 'parent':
        # Parents can chat with teachers
        available_users = User.objects.filter(role='teacher')
    elif request.user.role in ['director', 'admin']:
        # Director can chat with everyone
        available_users = User.objects.exclude(id=request.user.id)
    
    context = {
        'conversations': conversations,
        'available_users': available_users
    }
    return render(request, 'communication/chat_list.html', context)

@login_required
def start_chat(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        return redirect('chat_list')
        
    # Check if conversation already exists
    # This filter is a bit tricky for exact match on M2M, simpler approach:
    # Find conversation where both are participants and count is 2
    conversations = Conversation.objects.filter(participants=request.user).filter(participants=target_user)
    
    conversation = None
    for c in conversations:
        if c.participants.count() == 2:
            conversation = c
            break
            
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, target_user)
        
    return redirect('chat_detail', conversation_id=conversation.id)

@login_required
def chat_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        messages.error(request, "Access denied")
        return redirect('chat_list')
        
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            return redirect('chat_detail', conversation_id=conversation.id)
            
    messages_list = conversation.messages.all()
    # Mark others' messages as read
    messages_list.exclude(sender=request.user).update(is_read=True)
    
    other_participant = conversation.participants.exclude(id=request.user.id).first()
    
    context = {
        'conversation': conversation,
        'messages': messages_list,
        'other_participant': other_participant
    }
    return render(request, 'communication/chat_detail.html', context)

@login_required
def meeting_list(request):
    meetings = []
    if request.user.role == 'teacher':
        # Teachers see:
        # 1. Own meetings
        # 2. Meetings for 'teachers' audience
        # 3. Meetings for 'class' audience IF they are the organizer (covered by 1) OR maybe if they teach that class? 
        #    For now, keeping it simple: Own + Audience='teachers'
        own_meetings = OnlineMeeting.objects.filter(organizer=request.user)
        general_meetings = OnlineMeeting.objects.filter(audience='teachers')
        meetings = (own_meetings | general_meetings).distinct().order_by('start_time')

    elif request.user.role == 'student':
        if request.user.student_class:
            # Student sees 'class' meetings for their class
            class_meetings = OnlineMeeting.objects.filter(class_obj=request.user.student_class, audience='class')
            meetings = class_meetings.order_by('start_time')

    elif request.user.role == 'parent':
        children_classes = Class.objects.filter(students__in=request.user.children.all()).distinct()
        # Parent sees:
        # 1. 'parents' audience meetings
        # 2. 'class' audience meetings for their children's classes
        general_meetings = OnlineMeeting.objects.filter(audience='parents')
        class_meetings = OnlineMeeting.objects.filter(class_obj__in=children_classes, audience='class')
        meetings = (general_meetings | class_meetings).distinct().order_by('start_time')

    elif request.user.role in ['director', 'admin']:
         meetings = OnlineMeeting.objects.all().order_by('start_time')
        
    context = {
        'meetings': meetings,
    }
    return render(request, 'communication/meeting_list.html', context)

@login_required
def create_meeting(request):
    if request.user.role not in ['teacher', 'admin', 'director']:
        messages.error(request, "Access denied")
        return redirect('meeting_list')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        audience = request.POST.get('audience', 'class')
        class_id = request.POST.get('class_id')
        start_time = request.POST.get('start_time')
        link = request.POST.get('link')
        
        class_obj = None
        if audience == 'class' and class_id:
            class_obj = get_object_or_404(Class, id=class_id)
        elif audience != 'class':
            class_obj = None # Ensure class is None if audience is not class
            
        OnlineMeeting.objects.create(
            title=title,
            class_obj=class_obj,
            organizer=request.user,
            start_time=start_time,
            meeting_link=link,
            audience=audience
        )
        messages.success(request, "Meeting scheduled!")
        return redirect('meeting_list')
        
    classes = Class.objects.all()
    return render(request, 'communication/create_meeting.html', {'classes': classes})

@login_required
def broadcast_message(request):
    if request.user.role not in ['director', 'admin']:
        messages.error(request, "Access denied")
        return redirect('chat_list')
        
    if request.method == 'POST':
        audience = request.POST.get('audience')
        content = request.POST.get('content')
        
        if not content:
            messages.error(request, "Xabar matni bo'sh bo'lmasligi kerak")
            return redirect('chat_list')
            
        recipients = []
        if audience == 'teachers':
            recipients = User.objects.filter(role='teacher')
        elif audience == 'parents':
            recipients = User.objects.filter(role='parent')
        else:
            messages.error(request, "Noto'g'ri qabul qiluvchi guruhi")
            return redirect('chat_list')
            
        count = 0
        for recipient in recipients:
            if recipient == request.user:
                continue
                
            # Find or create conversation
            # This is a bit inefficient for large numbers, but fine for MVP
            conversation = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()
            
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, recipient)
            
            # Create message
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            count += 1
            
        messages.success(request, f"Xabar {count} ta foydalanuvchiga yuborildi")
        return redirect('chat_list')
        
    return redirect('chat_list')
