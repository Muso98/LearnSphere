from django.db import models
from django.conf import settings

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class (e.g., bi-trophy)")
    points_reward = models.IntegerField(default=0, help_text="Bonus points awarded when earned")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class PointTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('grade', 'Grade Reward'),
        ('manual', 'Teacher Award'),
        ('attendance', 'Perfect Attendance'),
        ('reward_purchase', 'Shop Purchase'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='point_transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.amount} ({self.transaction_type})"

class Reward(models.Model):
    REWARD_TYPES = (
        ('physical', 'Moddiy narsa'),
        ('digital', 'Raqamli rag\'bat'),
        ('privilege', 'Imkoniyat'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.IntegerField()
    image = models.ImageField(upload_to='rewards/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=REWARD_TYPES, default='physical')
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class (e.g., bi-star)")
    
    def __str__(self):
        return self.name

class Redemption(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    is_equipped = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} redeemed {self.reward.name}"
