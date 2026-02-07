from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from journal.models import Grade

@login_required
def profile_view(request):
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.bio = request.POST.get('bio', user.bio)
        user.phone = request.POST.get('phone', user.phone)
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, "Profil muvaffaqiyatli yangilandi!")
        return redirect('profile')
    
    # Get additional context based on role
    context = {'user': request.user}
    
    if request.user.role == 'parent':
        context['children'] = request.user.children.all()
    
    return render(request, 'core/profile.html', context)
