from modeltranslation.translator import register, TranslationOptions
from .models import Resource, Quiz, Question, Answer

@register(Resource)
class ResourceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Quiz)
class QuizTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ('text',)

@register(Answer)
class AnswerTranslationOptions(TranslationOptions):
    fields = ('text',)
