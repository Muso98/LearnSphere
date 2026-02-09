from django import template
from gamification.models import Redemption

register = template.Library()

@register.simple_tag
def get_equipped_item(user):
    if not user.is_authenticated:
        return None
    try:
        return Redemption.objects.filter(user=user, is_equipped=True).select_related('reward').first()
    except Exception:
        return None
