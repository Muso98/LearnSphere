from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}: {self.message[:20]}"


class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    
    # Flexible metadata for future features (kompetensiya xaritasi, AI tutor config)
    metadata = models.JSONField(default=dict, blank=True, help_text="Kompetensiya xaritasi, AI tutor sozlamalari")

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=20) # e.g., "9-A"
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Classes"


class Schedule(models.Model):
    """Dars jadvali modeli"""
    DAY_CHOICES = [
        ('monday', 'Dushanba'),
        ('tuesday', 'Seshanba'),
        ('wednesday', 'Chorshanba'),
        ('thursday', 'Payshanba'),
        ('friday', 'Juma'),
        ('saturday', 'Shanba'),
    ]
    
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='schedules', verbose_name='Sinf')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules', verbose_name='Fan')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules', verbose_name="O'qituvchi")
    room = models.CharField(max_length=50, verbose_name='Xona')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES, verbose_name='Kun')
    start_time = models.TimeField(verbose_name='Boshlanish vaqti')
    end_time = models.TimeField(verbose_name='Tugash vaqti')
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Jadval'
        verbose_name_plural = 'Jadvallar'
    
    def __str__(self):
        return f"{self.class_obj} - {self.subject} ({self.get_day_of_week_display()} {self.start_time}-{self.end_time})"
    
    def clean(self):
        """Validate and check for conflicts"""
        from django.core.exceptions import ValidationError
        
        # Check if end_time is after start_time
        if self.end_time <= self.start_time:
            raise ValidationError("Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak!")
        
        # Check for teacher conflicts
        teacher_conflicts = Schedule.objects.filter(
            teacher=self.teacher,
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if teacher_conflicts.exists():
            conflict = teacher_conflicts.first()
            raise ValidationError(
                f"O'qituvchi {self.teacher} bu vaqtda band: {conflict.class_obj} - {conflict.subject} "
                f"({conflict.start_time}-{conflict.end_time})"
            )
        
        # Check for room conflicts
        room_conflicts = Schedule.objects.filter(
            room=self.room,
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if room_conflicts.exists():
            conflict = room_conflicts.first()
            raise ValidationError(
                f"Xona {self.room} bu vaqtda band: {conflict.class_obj} - {conflict.subject} "
                f"({conflict.start_time}-{conflict.end_time})"
            )
        
        # Check for class conflicts
        class_conflicts = Schedule.objects.filter(
            class_obj=self.class_obj,
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if class_conflicts.exists():
            conflict = class_conflicts.first()
            raise ValidationError(
                f"Sinf {self.class_obj} bu vaqtda band: {conflict.subject} ({conflict.teacher}) "
                f"({conflict.start_time}-{conflict.end_time})"
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

