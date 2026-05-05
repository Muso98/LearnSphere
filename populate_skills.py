import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LearnSphere.settings')
django.setup()

from accounts.models import User
from analytics.models import SkillMap

def populate_skills():
    print("Populating SkillMaps for students...")
    students = User.objects.filter(role='student')
    
    for student in students:
        skill_map, created = SkillMap.objects.get_or_create(student=student)
        skill_map.critical_thinking = random.randint(40, 95)
        skill_map.creativity = random.randint(40, 95)
        skill_map.communication = random.randint(40, 95)
        skill_map.teamwork = random.randint(40, 95)
        skill_map.adaptive_learning = random.randint(40, 95)
        skill_map.save()
        print(f"Updated skills for {student.username}")

if __name__ == '__main__':
    populate_skills()
