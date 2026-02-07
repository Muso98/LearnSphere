from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from core.models import Schedule, Class, Subject
from accounts.models import User

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@login_required
# @cache_page(60 * 15) # Cache for 15 minutes
def schedule_list(request):
    """Display weekly schedule"""
    # Allow students, teachers, and directors
    allowed_roles = ['student', 'teacher', 'director']
    if request.user.role not in allowed_roles:
        messages.error(request, "Ruxsat yo'q!")
        return redirect('home')
    
    # Filters - convert to int for easier comparison
    class_filter = request.GET.get('class_id')
    teacher_filter = request.GET.get('teacher_id')
    
    # Convert to int if present
    class_filter_int = int(class_filter) if class_filter and class_filter.isdigit() else None
    teacher_filter_int = int(teacher_filter) if teacher_filter and teacher_filter.isdigit() else None
    
    schedules = Schedule.objects.select_related('class_obj', 'subject', 'teacher').all()
    
    # Role-based filtering logic
    if request.user.role == 'student':
        # Students see ONLY their assigned class
        if request.user.student_class:
            schedules = schedules.filter(class_obj=request.user.student_class)
            class_filter_int = request.user.student_class.id # Lock filter UI
        else:
            schedules = Schedule.objects.none()
            messages.warning(request, "Sizga sinf biriktirilmagan. Iltimos, ma'muriyatga murojaat qiling.")
            
    elif request.user.role == 'teacher':
        # Teachers see ONLY their own schedule
        schedules = schedules.filter(teacher=request.user)
        # Note: We ignore teacher_filter_int from GET to prevent accessing others
        # Class filtering is still allowed if valid logic permits, but UI is hidden.
        # For simplicity, we just show their full schedule.

    # Apply explicit filters (Only relevant for Director now)
    if request.user.role == 'director':
        if class_filter_int:
            schedules = schedules.filter(class_obj_id=class_filter_int)
        if teacher_filter_int:
            schedules = schedules.filter(teacher_id=teacher_filter_int)
    
    # Organize by day
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    schedule_by_day = {}
    for day in days:
        schedule_by_day[day] = schedules.filter(day_of_week=day).order_by('start_time')
    
    # Mark selected items for UI
    classes = Class.objects.all()
    for c in classes:
        c.is_selected = (class_filter_int == c.id)
    
    teachers = User.objects.filter(role='teacher')
    for t in teachers:
        t.is_selected = (teacher_filter_int == t.id)
    
    context = {
        'schedule_by_day': schedule_by_day,
        'classes': classes,
        'teachers': teachers,
        'user_role': request.user.role, # Pass role explicitly if needed
    }
    return render(request, 'schedule/schedule_list.html', context)


@login_required
def schedule_create(request):
    """Create new schedule entry"""
    if request.user.role != 'director':
        messages.error(request, "Faqat direktor jadval qo'sha oladi!")
        return redirect('schedule_list')
    
    if request.method == 'POST':
        try:
            schedule = Schedule(
                class_obj_id=request.POST.get('class_id'),
                subject_id=request.POST.get('subject_id'),
                teacher_id=request.POST.get('teacher_id'),
                room=request.POST.get('room'),
                day_of_week=request.POST.get('day_of_week'),
                start_time=request.POST.get('start_time'),
                end_time=request.POST.get('end_time'),
            )
            schedule.save()  # This will call clean() and check for conflicts
            messages.success(request, "Dars muvaffaqiyatli qo'shildi!")
            return redirect('schedule_list')
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    context = {
        'classes': Class.objects.all(),
        'subjects': Subject.objects.all(),
        'teachers': User.objects.filter(role='teacher'),
    }
    return render(request, 'schedule/schedule_form.html', context)


@login_required
def schedule_edit(request, schedule_id):
    """Edit existing schedule entry"""
    if request.user.role != 'director':
        messages.error(request, "Faqat direktor jadval tahrirlashi mumkin!")
        return redirect('schedule_list')
    
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        try:
            schedule.class_obj_id = request.POST.get('class_id')
            schedule.subject_id = request.POST.get('subject_id')
            schedule.teacher_id = request.POST.get('teacher_id')
            schedule.room = request.POST.get('room')
            schedule.day_of_week = request.POST.get('day_of_week')
            schedule.start_time = request.POST.get('start_time')
            schedule.end_time = request.POST.get('end_time')
            schedule.save()
            messages.success(request, "Dars muvaffaqiyatli yangilandi!")
            return redirect('schedule_list')
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    context = {
        'schedule': schedule,
        'classes': Class.objects.all(),
        'subjects': Subject.objects.all(),
        'teachers': User.objects.filter(role='teacher'),
    }
    return render(request, 'schedule/schedule_form.html', context)


@login_required
def schedule_delete(request, schedule_id):
    """Delete schedule entry"""
    if request.user.role != 'director':
        messages.error(request, "Faqat direktor jadval o'chira oladi!")
        return redirect('schedule_list')
    
    schedule = get_object_or_404(Schedule, id=schedule_id)
    schedule.delete()
    messages.success(request, "Dars o'chirildi!")
    return redirect('schedule_list')
