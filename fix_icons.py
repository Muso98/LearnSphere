import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LearnSphere.settings')
django.setup()

from gamification.models import Reward

def fix_icons():
    rewards = Reward.objects.all()
    count = 0
    for r in rewards:
        if r.icon and '<' in r.icon:
            # Extract class name using regex, looking for 'bi-' followed by characters
            match = re.search(r'bi-[a-z0-9-]+', r.icon)
            if match:
                old_icon = r.icon
                r.icon = match.group(0)
                r.save()
                print(f'Fixed: {old_icon} -> {r.icon}')
                count += 1
            else:
                print(f"Could not extract icon from: {r.icon}")
    print(f'Total fixed: {count}')

if __name__ == '__main__':
    fix_icons()
