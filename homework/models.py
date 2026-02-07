from django.db import models
from core.models import Subject, Class
from django.conf import settings
from django.utils import timezone

class Assignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    target_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assignments')
    description = models.TextField()
    file_upload = models.FileField(upload_to='assignments/', blank=True, null=True)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.subject} - {self.target_class} - {self.deadline}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hw_submissions')
    file_submission = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(default=timezone.now)
    grade = models.IntegerField(null=True, blank=True) # Optional grade 1-5
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"Submission by {self.student} for {self.assignment}"
