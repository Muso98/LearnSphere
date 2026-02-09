from django.urls import path
from . import views

urlpatterns = [
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('shop/', views.rewards_shop, name='rewards_shop'),
    path('redeem/<int:reward_id>/', views.redeem_reward, name='redeem_reward'),
    path('inventory/', views.student_inventory, name='student_inventory'),
    path('equip/<int:redemption_id>/', views.equip_item, name='equip_item'),
    path('unequip/<int:redemption_id>/', views.unequip_item, name='unequip_item'),
]
