from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from journal.models import Grade
from accounts.models import User
from analytics.models import SkillMap

def home_view(request):
    context = {}
    if request.user.is_authenticated and request.user.role == 'student':
        # AI Foundation: Get Skill Map for student dashboard
        skill_map = SkillMap.objects.filter(student=request.user).first()
        context['skill_map'] = skill_map
        
    return render(request, 'home.html', context)

@login_required
def parent_dashboard(request):
    if request.user.role != 'parent':
        messages.error(request, "Access denied. Parents only.")
        return redirect('home')

    # Get children
    children = request.user.children.all()
    
    # Get last 10 grades for all children
    grades = Grade.objects.filter(student__in=children).select_related('student', 'subject').order_by('-date', '-id')[:10]
    
    # AI Foundation: Get skill maps for each child
    children_with_skills = []
    for child in children:
        skill_map = SkillMap.objects.filter(student=child).first()
        children_with_skills.append({
            'child': child,
            'skill_map': skill_map
        })
    
    context = {
        'children': children,
        'children_with_skills': children_with_skills,
        'recent_grades': grades,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def notifications_view(request):
    # Get all notifications
    notifications = request.user.notifications.all().order_by('-created_at')
    
    unread_ids = list(request.user.notifications.filter(is_read=False).values_list('id', flat=True))
    
    # Update context with list
    context = {
        'notifications': notifications
    }
    
    # After rendering, we should mark them as read. 
    request.user.notifications.filter(id__in=unread_ids).update(is_read=True)
    
    return render(request, 'core/notifications.html', context)
