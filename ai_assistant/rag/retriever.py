"""
Context Retriever for AI Agents
Retrieves relevant data from LearnSphere database for context-aware AI responses
"""
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from core.models import Subject
from journal.models import Grade, Attendance
from analytics.models import SkillMap
from resources.models import Resource


class ContextRetriever:
    """Retrieve context from database for AI agents"""
    
    def __init__(self, user):
        self.user = user
    
    def get_student_grades(self, student_id=None, subject_id=None, days=30):
        """
        Get student grades for specified period
        
        Args:
            student_id: Specific student (None = all accessible students)
            subject_id: Specific subject (None = all subjects)
            days: Number of days to look back
        
        Returns:
            List of grade dictionaries with student, subject, value, date, comment
        """
        since_date = timezone.now() - timedelta(days=days)
        grades = Grade.objects.filter(date__gte=since_date)
        
        # Filter by student if specified
        if student_id:
            grades = grades.filter(student_id=student_id)
        elif hasattr(self.user, 'student'):
            # If user is student, only their grades
            grades = grades.filter(student=self.user.student)
        elif hasattr(self.user, 'parent'):
            # If user is parent, only their children's grades
            children = self.user.parent.children.all()
            grades = grades.filter(student__in=children)
        
        # Filter by subject if specified
        if subject_id:
            grades = grades.filter(subject_id=subject_id)
        
        return list(grades.select_related('student', 'subject', 'teacher').values(
            'id', 'student__first_name', 'student__last_name', 
            'subject__name', 'value', 'date', 'comment',
            'teacher__first_name', 'teacher__last_name'
        ))
    
    def get_student_performance_summary(self, student_id):
        """
        Get performance summary for a student
        
        Returns:
            Dictionary with average grades per subject, attendance rate, etc.
        """
        User = settings.AUTH_USER_MODEL
        from django.apps import apps
        UserModel = apps.get_model(User)
        student = UserModel.objects.get(id=student_id)
        
        # Average grades per subject (last 30 days)
        since_date = timezone.now() - timedelta(days=30)
        subject_averages = Grade.objects.filter(
            student=student,
            date__gte=since_date
        ).values('subject__name').annotate(
            avg_grade=Avg('value'),
            count=Count('id')
        )
        
        # Attendance rate (last 30 days)
        total_days = Attendance.objects.filter(
            student=student,
            date__gte=since_date
        ).count()
        
        present_days = Attendance.objects.filter(
            student=student,
            date__gte=since_date,
            status='present'
        ).count()
        
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        return {
            'student_name': student.get_full_name(),
            'class_name': student.student_class.name if student.student_class else 'N/A',
            'subject_averages': list(subject_averages),
            'attendance_rate': round(attendance_rate, 1),
            'total_days': total_days,
            'present_days': present_days
        }
    
    def get_struggling_students(self, class_id=None, subject_id=None, threshold=3.0):
        """
        Find students with average grade below threshold
        
        Args:
            class_id: Filter by class
            subject_id: Filter by subject
            threshold: Grade threshold (default 3.0)
        
        Returns:
            List of students with low performance
        """
        since_date = timezone.now() - timedelta(days=30)
        
        # Build query
        grades = Grade.objects.filter(date__gte=since_date)
        
        if class_id:
            grades = grades.filter(student__student_class_id=class_id)
        
        if subject_id:
            grades = grades.filter(subject_id=subject_id)
        
        # Get students with average below threshold
        struggling = grades.values(
            'student__id',
            'student__first_name',
            'student__last_name',
            'student__student_class__name'
        ).annotate(
            avg_grade=Avg('value'),
            grade_count=Count('id')
        ).filter(avg_grade__lt=threshold).order_by('avg_grade')
        
        return list(struggling)
    
    def get_student_skill_map(self, student_id):
        """Get AI-generated skill map for student"""
        try:
            skill_map = SkillMap.objects.get(student_id=student_id)
            return {
                'critical_thinking': skill_map.critical_thinking,
                'creativity': skill_map.creativity,
                'communication': skill_map.communication,
                'teamwork': skill_map.teamwork,
                'adaptive_learning': skill_map.adaptive_learning,
                'generated_at': skill_map.generated_at
            }
        except SkillMap.DoesNotExist:
            return None
    
    def get_recommended_resources(self, subject_name=None, limit=5):
        """Get recommended learning resources"""
        resources = Resource.objects.filter(is_approved=True)
        
        if subject_name:
            resources = resources.filter(
                Q(title__icontains=subject_name) | 
                Q(description__icontains=subject_name)
            )
        
        return list(resources.values(
            'id', 'title', 'description', 'resource_type', 
            'file', 'url', 'uploaded_at'
        )[:limit])
    
    def get_class_schedule(self, class_id):
        """Get class schedule (placeholder - implement based on your schedule model)"""
        # TODO: Implement when schedule model is available
        return {
            'class_id': class_id,
            'message': 'Schedule retrieval not yet implemented'
        }
