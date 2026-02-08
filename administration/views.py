from django.utils.translation import gettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Count, Q
from django.conf import settings
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from gamification.models import Reward, Redemption, PointTransaction
from django.db.models import Sum, Count, Avg
from django.utils import timezone
import json
import pandas as pd
from django.views.decorators.http import require_POST

from .models import Room, RoomBooking, TeacherAssignment
from .forms import UserCreateForm, UserEditForm, ClassForm, SubjectForm, TeacherAssignmentForm
from core.models import Class, Subject
from journal.models import Grade, Attendance


@login_required
def teacher_assignment(request):
    """View to assign subjects and classes to teachers"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
        
    if request.method == 'POST':
        form = TeacherAssignmentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "O'qituvchiga fan va sinf muvaffaqiyatli biriktirildi!")
                return redirect('teacher_assignment')
            except Exception as e:
                messages.error(request, f"Xatolik yuz berdi: {str(e)}")
        else:
            messages.error(request, "Iltimos, ma'lumotlarni to'g'ri kiriting.")
    else:
        form = TeacherAssignmentForm()
    
    assignments = TeacherAssignment.objects.all().order_by('-created_at')
    
    context = {
        'form': form,
        'assignments': assignments,
    }
    return render(request, 'administration/teacher_assignment.html', context)

@login_required
def teacher_assignment_delete(request, assignment_id):
    """View to delete a teacher assignment"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
        
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id)
    assignment.delete()
    messages.success(request, "Biriktiruv o'chirildi.")
    return redirect('teacher_assignment')


def is_admin_user(user):
    """Check if user is admin, director, or superuser"""
    return user.is_superuser or user.role in ['admin', 'director']


@login_required
def admin_dashboard(request):
    """Main admin dashboard with statistics and charts"""
    # Check if user is admin, director, or superuser
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    # Get statistics
    User = settings.AUTH_USER_MODEL
    from django.apps import apps
    UserModel = apps.get_model(User)
    
    total_users = UserModel.objects.count()
    total_students = UserModel.objects.filter(role='student').count()
    total_teachers = UserModel.objects.filter(role='teacher').count()
    total_classes = Class.objects.count()
    total_subjects = Subject.objects.count()
    
    # Today's attendance rate
    today = timezone.now().date()
    total_attendance_today = Attendance.objects.filter(date=today).count()
    present_today = Attendance.objects.filter(date=today, status='present').count()
    attendance_rate = round((present_today / total_attendance_today * 100), 1) if total_attendance_today > 0 else 0
    
    # Average performance (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    avg_performance = Grade.objects.filter(date__gte=thirty_days_ago).aggregate(Avg('value'))['value__avg']
    avg_performance = round(avg_performance, 2) if avg_performance else 0
    
    # Recent activity - last 10 grades
    recent_grades = Grade.objects.select_related('student', 'subject', 'teacher').order_by('-date')[:10]
    
    # Recent users - last 5
    recent_users = UserModel.objects.order_by('-date_joined')[:5]
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'attendance_rate': attendance_rate,
        'avg_performance': avg_performance,
        'recent_grades': recent_grades,
        'recent_users': recent_users,
    }
    return render(request, 'administration/admin_dashboard.html', context)


@login_required
def stats_attendance(request):
    """API endpoint for attendance statistics"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get last 7 days attendance
    today = timezone.now().date()
    stats = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        total = Attendance.objects.filter(date=date).count()
        present = Attendance.objects.filter(date=date, status='present').count()
        rate = round((present / total * 100), 1) if total > 0 else 0
        
        stats.append({
            'date': date.strftime('%a'),  # Mon, Tue, etc.
            'rate': rate,
            'present': present,
            'total': total
        })
    
    # Today's breakdown
    today_total = Attendance.objects.filter(date=today).count()
    today_present = Attendance.objects.filter(date=today, status='present').count()
    today_absent = today_total - today_present
    
    return JsonResponse({
        'weekly_trend': stats,
        'today': {
            'present': today_present,
            'absent': today_absent,
            'total': today_total,
            'rate': round((today_present / today_total * 100), 1) if today_total > 0 else 0
        }
    })


@login_required
def stats_performance(request):
    """API endpoint for performance statistics by subject"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get average grade per subject (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    subject_stats = Grade.objects.filter(
        date__gte=thirty_days_ago
    ).values('subject__name').annotate(
        avg_grade=Avg('value'),
        count=Count('id')
    ).order_by('-avg_grade')
    
    subjects = []
    averages = []
    counts = []
    
    for stat in subject_stats:
        subjects.append(_(stat['subject__name']))
        averages.append(round(stat['avg_grade'], 2))
        counts.append(stat['count'])
    
    return JsonResponse({
        'subjects': subjects,
        'averages': averages,
        'counts': counts
    })


@login_required
def stats_top_students(request):
    """API endpoint for top performing students"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get top 10 students by average grade (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    top_students = Grade.objects.filter(
        date__gte=thirty_days_ago
    ).values(
        'student__id',
        'student__first_name',
        'student__last_name'
    ).annotate(
        avg_grade=Avg('value'),
        count=Count('id')
    ).order_by('-avg_grade')[:10]
    
    students = []
    for student in top_students:
        students.append({
            'name': f"{student['student__first_name']} {student['student__last_name']}",
            'average': round(student['avg_grade'], 2),
            'grades_count': student['count']
        })
    
    return JsonResponse({'top_students': students})


@login_required
def stats_struggling_students(request):
    """API endpoint for struggling students (avg < 3.0)"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get students with average < 3.0 (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    struggling = Grade.objects.filter(
        date__gte=thirty_days_ago
    ).values(
        'student__id',
        'student__first_name',
        'student__last_name',
        'student__student_class__name'
    ).annotate(
        avg_grade=Avg('value'),
        count=Count('id')
    ).filter(avg_grade__lt=3.0).order_by('avg_grade')[:20]
    
    students = []
    for student in struggling:
        students.append({
            'name': f"{student['student__first_name']} {student['student__last_name']}",
            'class': student['student__student_class__name'] or _('N/A'),
            'average': round(student['avg_grade'], 2),
            'grades_count': student['count']
        })
    
    return JsonResponse({'struggling_students': students})


# ========== EXISTING VIEWS ==========

@login_required
def room_list(request):
    rooms = Room.objects.all()
    
    # Simple search/filter
    room_type = request.GET.get('type')
    if room_type:
        rooms = rooms.filter(room_type=room_type)
        
    context = {
        'rooms': rooms,
        'selected_type': room_type,
        'today': timezone.now().date()
    }
    return render(request, 'administration/room_list.html', context)

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Get bookings for this room (filter by date if provided, else today)
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
        
    bookings = room.bookings.filter(date=selected_date).order_by('start_time')
    
    context = {
        'room': room,
        'bookings': bookings,
        'selected_date': selected_date
    }
    return render(request, 'administration/room_detail.html', context)

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        purpose = request.POST.get('purpose')
        
        try:
            booking = RoomBooking(
                room=room,
                teacher=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time,
                purpose=purpose
            )
            booking.full_clean() # Run validation logic (includes conflict check)
            booking.save()
            messages.success(request, "Xona muvaffaqiyatli band qilindi!")
            return redirect('room_detail', room_id=room.id)
        except Exception as e:
            messages.error(request, f"Xatolik: {e}")
            
    return redirect('room_detail', room_id=room.id)

@login_required
def quarter_report(request):
    if not (request.user.is_superuser or request.user.role in ['admin', 'director', 'teacher']):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    
    selected_class_id = request.GET.get('class')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    export = request.GET.get('export')
    
    report_data = []
    selected_class = None
    
    if selected_class_id:
        selected_class = get_object_or_404(Class, id=selected_class_id)
        students = selected_class.students.all().order_by('last_name', 'first_name')
        
        for student in students:
            student_data = {'student': student, 'grades': {}}
            for subject in subjects:
                grades_qs = Grade.objects.filter(student=student, subject=subject)
                if start_date and end_date:
                    grades_qs = grades_qs.filter(date__range=[start_date, end_date])
                
                avg_grade = grades_qs.aggregate(Avg('value'))['value__avg']
                student_data['grades'][subject.id] = round(avg_grade, 1) if avg_grade else '-'
            
            report_data.append(student_data)

        # Export logic
        if export == 'excel':
            data_for_export = []
            for item in report_data:
                row = {'O\'quvchi': item['student'].get_full_name()}
                for subject in subjects:
                    row[subject.name] = item['grades'].get(subject.id, '-')
                data_for_export.append(row)
            
            df = pd.DataFrame(data_for_export)
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="Quarter_Report_{selected_class.name}.xlsx"'
            df.to_excel(response, index=False)
            return response

    context = {
        'classes': classes,
        'subjects': subjects,
        'selected_class': selected_class,
        'report_data': report_data,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'administration/quarter_report.html', context)


# ========== USER MANAGEMENT VIEWS ==========

@login_required
def user_list(request):
    """List all users with search and filter - support both HTML and JSON"""
    if not is_admin_user(request.user):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    from django.apps import apps
    UserModel = apps.get_model(settings.AUTH_USER_MODEL)
    
    # Get all users
    users = UserModel.objects.all().order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        users_data = [{
            'id': u.id,
            'username': u.username,
            'full_name': u.get_full_name() or u.username,
            'initials': f"{u.first_name[0] if u.first_name else ''}{u.last_name[0] if u.last_name else ''}".upper() or u.username[0].upper(),
            'email': u.email,
            'phone': u.phone or '',
            'role': u.role,
            'role_display': u.get_role_display(),
            'is_active': u.is_active,
            'date_joined': u.date_joined.strftime('%d.%m.%Y'),
            'student_class': u.student_class.name if u.student_class else None
        } for u in users]
        
        return JsonResponse({'users': users_data, 'total': users.count()})
    
    # Pagination for HTML
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    classes = Class.objects.all()
    
    context = {
        'users': users_page,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'classes': classes,
        'total_users': users.count(),
    }
    return render(request, 'administration/user_list.html', context)


@login_required
def user_create(request):
    """Create new user - support both HTML and JSON"""
    if not is_admin_user(request.user):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f"Foydalanuvchi {user.username} muvaffaqiyatli yaratildi!",
                    'user_id': user.id
                })
            
            messages.success(request, f"Foydalanuvchi {user.username} muvaffaqiyatli yaratildi!")
            return redirect('user_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
                return JsonResponse({'success': False, 'message': 'Formada xatolar bor', 'errors': errors})
    else:
        form = UserCreateForm()
    
    context = {'form': form}
    return render(request, 'administration/user_form.html', context)


@login_required
def user_edit(request, user_id):
    """Edit existing user"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    from django.apps import apps
    UserModel = apps.get_model(settings.AUTH_USER_MODEL)
    user = get_object_or_404(UserModel, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Foydalanuvchi {user.username} tahrirlandi!")
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    
    context = {'form': form, 'edit_user': user}
    return render(request, 'administration/user_form.html', context)


@login_required
def user_delete(request, user_id):
    """Delete user - support both HTML and JSON"""
    if not is_admin_user(request.user):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    from django.apps import apps
    UserModel = apps.get_model(settings.AUTH_USER_MODEL)
    user = get_object_or_404(UserModel, id=user_id)
    
    # Prevent deleting yourself
    if user.id == request.user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': "O'zingizni o'chira olmaysiz!"})
        messages.error(request, "O'zingizni o'chira olmaysiz!")
        return redirect('user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f"Foydalanuvchi {username} o'chirildi!"})
        
        messages.success(request, f"Foydalanuvchi {username} o'chirildi!")
        return redirect('user_list')
    
    context = {'delete_user': user}
    return render(request, 'administration/user_delete_confirm.html', context)


@login_required
def user_bulk_action(request):
    """Bulk actions for users (delete, change role, etc.)"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
    import json
    data = json.loads(request.body)
    action = data.get('action')
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return JsonResponse({'error': 'No users selected'}, status=400)
    
    from django.apps import apps
    UserModel = apps.get_model(settings.AUTH_USER_MODEL)
    
    if action == 'delete':
        # Prevent deleting yourself
        if request.user.id in user_ids:
            return JsonResponse({'error': 'Cannot delete yourself'}, status=400)
        
        count = UserModel.objects.filter(id__in=user_ids).delete()[0]
        return JsonResponse({'success': True, 'message': f'{count} foydalanuvchi o\'chirildi'})
    
    elif action == 'activate':
        count = UserModel.objects.filter(id__in=user_ids).update(is_active=True)
        return JsonResponse({'success': True, 'message': f'{count} foydalanuvchi faollashtirildi'})
    
    elif action == 'deactivate':
        # Prevent deactivating yourself
        if request.user.id in user_ids:
            return JsonResponse({'error': 'Cannot deactivate yourself'}, status=400)
        
        count = UserModel.objects.filter(id__in=user_ids).update(is_active=False)
        return JsonResponse({'success': True, 'message': f'{count} foydalanuvchi o\'chirildi'})
    
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)


# ========== CLASS & SUBJECT MANAGEMENT VIEWS ==========

@login_required
def class_list(request):
    """List all classes"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    classes = Class.objects.all().order_by('name')
    
    # Add student count for each class
    from django.apps import apps
    UserModel = apps.get_model(settings.AUTH_USER_MODEL)
    
    class_data = []
    for cls in classes:
        student_count = UserModel.objects.filter(student_class=cls, role='student').count()
        class_data.append({
            'class': cls,
            'student_count': student_count
        })
    
    context = {'class_data': class_data}
    return render(request, 'administration/class_list.html', context)


@login_required
def class_create(request):
    """Create new class"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            cls = form.save()
            messages.success(request, f"Sinf {cls.name} muvaffaqiyatli yaratildi!")
            return redirect('class_list')
    else:
        form = ClassForm()
    
    context = {'form': form}
    return render(request, 'administration/class_form.html', context)


@login_required
def class_edit(request, class_id):
    """Edit existing class"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    cls = get_object_or_404(Class, id=class_id)
    
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=cls)
        if form.is_valid():
            form.save()
            messages.success(request, f"Sinf {cls.name} tahrirlandi!")
            return redirect('class_list')
    else:
        form = ClassForm(instance=cls)
    
    context = {'form': form, 'edit_class': cls}
    return render(request, 'administration/class_form.html', context)


@login_required
def class_delete(request, class_id):
    """Delete class"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    cls = get_object_or_404(Class, id=class_id)
    
    if request.method == 'POST':
        class_name = cls.name
        cls.delete()
        messages.success(request, f"Sinf {class_name} o'chirildi!")
        return redirect('class_list')
    
    context = {'delete_class': cls}
    return render(request, 'administration/class_delete_confirm.html', context)


@login_required
def class_students(request, class_id):
    """Manage students in a class"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    cls = get_object_or_404(Class, id=class_id)
    
    from django.apps import apps
    UserModel = apps.get_model(settings.AUTH_USER_MODEL)
    
    # Get students in this class
    students = UserModel.objects.filter(student_class=cls, role='student').order_by('last_name', 'first_name')
    
    # Get students not in any class
    unassigned_students = UserModel.objects.filter(student_class__isnull=True, role='student').order_by('last_name', 'first_name')
    
    context = {
        'class': cls,
        'students': students,
        'unassigned_students': unassigned_students
    }
    return render(request, 'administration/class_students.html', context)


@login_required
def subject_list(request):
    """List all subjects"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    subjects = Subject.objects.all().order_by('name')
    context = {'subjects': subjects}
    return render(request, 'administration/subject_list.html', context)


@login_required
def subject_create(request):
    """Create new subject"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"Fan {subject.name} muvaffaqiyatli yaratildi!")
            return redirect('subject_list')
    else:
        form = SubjectForm()
    
    context = {'form': form}
    return render(request, 'administration/subject_form.html', context)


@login_required
def subject_edit(request, subject_id):
    """Edit existing subject"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, f"Fan {subject.name} tahrirlandi!")
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    
    context = {'form': form, 'edit_subject': subject}
    return render(request, 'administration/subject_form.html', context)


@login_required
def subject_delete(request, subject_id):
    """Delete subject"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        subject_name = subject.name
        subject.delete()
        messages.success(request, f"Fan {subject_name} o'chirildi!")
        return redirect('subject_list')
    
    context = {'delete_subject': subject}
    return render(request, 'administration/subject_delete_confirm.html', context)

# ========== GRADE & ATTENDANCE MANAGEMENT VIEWS ==========

@login_required
def grade_list(request):
    """List and filter grades"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    grades = Grade.objects.all().order_by('-date')
    
    # Filtering
    class_id = request.GET.get('class')
    subject_id = request.GET.get('subject')
    student_name = request.GET.get('student')
    
    if class_id:
        grades = grades.filter(student__student_class_id=class_id)
    if subject_id:
        grades = grades.filter(subject_id=subject_id)
    if student_name:
        grades = grades.filter(
            Q(student__first_name__icontains=student_name) | 
            Q(student__last_name__icontains=student_name)
        )
    
    # Pagination
    paginator = Paginator(grades, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'grades': page_obj,
        'classes': Class.objects.all(),
        'subjects': Subject.objects.all(),
        'selected_class': class_id,
        'selected_subject': subject_id,
        'student_query': student_name
    }
    return render(request, 'administration/grade_list.html', context)


@login_required
def attendance_list(request):
    """List and filter attendance records"""
    if not is_admin_user(request.user):
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('home')
    
    attendance = Attendance.objects.all().order_by('-date')
    
    # Filtering
    class_id = request.GET.get('class')
    date_filter = request.GET.get('date')
    status_filter = request.GET.get('status')
    
    if class_id:
        attendance = attendance.filter(student__student_class_id=class_id)
    if date_filter:
        attendance = attendance.filter(date=date_filter)
    if status_filter:
        attendance = attendance.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(attendance, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'attendance': page_obj,
        'classes': Class.objects.all(),
        'selected_class': class_id,
        'selected_date': date_filter,
        'selected_status': status_filter
    }
    return render(request, 'administration/attendance_list.html', context)


@login_required
def grade_delete(request, grade_id):
    """Delete a grade record"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    grade = get_object_or_404(Grade, id=grade_id)
    grade.delete()
    return JsonResponse({'success': True, 'message': 'Baho o\'chirildi'})


@login_required
def attendance_update(request, attendance_id):
    """Update attendance status via AJAX"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    attendance = get_object_or_404(Attendance, id=attendance_id)
    status = request.POST.get('status')
    if status in ['present', 'absent', 'late']:
        attendance.status = status
        attendance.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid status'}, status=400)


# Shop Management Views

@login_required
def shop_rewards_list(request):
    """List all rewards"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    rewards = Reward.objects.all().order_by('-is_active', 'cost')
    data = [{
        'id': r.id,
        'name': r.name,
        'description': r.description,
        'cost': r.cost,
        'is_active': r.is_active
    } for r in rewards]
    
    return JsonResponse({'rewards': data})

@login_required
@require_POST
def shop_reward_create(request):
    """Create new reward"""
    if not is_admin_user(request.user):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    try:
        name = request.POST.get('name')
        description = request.POST.get('description')
        cost = int(request.POST.get('cost', 0))
        is_active = request.POST.get('is_active') == 'on'
        
        Reward.objects.create(
            name=name,
            description=description,
            cost=cost,
            is_active=is_active
        )
        return JsonResponse({'success': True, 'message': 'Mahsulot yaratildi'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def shop_reward_update(request, reward_id):
    """Update existing reward"""
    if not is_admin_user(request.user):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    try:
        reward = get_object_or_404(Reward, id=reward_id)
        reward.name = request.POST.get('name')
        reward.description = request.POST.get('description')
        reward.cost = int(request.POST.get('cost', 0))
        reward.is_active = request.POST.get('is_active') == 'on'
        reward.save()
        
        return JsonResponse({'success': True, 'message': 'Mahsulot yangilandi'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def shop_reward_delete(request, reward_id):
    """Delete reward"""
    if not is_admin_user(request.user):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    try:
        reward = get_object_or_404(Reward, id=reward_id)
        reward.delete()
        return JsonResponse({'success': True, 'message': "Mahsulot o'chirildi"})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def shop_redemptions_list(request):
    """List all redemptions"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    redemptions = Redemption.objects.select_related('user', 'reward').order_by('-created_at')
    
    data = [{
        'id': r.id,
        'student_name': r.user.get_full_name(),
        'student_username': r.user.username,
        'reward_name': r.reward.name,
        'reward_cost': r.reward.cost,
        'status': r.status,
        'status_display': r.get_status_display(),
        'created_at': r.created_at.strftime('%d.%m.%Y %H:%M')
    } for r in redemptions]
    
    return JsonResponse({'redemptions': data})

@login_required
@require_POST
def shop_redemption_process(request, redemption_id):
    """Approve or reject redemption"""
    if not is_admin_user(request.user):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        status = data.get('status')
        
        redemption = get_object_or_404(Redemption, id=redemption_id)
        
        if status == 'approved':
            redemption.status = 'approved'
            redemption.processed_at = timezone.now()
            redemption.save()
            return JsonResponse({'success': True, 'message': "So'rov tasdiqlandi"})
            
        elif status == 'rejected':
            # Refund points
            PointTransaction.objects.create(
                user=redemption.user,
                amount=redemption.reward.cost,
                transaction_type='manual',
                description=f"Qaytarildi: {redemption.reward.name} (Rad etildi)"
            )
            
            redemption.status = 'rejected'
            redemption.processed_at = timezone.now()
            redemption.save()
            return JsonResponse({'success': True, 'message': "So'rov rad etildi va ballar qaytarildi"})
            
        return JsonResponse({'success': False, 'message': 'Invalid status'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# Dashboard Stats API Views

@login_required
def api_attendance_stats(request):
    """Get attendance statistics for charts"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    today = timezone.now().date()
    # Weekly trend
    weekly_trend = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        total = Attendance.objects.filter(date=date).count()
        present = Attendance.objects.filter(date=date, status='present').count()
        rate = round((present / total * 100), 1) if total > 0 else 0
        weekly_trend.append({
            'date': date.strftime('%d.%m'),
            'rate': rate
        })
    
    # Today's stats
    total_today = Attendance.objects.filter(date=today).count()
    present_today = Attendance.objects.filter(date=today, status='present').count()
    absent_today = Attendance.objects.filter(date=today, status='absent').count()
    late_today = Attendance.objects.filter(date=today, status='late').count()
    
    return JsonResponse({
        'weekly_trend': weekly_trend,
        'today': {
            'present': present_today,
            'absent': absent_today,
            'late': late_today,
            'total': total_today
        }
    })

@login_required
def api_performance_stats(request):
    """Get performance statistics by subject"""
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    subjects = Subject.objects.annotate(avg_grade=Avg('grade__value')).order_by('-avg_grade')
    
    data = {
        'subjects': [s.name for s in subjects],
        'averages': [round(s.avg_grade, 2) if s.avg_grade else 0 for s in subjects]
    }
    
    return JsonResponse(data)

@login_required
def api_top_students(request):
    """Get top performing students"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Simplified logic: Get students with highest average grades
    # In a real app, this should be optimized
    students = User.objects.filter(role='student').annotate(
        avg_grade=Avg('student_grades__value'),
        grades_count=Count('student_grades')
    ).filter(grades_count__gt=0).order_by('-avg_grade')[:5]
    
    data = [{
        'name': s.get_full_name(),
        'average': round(s.avg_grade, 2),
        'grades_count': s.grades_count
    } for s in students]
    
    return JsonResponse({'top_students': data})

@login_required
def api_struggling_students(request):
    """Get struggling students (avg < 3)"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not is_admin_user(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    students = User.objects.filter(role='student').annotate(
        avg_grade=Avg('student_grades__value'),
        grades_count=Count('student_grades')
    ).filter(grades_count__gt=0, avg_grade__lt=3.0).order_by('avg_grade')[:5]
    
    data = [{
        'name': s.get_full_name(),
        'class': str(s.student_class) if hasattr(s, 'student_class') else 'N/A',
        'average': round(s.avg_grade, 2),
        'grades_count': s.grades_count
    } for s in students]
    
    return JsonResponse({'struggling_students': data})


