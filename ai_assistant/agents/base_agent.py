"""
Base Agent Class
All AI agents inherit from this class
"""
from abc import ABC, abstractmethod
from ai_assistant.rag.retriever import ContextRetriever
from ai_assistant.rag.prompt_builder import PromptBuilder


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
        Call LLM API (placeholder - will implement with actual API)
        
        Args:
            messages: List of message dictionaries
        
        Returns:
            LLM response text
        """
        # TODO: Implement actual LLM API call (OpenAI, Claude, etc.)
        # For now, return a placeholder
        return {
            'response': "AI response placeholder - LLM API not yet integrated",
            'tokens_used': 0
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
