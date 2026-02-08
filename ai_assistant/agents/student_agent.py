"""
Student Tutor Agent
Helps students learn using Socratic method (guiding questions)
"""
from .base_agent import BaseAgent


class StudentAgent(BaseAgent):
    """AI Tutor for Students"""
    
    @property
    def agent_type(self):
        return 'student'
    
    def process_message(self, user_message):
        """
        Process student's request
        
        Examples:
        - "Help me understand quadratic equations"
        - "I don't understand photosynthesis"
        - "How do I solve this problem: 2x + 5 = 15?"
        
        IMPORTANT: Never give direct answers, use Socratic method
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
        
        # Check if we should recommend resources
        actions = self._check_resource_recommendations(user_message, context)
        
        return {
            'response': llm_response['response'],
            'tokens_used': llm_response['tokens_used'],
            'actions': actions
        }
    
    def retrieve_context(self, user_message):
        """Retrieve student-specific context"""
        context = {}
        
        # Get student's own data
        if hasattr(self.user, 'student'):
            student = self.user.student
            
            # Performance summary
            context['performance'] = self.retriever.get_student_performance_summary(student.id)
            
            # Skill map
            context['skill_map'] = self.retriever.get_student_skill_map(student.id)
        
        # Check if asking about specific subject
        message_lower = user_message.lower()
        subjects = ['math', 'english', 'science', 'history', 'physics', 'chemistry', 'biology']
        
        for subject in subjects:
            if subject in message_lower:
                # Get recommended resources for this subject
                context['resources'] = self.retriever.get_recommended_resources(
                    subject_name=subject,
                    limit=3
                )
                break
        
        return context
    
    def _check_resource_recommendations(self, user_message, context):
        """Check if we should recommend learning resources"""
        actions = []
        
        if 'resources' in context and context['resources']:
            for resource in context['resources']:
                actions.append({
                    'type': 'resource_recommended',
                    'resource_id': resource['id'],
                    'title': resource['title'],
                    'type': resource['resource_type']
                })
                
                self.log_action(
                    action_type='resource_recommended',
                    description=f"Recommended resource: {resource['title']}",
                    action_data={'resource_id': resource['id']}
                )
        
        return actions
