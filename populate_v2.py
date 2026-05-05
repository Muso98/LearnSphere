import os
import django
import random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LearnSphere.settings')
django.setup()

from accounts.models import User
from core.models import School, Class, Subject, Schedule
from journal.models import Grade, Attendance
from administration.models import TeacherAssignment
from django.utils import timezone
from django.core.exceptions import ValidationError

def populate():
    print("Populating comprehensive data...")

    # Names
    first_names_m = ["Aziz", "Olim", "Jasur", "Dilshod", "Anvar", "Rustam", "Farhod", "Sardor", "Botir", "Elyor"]
    first_names_f = ["Madina", "Nigora", "Dilnoza", "Shahlo", "Gulnoza", "Malika", "Sevara", "Lola", "Rayhon", "Zilola"]
    last_names = ["Rahimov", "Tursunov", "Karimov", "Aliyev", "Saidov", "Xolmatov", "Umarov", "Sodiqov", "Azimov", "Ibrohimov"]

    # Create School
    school, _ = School.objects.get_or_create(name="LearnSphere Zamonaviy Maktabi", address="Toshkent shahri, Yunusobod tumani")

    # Create Subjects
    subjects_list = [
        "Ona tili", "Matematika", "Fizika", "Kimyo", "Biologiya", 
        "Tarix", "Ingliz tili", "Geografiya", "Informatika", "Adabiyot"
    ]
    subjects = []
    for s_name in subjects_list:
        subj, _ = Subject.objects.get_or_create(name=s_name)
        subjects.append(subj)

    # Create Classes
    class_names = ["1-A", "2-B", "5-C", "9-A", "11-B"]
    classes = []
    for c_name in class_names:
        cls, _ = Class.objects.get_or_create(name=c_name, school=school)
        classes.append(cls)

    # Helper to create user
    def create_user(username, role, first_name, last_name, password="password123", **kwargs):
        email = f"{username}@learnsphere.uz"
        user, created = User.objects.get_or_create(
            username=username, 
            defaults={
                'email': email, 
                'role': role,
                'first_name': first_name,
                'last_name': last_name
            }
        )
        if created:
            user.set_password(password)
            for k, v in kwargs.items():
                setattr(user, k, v)
            user.save()
            print(f"Created {role}: {username}")
        return user

    # Create Teachers
    teachers = []
    for i in range(1, 7):
        t_fname = random.choice(first_names_m + first_names_f)
        t_lname = random.choice(last_names)
        if t_fname in first_names_f and not t_lname.endswith('a'):
            t_lname += 'a'
        teacher = create_user(f"teacher{i}", "teacher", t_fname, t_lname)
        teachers.append(teacher)
        
        # Assign subjects and classes to teachers
        # Each teacher gets 2 subjects and 2 classes
        for s in random.sample(subjects, 2):
            for c in random.sample(classes, 2):
                TeacherAssignment.objects.get_or_create(teacher=teacher, subject=s, assigned_class=c)
                
    # Create Schedule for each class
    print("Creating schedules...")
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    times = [
        ("08:30", "09:15"),
        ("09:25", "10:10"),
        ("10:20", "11:05"),
        ("11:25", "12:10"),
        ("12:20", "13:05")
    ]
    
    for cls in classes:
        # Get assignments for this class to know which teachers/subjects to use
        class_assignments = TeacherAssignment.objects.filter(assigned_class=cls)
        if not class_assignments.exists():
            continue
            
        for day in days:
            # Randomly pick 4-5 lessons for this day
            daily_lessons = random.sample(list(class_assignments), min(len(class_assignments), random.randint(4, 5)))
            for i, assignment in enumerate(daily_lessons):
                if i >= len(times): break
                start, end = times[i]
                try:
                    Schedule.objects.get_or_create(
                        class_obj=cls,
                        day_of_week=day,
                        start_time=start,
                        defaults={
                            'end_time': end,
                            'subject': assignment.subject,
                            'teacher': assignment.teacher,
                            'room': f"{random.randint(101, 305)}"
                        }
                    )
                except ValidationError:
                    # Skip conflicting schedule
                    continue

    # Create Students and Parents
    all_students = []
    for cls in classes:
        for i in range(1, 6): # 5 students per class
            s_fname = random.choice(first_names_m if i % 2 == 0 else first_names_f)
            s_lname = random.choice(last_names)
            if s_fname in first_names_f and not s_lname.endswith('a'):
                s_lname += 'a'
            
            student = create_user(f"student_{cls.name.replace('-', '').lower()}_{i}", "student", s_fname, s_lname, student_class=cls)
            all_students.append(student)
            
            # Create Parent for some students
            if i % 2 == 1:
                p_fname = random.choice(first_names_m)
                p_lname = s_lname if not s_lname.endswith('a') else s_lname[:-1]
                parent = create_user(f"parent_{student.username}", "parent", p_fname, p_lname)
                parent.children.add(student)

    # Create Grades and Attendance for the last 7 days
    today = timezone.now().date()
    for day_offset in range(7):
        date = today - timedelta(days=day_offset)
        if date.weekday() >= 5: # Skip weekends
            continue
            
        for student in all_students:
            # Attendance
            status = random.choices(['present', 'absent', 'late'], weights=[85, 10, 5])[0]
            Attendance.objects.get_or_create(student=student, date=date, defaults={'status': status})
            
            # Grades (some students get grades)
            if random.random() < 0.3:
                # Find assignments for this student's class
                assignments = TeacherAssignment.objects.filter(assigned_class=student.student_class)
                if assignments.exists():
                    assignment = random.choice(assignments)
                    Grade.objects.get_or_create(
                        student=student, 
                        subject=assignment.subject, 
                        date=date,
                        defaults={
                            'teacher': assignment.teacher,
                            'value': random.randint(3, 5),
                            'comment': random.choice(["Barakalla!", "Yaxshi", "Yana harakat qil", "Zo'r!"])
                        }
                    )

    print("Populate complete!")

if __name__ == '__main__':
    populate()
