
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LearnSphere.settings')
django.setup()

from gamification.models import Reward

def update_icons():
    updates = {
        'kapalak': 'bi-bug',
        'Samaliyot': 'bi-airplane-fill',
        'kitob': 'bi-book'
    }

    for name, icon in updates.items():
        try:
            reward = Reward.objects.get(name__icontains=name)
            reward.icon = icon
            reward.save()
            print(f"Updated {reward.name} to {icon}")
        except Reward.DoesNotExist:
            print(f"Reward '{name}' not found.")
        except Reward.MultipleObjectsReturned:
            print(f"Multiple rewards found for '{name}'. skipped.")

if __name__ == '__main__':
    update_icons()
