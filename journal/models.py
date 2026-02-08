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

class GradeAudit(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='audits')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    previous_value = models.IntegerField(null=True, blank=True)
    new_value = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20) # 'create', 'update', 'delete'

    def __str__(self):
        return f"{self.grade} - {self.action} by {self.changed_by} at {self.timestamp}"
