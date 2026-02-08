from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Class, Subject
from accounts.models import User
from core.models import Class, Subject, Schedule
from accounts.models import User
from .models import Grade, Attendance, GradeAudit
from django.utils import timezone

@login_required
def gradebook_view(request):
    # Ensure user is teacher
    if request.user.role != 'teacher':
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')

    selected_class_id = request.GET.get('class_id')
    selected_subject_id = request.GET.get('subject_id')
    
    classes = Class.objects.filter(schedules__teacher=request.user).distinct()
    subjects = Subject.objects.filter(schedules__teacher=request.user).distinct()
    
    # Add is_selected attribute to each class and subject for template
    for cls in classes:
        cls.is_selected = (selected_class_id and str(cls.id) == selected_class_id)
    
    for subj in subjects:
        subj.is_selected = (selected_subject_id and str(subj.id) == selected_subject_id)
    
    students = []
    current_class = None
    current_subject = None

    if selected_class_id and selected_subject_id:
        current_class = get_object_or_404(Class, id=selected_class_id)
        current_subject = get_object_or_404(Subject, id=selected_subject_id)
        
        # Verify teacher schedule
        if not Schedule.objects.filter(teacher=request.user, class_obj=current_class, subject=current_subject).exists():
             messages.error(request, "Siz bu sinfga bu fandan dars bermaysiz!")
             return redirect('gradebook')

        students = User.objects.filter(student_class=current_class, role='student')
    
    
    if request.method == 'POST':
        # Check if bulk save
        if request.POST.get('bulk_save'):
            # Bulk grade submission
            date = request.POST.get('date') or timezone.now().date()
            saved_count = 0
            
            for student in students:
                grade_value = request.POST.get(f'grade_{student.id}')
                comment = request.POST.get(f'comment_{student.id}', '').strip()
                
                if grade_value:
                    # Validate grade
                    try:
                        grade_int = int(grade_value)
                        if not (1 <= grade_int <= 5):
                            messages.warning(request, f"Student {student.first_name}'s grade '{grade_value}' is invalid. Must be between 1 and 5.")
                            continue
                    except ValueError:
                        messages.warning(request, f"Student {student.first_name}'s grade '{grade_value}' is not a valid number.")
                        continue

                    previous_value = None
                    try:
                        existing_grade = Grade.objects.get(student=student, subject=current_subject, date=date)
                        previous_value = existing_grade.value
                    except Grade.DoesNotExist:
                        pass

                    grade_obj, created = Grade.objects.update_or_create(
                        student=student,
                        subject=current_subject,
                        date=date,
                        defaults={'value': grade_int, 'comment': comment, 'teacher': request.user}
                    )
                    
                    # Audit Trail
                    if created:
                        action = 'create'
                    elif previous_value != grade_int:
                        action = 'update'
                    else:
                        action = None # No change
                    
                    if action:
                        GradeAudit.objects.create(
                            grade=grade_obj,
                            changed_by=request.user,
                            previous_value=previous_value,
                            new_value=grade_int,
                            action=action
                        )
                    
                    # Save competency metadata if selected
                    competency = request.POST.get(f'competency_{student.id}')
                    if competency:
                        # Merge with existing metadata or create new
                        meta = grade_obj.metadata or {}
                        meta['competency'] = competency
                        grade_obj.metadata = meta
                        grade_obj.save()

                    saved_count += 1
                    
                    # Create notification for low grades (3 and below)
                    if grade_int <= 3:
                        # Find parent
                        parent = User.objects.filter(role='parent', children=student).first()
                        if parent:
                            from core.models import Notification
                            message = f"{student.first_name} {current_subject.name} fanidan {grade_int} baho oldi"
                            if comment:
                                message += f". O'qituvchi izohi: {comment}"
                            
                            Notification.objects.create(
                                user=parent,
                                message=message
                            )
            
            messages.success(request, f"{saved_count} ta baho saqlandi!")
            return redirect(request.get_full_path())
        else:
            # Single grade submission (legacy HTMX)
            student_id = request.POST.get('student_id')
            grade_value = request.POST.get('grade_value')
            date_str = request.POST.get('date')
            
            student = get_object_or_404(User, id=student_id)
            
            grade = Grade.objects.create(
                student=student,
                subject=current_subject,
                teacher=request.user,
                value=grade_value,
                date=date_str or timezone.now()
            )

            # Audit Trail
            GradeAudit.objects.create(
                grade=grade,
                changed_by=request.user,
                previous_value=None,
                new_value=grade_value,
                action='create'
            )
            
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                return HttpResponse(f"""
                    <button type="submit" class="btn btn-sm btn-success" disabled>Saved!</button>
                    <script>
                        setTimeout(() => {{
                            htmx.trigger(htmx.find("#form-{student.id}"), "reset");
                        }}, 1000);
                    </script>
                """)
                
            messages.success(request, f"Grade added for {student.username}")
            return redirect(request.get_full_path())

    context = {
        'classes': classes,
        'subjects': subjects,
        'selected_class': current_class,
        'selected_subject': current_subject,
        'students': students,
        'today': timezone.now().date(),
    }
    return render(request, 'journal/gradebook.html', context)

@login_required
def attendance_view(request):
    if request.user.role != 'teacher':
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')
        
    selected_class_id = request.GET.get('class_id')
    classes = Class.objects.all()
    students = []
    current_class = None
    
    # Add is_selected attribute to each class for template
    for cls in classes:
        cls.is_selected = (selected_class_id and str(cls.id) == selected_class_id)
    
    if selected_class_id:
        current_class = get_object_or_404(Class, id=selected_class_id)
        students = User.objects.filter(student_class=current_class, role='student')
        
        
    if request.method == 'POST':
        # Check if bulk save
        if request.POST.get('bulk_save'):
            # Bulk attendance submission
            date = request.POST.get('date') or timezone.now().date()
            saved_count = 0
            
            for student in students:
                status = request.POST.get(f'attendance_{student.id}')
                if status:
                    Attendance.objects.update_or_create(
                        student=student,
                        date=date,
                        defaults={'status': status}
                    )
                    saved_count += 1
                    
                    # Create notification for absent students
                    if status == 'absent':
                        parent = User.objects.filter(role='parent', children=student).first()
                        if parent:
                            from core.models import Notification
                            Notification.objects.create(
                                user=parent,
                                message=f"{student.first_name} {date} sanasida darsga kelmadi"
                            )
            
            messages.success(request, f"{saved_count} ta davomat belgilandi!")
            return redirect(request.get_full_path())
        else:
            # Single attendance submission (legacy HTMX)
            student_id = request.POST.get('student_id')
            status = request.POST.get('status')
            date_str = request.POST.get('date')
            
            student = get_object_or_404(User, id=student_id)
            
            # update_or_create to avoid duplicate attendance for same day
            Attendance.objects.update_or_create(
                student=student,
                date=date_str or timezone.now().date(),
                defaults={'status': status}
            )
            
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                return HttpResponse('<span class="badge bg-success">Saved</span>')
                
            messages.success(request, f"Attendance marked for {student.username}")
            return redirect(request.get_full_path())
        
    context = {
        'classes': classes,
        'selected_class': current_class,
        'students': students,
        'today': timezone.now().date(),
    }
    return render(request, 'journal/attendance.html', context)
