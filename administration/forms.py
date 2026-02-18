from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from core.models import Class, Subject

User = get_user_model()


class UserCreateForm(UserCreationForm):
    """Form for creating new users"""
    first_name = forms.CharField(max_length=150, required=True, label="Ism")
    last_name = forms.CharField(max_length=150, required=True, label="Familiya")
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=20, required=False, label="Telefon")
    role = forms.ChoiceField(
        choices=[
            ('student', 'O\'quvchi'),
            ('teacher', 'O\'qituvchi'),
            ('parent', 'Ota-ona'),
            ('vice_director', 'Direktor o\'rinbosari'),
            ('director', 'Direktor'),
            ('admin', 'Admin'),
        ],
        required=True,
        label="Rol"
    )
    student_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        required=False,
        label="Sinf",
        help_text="Faqat o'quvchilar uchun"
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'student_class', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in ['password1', 'password2']:
                field.widget.attrs['placeholder'] = '••••••••'


class UserEditForm(forms.ModelForm):
    """Form for editing existing users"""
    first_name = forms.CharField(max_length=150, required=True, label="Ism")
    last_name = forms.CharField(max_length=150, required=True, label="Familiya")
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=20, required=False, label="Telefon")
    role = forms.ChoiceField(
        choices=[
            ('student', 'O\'quvchi'),
            ('teacher', 'O\'qituvchi'),
            ('parent', 'Ota-ona'),
            ('vice_director', 'Direktor o\'rinbosari'),
            ('director', 'Direktor'),
            ('admin', 'Admin'),
        ],
        required=True,
        label="Rol"
    )
    student_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        required=False,
        label="Sinf",
        help_text="Faqat o'quvchilar uchun"
    )
    is_active = forms.BooleanField(required=False, label="Faol")
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'student_class', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name == 'is_active':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class ClassForm(forms.ModelForm):
    """Form for creating/editing classes"""
    class Meta:
        model = Class
        fields = ['name', 'school']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SubjectForm(forms.ModelForm):
    """Form for creating/editing subjects"""
    class Meta:
        model = Subject
        fields = ['name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


from .models import TeacherAssignment

class TeacherAssignmentForm(forms.ModelForm):
    """Form for assigning subjects and classes to teachers"""
    class Meta:
        model = TeacherAssignment
        fields = ['teacher', 'subject', 'assigned_class']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select'
