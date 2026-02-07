from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User
from journal.models import Grade, Attendance
from core.models import Class, Subject, School
from django.db.models import Count

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        messages.error(request, "Access denied. Students only.")
        return redirect('home')
        
    # Get student's grades and attendance
    grades = Grade.objects.filter(student=request.user).select_related('subject').order_by('-date')
    attendance = Attendance.objects.filter(student=request.user).order_by('-date')
    
    # Get Competencies from Subjects (via Class Schedule)
    competencies_data = []
    if request.user.student_class:
        # Subjects linked to student's class via Schedule
        subjects = Subject.objects.filter(schedules__class_obj=request.user.student_class).distinct()
        
        for sub in subjects:
            # Metadata structure expected: {"competencies": ["Skill 1", "Skill 2"], "ai_tutor": {...}}
            comps = sub.metadata.get('competencies', [])
            if comps:
                competencies_data.append({
                    'subject': sub.name,
                    'skills': comps,
                    'metadata': sub.metadata # Pass full metadata for other uses
                })
    
    context = {
        'grades': grades,
        'attendance': attendance,
        'competencies': competencies_data,
    }
    return render(request, 'core/student_dashboard.html', context)

@login_required
def director_dashboard(request):
    if request.user.role != 'director':
        messages.error(request, "Access denied. Directors only.")
        return redirect('home')
    
    # Stats
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_classes = Class.objects.count()
    
    # Recent activity
    recent_grades = Grade.objects.select_related('student', 'subject').order_by('-date')[:10]
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'recent_grades': recent_grades,
    }
    return render(request, 'core/director_dashboard.html', context)
