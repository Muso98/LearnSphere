from django import forms
from .models import SkillMap

class SkillMapForm(forms.ModelForm):
    class Meta:
        model = SkillMap
        fields = ['critical_thinking', 'creativity', 'communication', 'teamwork', 'adaptive_learning']
        widgets = {
            'critical_thinking': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': 0, 'max': 100}),
            'creativity': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': 0, 'max': 100}),
            'communication': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': 0, 'max': 100}),
            'teamwork': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': 0, 'max': 100}),
            'adaptive_learning': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': 0, 'max': 100}),
        }
