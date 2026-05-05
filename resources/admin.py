from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Resource, Quiz, Question, Answer

@admin.register(Resource)
class ResourceAdmin(TranslationAdmin):
    list_display = ('title', 'subject', 'resource_type')
    list_filter = ('resource_type', 'subject')

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(TranslationAdmin):
    list_display = ('title', 'subject', 'target_class', 'is_active')
    list_filter = ('subject', 'target_class', 'is_active')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(TranslationAdmin):
    list_display = ('text', 'quiz', 'points')

@admin.register(Answer)
class AnswerAdmin(TranslationAdmin):
    list_display = ('text', 'question', 'is_correct')
