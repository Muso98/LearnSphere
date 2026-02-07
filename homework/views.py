from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assignment, Submission
from core.models import Class, Subject
from django.utils import timezone

@login_required
def create_assignment(request):
    if request.user.role != 'teacher':
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')
    
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        subject_id = request.POST.get('subject_id')
        description = request.POST.get('description')
        from django.utils.dateparse import parse_datetime
        deadline_str = request.POST.get('deadline')
        deadline = parse_datetime(deadline_str) if deadline_str else None
        
        file = request.FILES.get('file_upload')
        
        target_class = get_object_or_404(Class, id=class_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        Assignment.objects.create(
            subject=subject,
            target_class=target_class,
            description=description,
            deadline=deadline,
            file_upload=file
        )
        messages.success(request, "Assignment created successfully!")
        return redirect('assignment_list')

    classes = Class.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'homework/create_assignment.html', {'classes': classes, 'subjects': subjects})

@login_required
def assignment_list(request):
    today = timezone.now()
    assignments = []
    
    if request.user.role == 'student':
        if request.user.student_class:
            raw_assignments = Assignment.objects.filter(target_class=request.user.student_class, deadline__gte=today).order_by('deadline')
            for a in raw_assignments:
                is_submitted = Submission.objects.filter(assignment=a, student=request.user).exists()
                a.is_submitted = is_submitted
                assignments.append(a)
    elif request.user.role == 'teacher':
        assignments = Assignment.objects.filter(deadline__gte=today).order_by('deadline')
        
    return render(request, 'homework/assignment_list.html', {'assignments': assignments, 'today': today})

@login_required
def submit_homework(request, assignment_id):
    if request.user.role != 'student':
        messages.error(request, "Access denied. Students only.")
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if assignment.deadline < timezone.now():
        messages.error(request, "Deadline passed.")
        return redirect('assignment_list')

    if request.method == 'POST':
        file = request.FILES.get('file_submission')
        if file:
            Submission.objects.create(
                assignment=assignment,
                student=request.user,
                file_submission=file
            )
            messages.success(request, "Homework submitted!")
            return redirect('assignment_list')
        else:
            messages.error(request, "Please upload a file.")

    return render(request, 'homework/submit_homework.html', {'assignment': assignment})

@login_required
def view_submissions(request, assignment_id):
    if request.user.role != 'teacher':
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment).select_related('student')
    
    return render(request, 'homework/view_submissions.html', {'assignment': assignment, 'submissions': submissions})

@login_required
def grade_submission(request, submission_id):
    if request.user.role != 'teacher':
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')
        
    submission = get_object_or_404(Submission, id=submission_id)
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback')
        
        submission.grade = grade
        submission.feedback = feedback
        submission.save()
        
        messages.success(request, f"Graded submission for {submission.student.username}")
        return redirect('view_submissions', assignment_id=submission.assignment.id)
        
    return render(request, 'homework/grade_submission.html', {'submission': submission})
