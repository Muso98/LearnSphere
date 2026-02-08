"""
Teacher Assistant Agent
Helps teachers analyze student performance and create interventions
"""
from .base_agent import BaseAgent


class TeacherAgent(BaseAgent):
    """AI Assistant for Teachers"""
    
    @property
    def agent_type(self):
        return 'teacher'
    
    def process_message(self, user_message):
        """
        Process teacher's request
        
        Examples:
        - "Find students struggling in Math"
        - "Generate parent notification for low performers"
        - "Analyze 9-A class performance this month"
        """
        # Retrieve relevant context
        context = self.retrieve_context(user_message)
        
        # Build prompt with context
        messages = self.prompt_builder.build_prompt(user_message, context)
        
        # Add conversation history if available
        if self.conversation:
            history = self.conversation.messages.all()
            messages = self.prompt_builder.add_conversation_history(messages, history)
        
        # Call LLM
        llm_response = self.call_llm(messages)
        
        # Check if autonomous actions are needed
        actions_performed = self._check_and_perform_actions(user_message, context)
        
        return {
            'response': llm_response['response'],
            'tokens_used': llm_response['tokens_used'],
            'actions': actions_performed
        }
    
    def retrieve_context(self, user_message):
        """Retrieve teacher-specific context"""
        context = {}
        
        message_lower = user_message.lower()
        
        # If asking about struggling students
        if any(word in message_lower for word in ['struggling', 'low', 'poor', 'failing']):
            context['struggling_students'] = self.retriever.get_struggling_students()
        
        # If asking about specific subject
        subjects = ['math', 'english', 'science', 'history', 'physics', 'chemistry']
        for subject in subjects:
            if subject in message_lower:
                # Get recent grades for this subject
                # Note: This is simplified - in real implementation, map subject name to ID
                context['grades'] = self.retriever.get_student_grades(days=30)
                break
        
        # If asking about a class (e.g., "9-A")
        if any(char.isdigit() for char in user_message) and '-' in user_message:
            context['grades'] = self.retriever.get_student_grades(days=30)
        
        # Default: get recent grades
        if not context:
            context['grades'] = self.retriever.get_student_grades(days=7)
        
        return context
    
    def _check_and_perform_actions(self, user_message, context):
        """
        Check if message requires autonomous actions
        
        Examples:
        - "Send notification to parents" -> Draft notification
        - "Generate report" -> Create report
        """
        actions = []
        message_lower = user_message.lower()
        
        # Check for notification request
        if 'notification' in message_lower or 'notify' in message_lower:
            if 'struggling_students' in context and context['struggling_students']:
                # Draft notifications for struggling students
                for student in context['struggling_students'][:3]:  # Top 3
                    notification_draft = self._draft_parent_notification(student)
                    actions.append({
                        'type': 'notification_drafted',
                        'student': f"{student['student__first_name']} {student['student__last_name']}",
                        'draft': notification_draft
                    })
                    
                    self.log_action(
                        action_type='notification_sent',
                        description=f"Drafted notification for {student['student__first_name']} {student['student__last_name']}",
                        action_data={'draft': notification_draft}
                    )
        
        return actions
    
    def _draft_parent_notification(self, student_data):
        """Draft a notification for parents"""
        return f"""Dear Parent,

This is to inform you that {student_data['student__first_name']} {student_data['student__last_name']} 
(Class: {student_data['student__student_class__name']}) has been showing a decline in academic performance.

Current average grade: {student_data['avg_grade']:.2f}

We recommend scheduling a meeting to discuss how we can support your child's learning.

Best regards,
LearnSphere Team"""
