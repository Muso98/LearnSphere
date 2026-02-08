from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resource, Quiz, Question, Answer, QuizResult
from core.models import Subject
from django.db.models import Count, Q

# --- Resource Views ---
@login_required
def resource_list(request):
    resources = Resource.objects.all().order_by('-created_at')
    subjects = Subject.objects.all()
    
    # Filter by Subject
    subject_id = request.GET.get('subject')
    if subject_id:
        resources = resources.filter(subject_id=subject_id)
        selected_subject = int(subject_id)
    else:
        selected_subject = None
    
    # Filter by Type
    resource_type = request.GET.get('type')
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
        
    context = {
        'resources': resources,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'selected_type': resource_type
    }
    return render(request, 'resources/resource_list.html', context)

@login_required
def resource_create(request):
    # Only Teachers and Admins can upload
    if request.user.role not in ['teacher', 'admin', 'director']:
        messages.error(request, "Sizda resurs yuklash huquqi yo'q!")
        return redirect('resource_list')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        resource_type = request.POST.get('resource_type')
        description = request.POST.get('description')
        link = request.POST.get('link')
        file = request.FILES.get('file')
        
        if title and subject_id and resource_type:
            Resource.objects.create(
                title=title,
                subject_id=subject_id,
                resource_type=resource_type,
                description=description,
                link=link,
                file=file,
                uploaded_by=request.user
            )
            messages.success(request, "Resurs muvaffaqiyatli yuklandi!")
            return redirect('resource_list')
        else:
            messages.error(request, "Iltimos, barcha majburiy maydonlarni to'ldiring.")
            
    subjects = Subject.objects.all()
    return render(request, 'resources/resource_form.html', {'subjects': subjects})

# --- Quiz Views ---
@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(is_active=True).order_by('-created_at')
    subjects = Subject.objects.all()
    
    subject_id = request.GET.get('subject')
    if subject_id:
        quizzes = quizzes.filter(subject_id=subject_id)
        selected_subject = int(subject_id)
    else:
        selected_subject = None

    # Annotate with question count
    quizzes = quizzes.annotate(question_count=Count('questions'))

    context = {
        'quizzes': quizzes,
        'subjects': subjects,
        'selected_subject': selected_subject,
    }
    return render(request, 'resources/quiz_list.html', context)

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user already took this quiz
    last_result = QuizResult.objects.filter(student=request.user, quiz=quiz).order_by('-date_taken').first()
    
    context = {
        'quiz': quiz,
        'last_result': last_result
    }
    return render(request, 'resources/quiz_detail.html', context)

@login_required
def quiz_take(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Fetch questions and answers
    questions_qs = quiz.questions.all().prefetch_related('answers')
    
    # Convert to list and shuffle questions
    questions = list(questions_qs)
    import random
    random.shuffle(questions)
    
    # Shuffle answers for each question
    for question in questions:
        answers = list(question.answers.all())
        random.shuffle(answers)
        question.shuffled_answers = answers

    if request.method == 'POST':
        score = 0
        total_questions = len(questions)
        correct_answers_count = 0
        
        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                # We verify against the DB to be safe, or check the prepared list
                # Since we have the objects loaded, we can check directly if we want, 
                # but fetching the specific answer ensures validity.
                answer = Answer.objects.filter(id=selected_answer_id, question=question).first()
                if answer and answer.is_correct:
                    score += question.points
                    correct_answers_count += 1
        
        # Save result
        result = QuizResult.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers_count
        )
        
        messages.success(request, f"Test yakunlandi! Siz {score} ball to'pladingiz.")
        return redirect('quiz_result', result_id=result.id)
        
    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'resources/quiz_take.html', context)

@login_required
def quiz_result(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id, student=request.user)
    
    context = {
        'result': result,
        'percentage': (result.correct_answers / result.total_questions * 100) if result.total_questions > 0 else 0
    }
    return render(request, 'resources/quiz_result.html', context)

# --- Teacher Quiz Management ---
@login_required
def quiz_create(request):
    if request.user.role not in ['teacher', 'admin', 'director']:
        messages.error(request, "Sizda test yaratish huquqi yo'q!")
        return redirect('quiz_list')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        description = request.POST.get('description')
        time_limit = request.POST.get('time_limit', 0)
        
        if title and subject_id:
            quiz = Quiz.objects.create(
                title=title,
                subject_id=subject_id,
                description=description,
                time_limit=time_limit,
                created_by=request.user
            )
            messages.success(request, "Test yaratildi! Endi savollarni qo'shing.")
            return redirect('quiz_edit', quiz_id=quiz.id)
            
    subjects = Subject.objects.all()
    return render(request, 'resources/quiz_form.html', {'subjects': subjects})

@login_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user != quiz.created_by and request.user.role != 'admin':
        messages.error(request, "Bu testni tahrirlash huquqiga ega emassiz!")
        return redirect('quiz_list')

    if request.method == 'POST':
        if 'import_excel' in request.POST:
            import_questions_from_excel(request, quiz)
        elif 'add_question' in request.POST:
            add_manual_question(request, quiz)
            
        return redirect('quiz_edit', quiz_id=quiz.id)

    questions = quiz.questions.all().prefetch_related('answers')
    return render(request, 'resources/quiz_edit.html', {'quiz': quiz, 'questions': questions})

# Helpers
import pandas as pd

def import_questions_from_excel(request, quiz):
    excel_file = request.FILES.get('excel_file')
    if not excel_file:
        messages.error(request, "Fayl tanlanmadi!")
        return

    try:
        df = pd.read_excel(excel_file)
        # Expected columns: Question, Option A, Option B, Option C, Option D, Correct Answer (A/B/C/D)
        
        count = 0
        for index, row in df.iterrows():
            question_text = row.get('Question')
            if not question_text: continue
            
            question = Question.objects.create(quiz=quiz, text=question_text, order=quiz.questions.count()+1)
            
            options = {
                'A': row.get('Option A'),
                'B': row.get('Option B'),
                'C': row.get('Option C'),
                'D': row.get('Option D')
            }
            correct = str(row.get('Correct Answer')).strip().upper()
            
            for key, text in options.items():
                if pd.notna(text):
                    Answer.objects.create(
                        question=question,
                        text=text,
                        is_correct=(key == correct)
                    )
            count += 1
            
        messages.success(request, f"{count} ta savol muvaffaqiyatli yuklandi!")
    except Exception as e:
        messages.error(request, f"Xatolik yuz berdi: {str(e)}")

def add_manual_question(request, quiz):
    question_text = request.POST.get('question_text')
    points = request.POST.get('points', 1)
    
    if question_text:
        question = Question.objects.create(quiz=quiz, text=question_text, points=points, order=quiz.questions.count()+1)
        
        # Add 4 options
        for i in range(1, 5):
            option_text = request.POST.get(f'option_{i}')
            is_correct = request.POST.get('correct_option') == str(i)
            
            if option_text:
                Answer.objects.create(
                    question=question,
                    text=option_text,
                    is_correct=is_correct
                )
        messages.success(request, "Savol qo'shildi!")
