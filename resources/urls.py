from django.urls import path
from . import views

urlpatterns = [
    # Resources
    path('', views.resource_list, name='resource_list'),
    path('upload/', views.resource_create, name='resource_create'),
    
    # Quizzes
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/<int:quiz_id>/take/', views.quiz_take, name='quiz_take'),
    path('quizzes/results/<int:result_id>/', views.quiz_result, name='quiz_result'),
    
    # Teacher Quiz Management
    path('quizzes/create/', views.quiz_create, name='quiz_create'),
    path('quizzes/<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
]
