from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from core.models import School, Class, Subject, Schedule
from journal.models import Grade, GradeAudit
from django.utils import timezone
import datetime

class GradeConstraintTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.school = School.objects.create(name="Test School", address="Address")
        self.class_9a = Class.objects.create(name="9-A", school=self.school)
        self.class_10b = Class.objects.create(name="10-B", school=self.school)
        self.subject_math = Subject.objects.create(name="Math")
        self.subject_history = Subject.objects.create(name="History")
        
        # Teacher who teaches Math to 9-A
        self.teacher = User.objects.create_user(username='teacher', password='password123', role='teacher')
        Schedule.objects.create(
            class_obj=self.class_9a,
            subject=self.subject_math,
            teacher=self.teacher,
            room="101",
            day_of_week="monday",
            start_time="09:00",
            end_time="10:00"
        )
        
        # Teacher 2 (no schedule)
        self.teacher2 = User.objects.create_user(username='teacher2', password='password123', role='teacher')

        # Student in 9-A
        self.student = User.objects.create_user(username='student', password='password123', role='student', student_class=self.class_9a)
        
    def test_grade_success_with_schedule(self):
        self.client.login(username='teacher', password='password123')
        response = self.client.post(reverse('gradebook') + f'?class_id={self.class_9a.id}&subject_id={self.subject_math.id}', {
            'student_id': self.student.id,
            'grade_value': 5,
            'date': timezone.now().date()
        })
        # Expect 302 redirect (success)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Grade.objects.filter(student=self.student, value=5).exists())
        self.assertTrue(GradeAudit.objects.filter(action='create', new_value=5, changed_by=self.teacher).exists())

    def test_grade_fail_without_schedule(self):
        self.client.login(username='teacher', password='password123')
        # Try to grade History (teacher doesn't teach History)
        response = self.client.post(reverse('gradebook') + f'?class_id={self.class_9a.id}&subject_id={self.subject_history.id}', {
            'student_id': self.student.id,
            'grade_value': 4,
            'date': timezone.now().date()
        })
        # Should be blocked. The view implementation redirects or shows error.
        # My implementation redirects to 'gradebook' on error.
        self.assertEqual(response.status_code, 302)
        # Verify grade was NOT created
        self.assertFalse(Grade.objects.filter(student=self.student, subject=self.subject_history).exists())

    def test_audit_update(self):
        # Initial grade
        grade = Grade.objects.create(
            student=self.student, 
            subject=self.subject_math, 
            teacher=self.teacher, 
            value=4, 
            date=timezone.now().date()
        )
        
        self.client.login(username='teacher', password='password123')
        # Update grade via bulk save (which my implementation handles)
        response = self.client.post(reverse('gradebook') + f'?class_id={self.class_9a.id}&subject_id={self.subject_math.id}', {
            'bulk_save': 'true',
            'date': timezone.now().date(),
            f'grade_{self.student.id}': 5,
            f'comment_{self.student.id}': 'Improved'
        })
        
        grade.refresh_from_db()
        self.assertEqual(grade.value, 5)
        
        # Check Audit
        audit = GradeAudit.objects.filter(grade=grade, action='update').last()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.previous_value, 4)
        self.assertEqual(audit.new_value, 5)
        self.assertEqual(audit.changed_by, self.teacher)
