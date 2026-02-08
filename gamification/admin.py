from django.contrib import admin
from .models import Badge, UserBadge, PointTransaction, Reward, Redemption

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_reward', 'created_at')
    search_fields = ('name', 'description')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('badge', 'earned_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'description')

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'reward__name')
    actions = ['approve_redemption', 'reject_redemption']

    def approve_redemption(self, request, queryset):
        queryset.update(status='approved', processed_at=timezone.now())
    approve_redemption.short_description = "Tanlangan so'rovlarni tasdiqlash"

    def reject_redemption(self, request, queryset):
        # Refund points logic could be added here
        queryset.update(status='rejected', processed_at=timezone.now())
    reject_redemption.short_description = "Tanlangan so'rovlarni rad etish"
