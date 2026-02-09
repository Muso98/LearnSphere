from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import PointTransaction, Reward, Redemption, UserBadge
from django.utils import timezone
from accounts.models import User

@login_required
def leaderboard(request):
    students = User.objects.filter(role='student')
    
    leaderboard_data = []
    for student in students:
        total_points = PointTransaction.objects.filter(user=student).aggregate(Sum('amount'))['amount__sum'] or 0
        badges = UserBadge.objects.filter(user=student).select_related('badge')
        
        leaderboard_data.append({
            'student': student,
            'total_points': total_points,
            'badges': badges
        })
    
    # Sort by points descending
    leaderboard_data.sort(key=lambda x: x['total_points'], reverse=True)
    
    context = {
        'leaderboard': leaderboard_data
    }
    return render(request, 'gamification/ranking.html', context)

@login_required
def rewards_shop(request):
    rewards = Reward.objects.filter(is_active=True)
    
    # Get current user's balance
    balance_info = PointTransaction.objects.filter(user=request.user).aggregate(Sum('amount'))
    user_balance = balance_info['amount__sum'] or 0
    
    context = {
        'rewards': rewards,
        'user_balance': user_balance
    }
    return render(request, 'gamification/shop.html', context)

@login_required
def redeem_reward(request, reward_id):
    if request.method != 'POST':
        return redirect('rewards_shop')
        
    reward = get_object_or_404(Reward, id=reward_id)
    
    # Check balance
    balance_info = PointTransaction.objects.filter(user=request.user).aggregate(Sum('amount'))
    user_balance = balance_info['amount__sum'] or 0
    
    if user_balance >= reward.cost:
        # Create negative transaction
        PointTransaction.objects.create(
            user=request.user,
            amount=-reward.cost,
            transaction_type='reward_purchase',
            description=f"Sotib olindi: {reward.name}"
        )
        
        # Create redemption record
        status = 'approved' if reward.type in ['digital', 'privilege'] else 'pending'
        processed_at = timezone.now() if status == 'approved' else None
        
        Redemption.objects.create(
            user=request.user,
            reward=reward,
            status=status,
            processed_at=processed_at
        )
        
        messages.success(request, f"{reward.name} muvaffaqiyatli sotib olindi!")
    else:
        messages.error(request, "Ballar yetarli emas!")
        
    return redirect('rewards_shop')

@login_required
def student_inventory(request):
    # Get approved redemptions (purchased items)
    inventory = Redemption.objects.filter(
        user=request.user
    ).select_related('reward').order_by('-created_at')
    
    return render(request, 'gamification/inventory.html', {'inventory': inventory})

@login_required
def equip_item(request, redemption_id):
    if request.method != 'POST':
        return redirect('student_inventory')
        
    item = get_object_or_404(Redemption, id=redemption_id, user=request.user, status='approved')
    
    # Unequip all other items first (ensure only one is equipped)
    Redemption.objects.filter(user=request.user, is_equipped=True).update(is_equipped=False)
    
    # Equip the selected item
    item.is_equipped = True
    item.save()
    
    messages.success(request, f"{item.reward.name} muvaffaqiyatli qadaldi!")
    return redirect('student_inventory')

@login_required
def unequip_item(request, redemption_id):
    if request.method != 'POST':
        return redirect('student_inventory')
        
    item = get_object_or_404(Redemption, id=redemption_id, user=request.user)
    item.is_equipped = False
    item.save()
    
    messages.success(request, f"{item.reward.name} olib tashlandi!")
    return redirect('student_inventory')
