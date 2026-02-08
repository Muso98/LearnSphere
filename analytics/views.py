from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Class
from .models import SkillMap
from .forms import SkillMapForm

@login_required
def skill_input_list(request):
    if request.user.role != 'teacher':
        messages.error(request, "Faqat o'qituvchilar kirishi mumkin.")
        return redirect('home')
        
    # Get classes where logged in user is a teacher
    # Assuming logic: teacher sees all classes or filtered by their schedule.
    # For now, list all classes for simplicity, or filter if Schedule model allows.
    classes = Class.objects.all() 
    
    return render(request, 'analytics/skill_input_list.html', {'classes': classes})

@login_required
def skill_input_detail(request, class_id):
    if request.user.role != 'teacher':
        return redirect('home')
        
    class_obj = get_object_or_404(Class, id=class_id)
    students = class_obj.students.all()
    
    context = {
        'class_obj': class_obj,
        'students': students
    }
    return render(request, 'analytics/skill_input_detail.html', context)

@login_required
def update_skills(request, student_id):
    if request.user.role != 'teacher':
        return redirect('home')
        
    # Use Get user model dynamically if needed, but here assuming relation exists
    # We need to import User properly or use get_user_model
    from django.contrib.auth import get_user_model
    User = get_user_model()
    student = get_object_or_404(User, id=student_id)
    
    skill_map, created = SkillMap.objects.get_or_create(student=student)
    
    if request.method == 'POST':
        form = SkillMapForm(request.POST, instance=skill_map)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.updated_by = request.user
            obj.save()
            messages.success(request, f"{student.get_full_name()} uchun ma'lumotlar saqlandi!")
            return redirect('skill_input_detail', class_id=student.student_class.id)
    else:
        form = SkillMapForm(instance=skill_map)
        
    return render(request, 'analytics/update_skills.html', {'form': form, 'student': student})
