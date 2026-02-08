from django.db import models
from django.conf import settings
from core.models import Subject

class StudentInterest(models.Model):
    """
    O'quvchining fanlarga qiziqish darajasi (AI uchun ma'lumot)
    Baholar, davomat va kutubxona foydalanishidan kelib chiqib hisoblanadi.
    """
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interests')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_interests')
    interest_score = models.IntegerField(default=0, help_text="Qiziqish darajasi (0-100)")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'subject')
        verbose_name = "O'quvchi Qiziqishi"
        verbose_name_plural = "O'quvchi Qiziqishlari"

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.interest_score}%"

class SkillMap(models.Model):
    """
    O'quvchining Soft Skills xaritasi.
    O'qituvchilar tomonidan baholanadi.
    """
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skill_map')
    
    # Soft Skills (0-100)
    critical_thinking = models.IntegerField(default=0, verbose_name="Tanqidiy fikrlash")
    creativity = models.IntegerField(default=0, verbose_name="Ijodkorlik")
    communication = models.IntegerField(default=0, verbose_name="Muloqot")
    teamwork = models.IntegerField(default=0, verbose_name="Jamoaviy ishlash")
    adaptive_learning = models.IntegerField(default=0, verbose_name="Moslashuvchanlik")
    
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='updated_skills')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Qobiliyatlar Xaritasi"
        verbose_name_plural = "Qobiliyatlar Xaritalari"

    def __str__(self):
        return f"{self.student} - Skill Map"
