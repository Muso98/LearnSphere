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
    
    # 1. Subject Performance Analysis (Avg Grade per Subject)
    from django.db.models import Avg, Count, Q
    subject_performance = Grade.objects.values('subject__name').annotate(
        avg_grade=Avg('value')
    ).order_by('-avg_grade')
    
    # Prepare data for Chart.js
    subject_labels = [item['subject__name'] for item in subject_performance]
    subject_data = [round(item['avg_grade'], 1) for item in subject_performance]
    
    # 2. Attendance Analysis (Avg Attendance per Class)
    # Simple logic: Percentage of 'present' vs 'absent' overall or per class
    # Let's do Overall Attendance for Pie Chart
    attendance_stats = Attendance.objects.values('status').annotate(count=Count('status'))
    attendance_data = {
        'present': 0,
        'absent': 0,
        'late': 0,
        'excused': 0
    }
    for item in attendance_stats:
        attendance_data[item['status']] = item['count']
        
    # 3. Activity Ratings
    # Top Teachers (by number of grades given)
    top_teachers = Grade.objects.values('teacher__first_name', 'teacher__last_name').annotate(
        grade_count=Count('id')
    ).order_by('-grade_count')[:5]
    
    # Top Students (by GPA) -- Corrected lookup path
    # Grade -> Student (User) -> Class -> Name
    # student__student_class__name might be correct if User has student_class FK.
    # Let's check User model.. if standard User, it doesn't have student_class directly unless extended.
    # Ah, User model in accounts/models.py has student_class.
    top_students = Grade.objects.values(
        'student__first_name', 'student__last_name', 'student__student_class__name'
    ).annotate(
        gpa=Avg('value')
    ).order_by('-gpa')[:5]
    
    # Recent activity - Removed 'teacher' from select_related as it doesn't exist
    recent_grades = Grade.objects.select_related('student', 'subject').order_by('-date')[:10]
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'recent_grades': recent_grades,
        # Analytics
        'subject_labels': subject_labels,
        'subject_data': subject_data,
        'attendance_data': list(attendance_data.values()), # [present, absent, late, excused]
        'attendance_labels': list(attendance_data.keys()),
        # Ratings
        'top_teachers': top_teachers,
        'top_students': top_students,
    }
    return render(request, 'core/director_dashboard.html', context)
