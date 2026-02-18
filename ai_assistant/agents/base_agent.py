"""
Base Agent Class
All AI agents inherit from this class
"""
from abc import ABC, abstractmethod
from ai_assistant.rag.retriever import ContextRetriever
from ai_assistant.rag.prompt_builder import PromptBuilder
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, user, conversation=None):
        """
        Initialize agent
        
        Args:
            user: Django User object
            conversation: Conversation object (optional)
        """
        self.user = user
        self.conversation = conversation
        self.retriever = ContextRetriever(user)
        self.prompt_builder = PromptBuilder(self.agent_type)
    
    @property
    @abstractmethod
    def agent_type(self):
        """Return agent type ('teacher', 'parent', 'student')"""
        pass
    
    @abstractmethod
    def process_message(self, user_message):
        """
        Process user message and return AI response
        
        Args:
            user_message: User's input message
        
        Returns:
            Dictionary with 'response' and optional 'actions' performed
        """
        pass
    
    def retrieve_context(self, user_message):
        """
        Retrieve relevant context based on user message
        Override in subclasses for agent-specific context
        
        Args:
            user_message: User's input message
        
        Returns:
            Dictionary of context data
        """
        return {}
    
    def call_llm(self, messages):
        """
        Call LLM API using Google Gemini
        
        Args:
            messages: List of message dictionaries [{'role': 'user'/'assistant', 'content': '...'}]
        
        Returns:
            Dictionary with response text and usage stats
        """
        try:
            import google.generativeai as genai
            from django.conf import settings
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-flash-latest')
            
            # Format history for Gemini
            # Gemini expects [{'role': 'user'/'model', 'parts': ['...']}]
            gemini_history = []
            for msg in messages[:-1]: # Exclude last message which is the prompt
                role = 'user' if msg['role'] == 'user' else 'model'
                gemini_history.append({'role': role, 'parts': [msg['content']]})
            
            # Start chat session
            chat = model.start_chat(history=gemini_history)
            
            # Send last message
            current_message = messages[-1]['content']
            response = chat.send_message(current_message)
            
            return {
                'response': response.text,
                'tokens_used': 0 # Gemini doesn't always return token usage easily in sync mode, setting 0 for now
            }
            
        except Exception as e:
            error_msg = f"Gemini API Error: {str(e)}"
            print(error_msg)
            with open('debug_view.log', 'a') as f:
                f.write(f"{datetime.now()}: {error_msg}\n")
            
            return {
                'response': "Kechirasiz, hozircha AI xizmatida muammo bor. Iltimos keyinroq urinib ko'ring.",
                'tokens_used': 0,
                'error': str(e)
            }
    
    def log_action(self, action_type, description, action_data=None, success=True, error_message=''):
        """
        Log autonomous action performed by agent
        
        Args:
            action_type: Type of action
            description: Human-readable description
            action_data: Additional metadata (optional)
            success: Whether action succeeded
            error_message: Error message if failed
        """
        if self.conversation:
            from ai_assistant.models import AgentAction
            AgentAction.objects.create(
                conversation=self.conversation,
                action_type=action_type,
                description=description,
                action_data=action_data,
                success=success,
                error_message=error_message
            )
