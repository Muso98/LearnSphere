from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # API endpoints for stats
    path('api/stats/attendance/', views.api_attendance_stats, name='api_attendance_stats'),
    path('api/stats/performance/', views.api_performance_stats, name='api_performance_stats'),
    path('api/stats/top-students/', views.api_top_students, name='api_top_students'),
    path('api/stats/struggling/', views.api_struggling_students, name='api_struggling_students'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/update/', views.user_edit, name='user_update'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # Teacher Assignment
    path('teacher-assignment/', views.teacher_assignment, name='teacher_assignment'),
    path('teacher-assignment/<int:assignment_id>/delete/', views.teacher_assignment_delete, name='teacher_assignment_delete'),
    
    # Reports
    path('reports/quarter/', views.quarter_report, name='quarter_report'),
    
    # Class Management
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create, name='class_create'),
    path('classes/<int:class_id>/update/', views.class_edit, name='class_edit'),
    path('classes/<int:class_id>/delete/', views.class_delete, name='class_delete'),
    path('classes/<int:class_id>/students/', views.class_students, name='class_students'),
    
    # Subject Management
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:subject_id>/update/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:subject_id>/delete/', views.subject_delete, name='subject_delete'),
    
    # Grade & Attendance Management
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/<int:grade_id>/delete/', views.grade_delete, name='grade_delete'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/<int:attendance_id>/update/', views.attendance_update, name='attendance_update'),
    
    # Shop Management
    path('api/shop/rewards/', views.shop_rewards_list, name='shop_rewards_list'),
    path('api/shop/rewards/create/', views.shop_reward_create, name='shop_reward_create'),
    path('api/shop/rewards/<int:reward_id>/update/', views.shop_reward_update, name='shop_reward_update'),
    path('api/shop/rewards/<int:reward_id>/delete/', views.shop_reward_delete, name='shop_reward_delete'),
    path('api/shop/redemptions/', views.shop_redemptions_list, name='shop_redemptions_list'),
    path('api/shop/redemptions/<int:redemption_id>/process/', views.shop_redemption_process, name='shop_redemption_process'),
]
