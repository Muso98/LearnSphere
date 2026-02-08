from django.urls import path
from . import views

urlpatterns = [
    path('skills/', views.skill_input_list, name='skill_input_list'),
    path('skills/class/<int:class_id>/', views.skill_input_detail, name='skill_input_detail'),
    path('skills/student/<int:student_id>/', views.update_skills, name='update_skills'),
]
