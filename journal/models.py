from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import Subject
from django.db.models.signals import post_save
from django.dispatch import receiver

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

class Grade(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grades')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_grades', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateField()
    comment = models.TextField(blank=True, null=True, help_text="O'qituvchi izohi")
    
    # Flexible metadata for future features (AI feedback, skill tags, learning path)
    metadata = models.JSONField(default=dict, blank=True, help_text="AI feedback, skill tags, o'rganish yo'li")
    
    class Meta:
        unique_together = ['student', 'subject', 'date']
    
    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.value}"

# Notification Signal Logic directly here or in signals.py
# User asked: "Django Signals-dan foydalanib, yangi baho qo'yilganda 'Notification' yaratish logikasini yoz."
# I will implement it here for simplicity or separate it. Best practice is signals.py but usually imported in apps.py ready()
# I'll put it in signals.py as per plan, but for now I'll just write models here.
