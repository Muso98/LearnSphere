import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LearnSphere.settings')
django.setup()

from accounts.models import User
from core.models import School, Class, Subject
from journal.models import Grade
from django.utils import timezone

def populate():
    print("Populating data...")

    # Create School
    school, _ = School.objects.get_or_create(name="Tashkent International School", address="123 Street, Tashkent")
    print(f"School: {school}")

    # Create Classes
    class_9a, _ = Class.objects.get_or_create(name="9-A", school=school)
    class_10b, _ = Class.objects.get_or_create(name="10-B", school=school)
    print("Classes created.")

    # Create Subjects
    math, _ = Subject.objects.get_or_create(name="Mathematics")
    phys, _ = Subject.objects.get_or_create(name="Physics")
    eng, _ = Subject.objects.get_or_create(name="English")
    print("Subjects created.")

    # Create Users
    def create_user(username, role, password="password123", **kwargs):
        user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com', 'role': role})
        if created:
            user.set_password(password)
            for k, v in kwargs.items():
                setattr(user, k, v)
            user.save()
            print(f"Created {role}: {username}")
        return user

    teacher = create_user("teacher1", "teacher", first_name="Aziz", last_name="Rahimov")
    
    student1 = create_user("student1", "student", student_class=class_9a, first_name="Jasur", last_name="Karimov")
    student2 = create_user("student2", "student", student_class=class_9a, first_name="Madina", last_name="Aliyeva")
    
    parent = create_user("parent1", "parent", first_name="Dilshod", last_name="Karimov")
    parent.children.add(student1)
    
    # Create Director
    create_user("director1", "director", first_name="Director", last_name="User")
    
    print("Users created.")

    # Create some grades
    if not Grade.objects.exists():
        Grade.objects.create(student=student1, subject=math, teacher=teacher, value=5, comment="Excellent work!", date=timezone.now().date())
        Grade.objects.create(student=student1, subject=eng, teacher=teacher, value=4, comment="Good", date=timezone.now().date())
        Grade.objects.create(student=student2, subject=math, teacher=teacher, value=3, comment="Needs improvement", date=timezone.now().date())
        print("Sample grades added.")

    print("Done! Login credentials:")
    print("Teacher: teacher1 / password123")
    print("Parent: parent1 / password123")
    print("Student: student1 / password123")

if __name__ == '__main__':
    populate()
