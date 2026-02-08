"""
AI Assistant Views
API endpoints for chat interface
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json

from .models import Conversation, Message
from .agents import TeacherAgent, ParentAgent, StudentAgent


@login_required
def chat_interface(request):
    """Render chat interface"""
    # Determine agent type based on user role
    agent_type = 'student'  # default
    if request.user.role == 'teacher':
        agent_type = 'teacher'
    elif request.user.role == 'parent':
        agent_type = 'parent'
    elif request.user.role == 'student':
        agent_type = 'student'
    
    # Get user's recent conversations
    conversations = Conversation.objects.filter(user=request.user, is_active=True)[:10]
    
    return render(request, 'ai_assistant/chat.html', {
        'conversations': conversations,
        'default_agent': agent_type
    })


@login_required
@require_http_methods(["POST"])
def start_conversation(request):
    """Start a new conversation with AI agent"""
    try:
        data = json.loads(request.body)
        agent_type = data.get('agent_type', 'student')
        
        # Validate agent type
        if agent_type not in ['teacher', 'parent', 'student']:
            return JsonResponse({'error': 'Invalid agent type'}, status=400)
        
        # Create conversation
        conversation = Conversation.objects.create(
            user=request.user,
            agent_type=agent_type,
            title=f"New {agent_type.title()} Chat"
        )
        
        return JsonResponse({
            'conversation_id': conversation.id,
            'agent_type': conversation.agent_type,
            'created_at': conversation.created_at.isoformat()
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def send_message(request, conversation_id):
    """Send message to AI agent"""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # Get appropriate agent
        agent = _get_agent(conversation.agent_type, request.user, conversation)
        
        # Process message
        result = agent.process_message(user_message)
        
        # Save AI response
        ai_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['response'],
            tokens_used=result.get('tokens_used', 0)
        )
        
        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save()
        
        return JsonResponse({
            'message_id': ai_message.id,
            'response': result['response'],
            'actions': result.get('actions', []),
            'timestamp': ai_message.timestamp.isoformat()
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_conversation_history(request, conversation_id):
    """Get conversation message history"""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        messages = conversation.messages.all()
        
        return JsonResponse({
            'conversation_id': conversation.id,
            'agent_type': conversation.agent_type,
            'messages': [
                {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _get_agent(agent_type, user, conversation):
    """Get appropriate agent instance"""
    if agent_type == 'teacher':
        return TeacherAgent(user, conversation)
    elif agent_type == 'parent':
        return ParentAgent(user, conversation)
    else:
        return StudentAgent(user, conversation)
