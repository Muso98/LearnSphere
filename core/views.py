from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from journal.models import Grade
from accounts.models import User

@login_required
def parent_dashboard(request):
    if request.user.role != 'parent':
        messages.error(request, "Access denied. Parents only.")
        return redirect('home')

    # Get children
    children = request.user.children.all()
    
    # Get last 10 grades for all children
    # If parent has multiple children, we can group by child or just show a mixed list.
    # User asked: "farzandining oxirgi 10 ta bahosini ko'rsatuvchi sodda 'Dashboard' yarat"
    # I'll show grades per child or just all recent grades. Given "Sodda (simple)", 
    # a combined list is simpler or a list per child. 
    # I'll fetch recent grades for any of the children.
    
    grades = Grade.objects.filter(student__in=children).select_related('student', 'subject').order_by('-date', '-id')[:10]
    
    context = {
        'children': children,
        'recent_grades': grades,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def notifications_view(request):
    # Get all notifications
    notifications = request.user.notifications.all().order_by('-created_at')
    
    # Mark as read (simple approach: mark all as read when viewed)
    # request.user.notifications.filter(is_read=False).update(is_read=True)
    # For now, let's keep them unread to see the badge, or maybe mark them read.
    # User didn't specify logic to mark read, but usually viewing list marks them read.
    # Let's NOT mark read automatically for now, so user can see badge persistence in test.
    # Or better, mark them read so badge disappears, which is expected behavior.
    
    unread_ids = list(request.user.notifications.filter(is_read=False).values_list('id', flat=True))
    
    # Update context with list
    context = {
        'notifications': notifications
    }
    
    # After rendering, we should mark them as read. 
    # But since we return render, we do updating here.
    request.user.notifications.filter(id__in=unread_ids).update(is_read=True)
    
    return render(request, 'core/notifications.html', context)

