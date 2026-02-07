from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('director', 'Director'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')
    
    # Relationships
    # Student specific
    student_class = models.ForeignKey('core.Class', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    
    # Parent specific
    # Using ManyToMany for Parent <-> Student relation as one parent can have multiple students
    # and one student could technically have multiple parents (Mom/Dad)
    children = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='parents')
    
    # Profile fields
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True, verbose_name="Bio")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon")
    
    # Flexible metadata for future features (AI tutor, competency mapping, etc.)
    metadata = models.JSONField(default=dict, blank=True, help_text="AI tutor preferences, kompetensiya xaritasi")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
