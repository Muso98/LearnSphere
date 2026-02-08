from django.urls import path
from . import views

urlpatterns = [
    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Statistics API
    path('api/stats/attendance/', views.stats_attendance, name='stats_attendance'),
    path('api/stats/performance/', views.stats_performance, name='stats_performance'),
    path('api/stats/top-students/', views.stats_top_students, name='stats_top_students'),
    path('api/stats/struggling/', views.stats_struggling_students, name='stats_struggling_students'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/bulk-action/', views.user_bulk_action, name='user_bulk_action'),
    
    # Class Management
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create, name='class_create'),
    path('classes/<int:class_id>/edit/', views.class_edit, name='class_edit'),
    path('classes/<int:class_id>/delete/', views.class_delete, name='class_delete'),
    path('classes/<int:class_id>/students/', views.class_students, name='class_students'),
    
    # Subject Management
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:subject_id>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:subject_id>/delete/', views.subject_delete, name='subject_delete'),
    
    # Teacher Assignment
    path('teachers/assign/', views.teacher_assignment, name='teacher_assignment'),
    path('teachers/assign/<int:assignment_id>/delete/', views.teacher_assignment_delete, name='teacher_assignment_delete'),
    
    # Grade & Attendance Management
    path('grades/', views.grade_list, name='admin_grade_list'),
    path('grades/<int:grade_id>/delete/', views.grade_delete, name='admin_grade_delete'),
    path('attendance/', views.attendance_list, name='admin_attendance_list'),
    path('attendance/<int:attendance_id>/update/', views.attendance_update, name='admin_attendance_update'),
    
    # Existing URLs
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/book/', views.book_room, name='book_room'),
    path('reports/quarter/', views.quarter_report, name='quarter_report'),
]
