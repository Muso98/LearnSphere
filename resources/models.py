from django.db import models
from django.conf import settings
from core.models import Subject, Class

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('video', 'Video Dars'),
        ('pdf', 'PDF Kitob/Qo\'llanma'),
        ('link', 'Foydali Link'),
        ('audio', 'Audio Dars'),
    )

    title = models.CharField(max_length=255, verbose_name="Mavzu")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='resources', verbose_name="Fan")
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES, verbose_name="Turi")
    
    file = models.FileField(upload_to='resources/', blank=True, null=True, verbose_name="Fayl (PDF/Audio)")
    link = models.URLField(blank=True, null=True, verbose_name="Video/Link URL")
    
    description = models.TextField(blank=True, verbose_name="Qisqacha tavsif")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Yukladi")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Target audience (optional - can be for specific class or all)
    target_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sinf uchun (ixtiyoriy)")

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
    
    class Meta:
        verbose_name = "O'quv Resursi"
        verbose_name_plural = "O'quv Resurslari"

class Quiz(models.Model):
    title = models.CharField(max_length=255, verbose_name="Test Sarlavhasi")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes', verbose_name="Fan")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    target_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sinf uchun")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Tuzuvchi")
    created_at = models.DateTimeField(auto_now_add=True)
    time_limit = models.IntegerField(default=0, verbose_name="Vaqt cheklovi (daqiqa)", help_text="0 = cheklov yo'q")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")

    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Testlar"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name="Savol matni")
    points = models.IntegerField(default=1, verbose_name="Ball")
    order = models.IntegerField(default=0, verbose_name="Tartib raqami")

    def __str__(self):
        return self.text[:50]
    
    class Meta:
        ordering = ['order']
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255, verbose_name="Javob varianti")
    is_correct = models.BooleanField(default=False, verbose_name="To'g'ri javobmi?")

    def __str__(self):
        return self.text

class QuizResult(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField(verbose_name="To'plangan ball")
    total_questions = models.IntegerField(verbose_name="Jami savollar")
    correct_answers = models.IntegerField(verbose_name="To'g'ri javoblar")
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.quiz.title}: {self.score}"
    
    class Meta:
        verbose_name = "Test Natijasi"
        verbose_name_plural = "Test Natijalari"
