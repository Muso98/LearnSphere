"""
Parent Monitor Agent
Helps parents track their children's academic progress
"""
from .base_agent import BaseAgent


class ParentAgent(BaseAgent):
    """AI Assistant for Parents"""
    
    @property
    def agent_type(self):
        return 'parent'
    
    def process_message(self, user_message):
        """
        Process parent's request
        
        Examples:
        - "How is my child doing this week?"
        - "Compare my child's math and science performance"
        - "Show me attendance summary"
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
        
        return {
            'response': llm_response['response'],
            'tokens_used': llm_response['tokens_used'],
            'actions': []
        }
    
    def retrieve_context(self, user_message):
        """Retrieve parent-specific context"""
        context = {}
        
        # Get parent's children
        if hasattr(self.user, 'parent'):
            children = self.user.parent.children.all()
            
            if children.exists():
                # Get first child's data (or all children if multiple)
                child = children.first()
                
                # Performance summary
                context['performance'] = self.retriever.get_student_performance_summary(child.id)
                
                # Recent grades
                context['grades'] = self.retriever.get_student_grades(
                    student_id=child.id,
                    days=30
                )
                
                # Skill map
                context['skill_map'] = self.retriever.get_student_skill_map(child.id)
        
        return context
