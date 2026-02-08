from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Room(models.Model):
    ROOM_TYPES = (
        ('classroom', 'Sinf xonasi'),
        ('lab', 'Laboratoriya'),
        ('hall', 'Faollar zali'),
        ('sport', 'Sport zali'),
        ('meeting', 'Majlislar xonasi'),
    )
    
    number = models.CharField(max_length=20, verbose_name="Xona raqami/nomi")
    capacity = models.IntegerField(verbose_name="Sig'imi")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, verbose_name="Turi")
    has_projector = models.BooleanField(default=False, verbose_name="Proyektor bormi?")
    has_smartboard = models.BooleanField(default=False, verbose_name="Elektron doska bormi?")
    description = models.TextField(blank=True, verbose_name="Qo'shimcha jihozlar")
    
    def __str__(self):
        return f"{self.number} ({self.get_room_type_display()})"
    
    class Meta:
        verbose_name = "Xona"
        verbose_name_plural = "Xonalar"

class RoomBooking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', verbose_name="Xona")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='room_bookings', verbose_name="Band qiluvchi")
    date = models.DateField(verbose_name="Sana")
    start_time = models.TimeField(verbose_name="Boshlanish vaqti")
    end_time = models.TimeField(verbose_name="Tugash vaqti")
    purpose = models.CharField(max_length=255, verbose_name="Maqsad (masalan: 9-A sinf, Fizika lab)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak.")
            
        # Check for conflicts
        conflicts = RoomBooking.objects.filter(
            room=self.room,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        
        if conflicts.exists():
            raise ValidationError("Bu vaqtda xona allaqachon band qilingan.")
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room} - {self.date} ({self.start_time}-{self.end_time})"

    class Meta:
        verbose_name = "Xona Bandligi"
        verbose_name_plural = "Xona Bandliklari"
        ordering = ['-date', '-start_time']

class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_assignments', verbose_name="O'qituvchi", limit_choices_to={'role': 'teacher'})
    subject = models.ForeignKey('core.Subject', on_delete=models.CASCADE, related_name='teacher_assignments', verbose_name="Fan")
    assigned_class = models.ForeignKey('core.Class', on_delete=models.CASCADE, related_name='teacher_assignments', verbose_name="Sinf")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'subject', 'assigned_class')
        verbose_name = "O'qituvchi Biriktiruvi"
        verbose_name_plural = "O'qituvchi Biriktiruvlari"

    def __str__(self):
        return f"{self.teacher} - {self.subject} ({self.assigned_class})"
