from modeltranslation.translator import register, TranslationOptions
from .models import School, Subject, Class, Schedule

@register(School)
class SchoolTranslationOptions(TranslationOptions):
    fields = ('name', 'address')

@register(Subject)
class SubjectTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Class)
class ClassTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Schedule)
class ScheduleTranslationOptions(TranslationOptions):
    fields = ('room',)
