from django.urls import path
from . import views

urlpatterns = [
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('shop/', views.rewards_shop, name='rewards_shop'),
    path('redeem/<int:reward_id>/', views.redeem_reward, name='redeem_reward'),
]
