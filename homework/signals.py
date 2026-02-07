from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Assignment, Submission
from core.models import Notification
from accounts.models import User

@receiver(post_save, sender=Assignment)
def create_assignment_notification(sender, instance, created, **kwargs):
    if created:
        # Notify all students in the target class
        students = User.objects.filter(role='student', student_class=instance.target_class)
        deadline_str = instance.deadline.strftime('%d.%m.%Y %H:%M')
        message = f"Yangi vazifa: {instance.subject.name} fanidan vazifa qo'shildi. Muddat: {deadline_str}"
        
        notifications = [
            Notification(user=student, message=message)
            for student in students
        ]
        Notification.objects.bulk_create(notifications)

@receiver(post_save, sender=Submission)
def create_submission_notification(sender, instance, created, **kwargs):
    if created:
        # Notify all teachers (simplification for MVP as Assignment doesn't strictly link to one teacher)
        teachers = User.objects.filter(role='teacher')
        student_name = f"{instance.student.first_name} {instance.student.last_name}"
        message = f"Vazifa topshirildi: {student_name} {instance.assignment.subject.name} fanidan vazifa yukladi."
        
        notifications = [
            Notification(user=teacher, message=message)
            for teacher in teachers
        ]
        Notification.objects.bulk_create(notifications)
