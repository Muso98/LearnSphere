from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import School, Subject, Class

@admin.register(School)
class SchoolAdmin(TranslationAdmin):
    list_display = ('name',)

@admin.register(Subject)
class SubjectAdmin(TranslationAdmin):
    list_display = ('name',)

@admin.register(Class)
class ClassAdmin(TranslationAdmin):
    list_display = ('name',)
