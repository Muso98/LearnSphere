from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.views import parent_dashboard, notifications_view
from core.views_extra import student_dashboard, director_dashboard
from core.schedule_views import schedule_list, schedule_create, schedule_edit, schedule_delete
from journal.views import gradebook_view, attendance_view
from journal.export_views import export_grades_excel, export_attendance_excel, export_students_excel
from journal.import_views import download_students_template, import_students
from homework.views import create_assignment, assignment_list, submit_homework, view_submissions, grade_submission
from accounts.views import profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='base.html'), name='home'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('notifications/', notifications_view, name='notifications'),
    path('dashboard/', parent_dashboard, name='parent_dashboard'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('director/dashboard/', director_dashboard, name='director_dashboard'),
    path('gradebook/', gradebook_view, name='gradebook'),
    path('attendance/', attendance_view, name='attendance'),
    # Schedule URLs
    path('schedule/', schedule_list, name='schedule_list'),
    path('schedule/create/', schedule_create, name='schedule_create'),
    path('schedule/<int:schedule_id>/edit/', schedule_edit, name='schedule_edit'),
    path('schedule/<int:schedule_id>/delete/', schedule_delete, name='schedule_delete'),
    # Assignments
    path('assignments/create/', create_assignment, name='create_assignment'),
    path('assignments/', assignment_list, name='assignment_list'),
    path('assignments/<int:assignment_id>/submit/', submit_homework, name='submit_homework'),
    path('assignments/<int:assignment_id>/submissions/', view_submissions, name='view_submissions'),
    path('assignments/submission/<int:submission_id>/grade/', grade_submission, name='grade_submission'),
    # Excel Export URLs
    path('export/grades/', export_grades_excel, name='export_grades'),
    path('export/attendance/', export_attendance_excel, name='export_attendance'),
    path('export/students/', export_students_excel, name='export_students'),
    # Excel Import URLs
    path('import/students/', import_students, name='import_students'),
    path('import/students/template/', download_students_template, name='download_students_template'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
