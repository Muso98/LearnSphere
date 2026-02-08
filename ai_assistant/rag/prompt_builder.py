"""
Prompt Builder for AI Agents
Constructs context-aware prompts with retrieved data
"""
import json
from datetime import datetime


class PromptBuilder:
    """Build prompts for LLM with context data"""
    
    # System prompts for each agent type
    SYSTEM_PROMPTS = {
        'teacher': """You are a Teacher Assistant AI for LearnSphere, an educational management platform.

Your role:
- Analyze student performance data and identify trends
- Help teachers create intervention strategies for struggling students
- Generate draft notifications for parents about student progress
- Suggest quiz questions based on curriculum
- Provide data-driven insights

Guidelines:
- Be professional and constructive
- Focus on actionable insights
- Respect student privacy
- Use data to support recommendations
- Be encouraging about student potential

Current date: {current_date}
""",
        
        'parent': """You are a Parent Monitor AI for LearnSphere, helping parents track their children's academic progress.

Your role:
- Provide weekly progress summaries with visualizations
- Compare child's performance across subjects and over time
- Alert parents to significant grade changes
- Answer questions about school policies and schedules
- Recommend resources for additional support

Guidelines:
- Be supportive and reassuring
- Explain educational concepts in simple terms
- Highlight both strengths and areas for improvement
- Suggest practical ways parents can help
- Maintain student privacy (only show data for user's children)

Current date: {current_date}
""",
        
        'student': """You are an AI Tutor for LearnSphere, helping students learn and grow.

Your role:
- Explain concepts using the Socratic method (guiding questions)
- Help with homework WITHOUT giving direct answers
- Provide study tips based on learning patterns
- Recommend resources from the library
- Encourage critical thinking and problem-solving

Guidelines:
- NEVER give direct answers to homework problems
- Ask guiding questions to help students think through problems
- Be patient and encouraging
- Adapt explanations to student's level
- Celebrate progress and effort
- Use simple, clear language

Current date: {current_date}
"""
    }
    
    def __init__(self, agent_type):
        self.agent_type = agent_type
        self.system_prompt = self.SYSTEM_PROMPTS.get(agent_type, "").format(
            current_date=datetime.now().strftime("%Y-%m-%d")
        )
    
    def build_prompt(self, user_message, context_data=None):
        """
        Build complete prompt with system message, context, and user message
        
        Args:
            user_message: User's question/request
            context_data: Dictionary of retrieved context (grades, students, etc.)
        
        Returns:
            List of messages for LLM API
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add context if available
        if context_data:
            context_message = self._format_context(context_data)
            if context_message:
                messages.append({
                    "role": "system",
                    "content": f"CONTEXT DATA:\n{context_message}"
                })
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _format_context(self, context_data):
        """Format context data for LLM consumption"""
        formatted_parts = []
        
        # Format grades
        if 'grades' in context_data and context_data['grades']:
            formatted_parts.append("RECENT GRADES:")
            for grade in context_data['grades'][:10]:  # Limit to 10 most recent
                formatted_parts.append(
                    f"- {grade['student__first_name']} {grade['student__last_name']}: "
                    f"{grade['subject__name']} = {grade['value']} ({grade['date']})"
                    f"{' - ' + grade['comment'] if grade.get('comment') else ''}"
                )
        
        # Format performance summary
        if 'performance' in context_data:
            perf = context_data['performance']
            formatted_parts.append(f"\nPERFORMANCE SUMMARY for {perf['student_name']}:")
            formatted_parts.append(f"Class: {perf['class_name']}")
            formatted_parts.append(f"Attendance: {perf['attendance_rate']}% ({perf['present_days']}/{perf['total_days']} days)")
            
            if perf['subject_averages']:
                formatted_parts.append("Subject Averages:")
                for subj in perf['subject_averages']:
                    formatted_parts.append(
                        f"  - {subj['subject__name']}: {subj['avg_grade']:.2f} "
                        f"({subj['count']} grades)"
                    )
        
        # Format struggling students
        if 'struggling_students' in context_data and context_data['struggling_students']:
            formatted_parts.append("\nSTRUGGLING STUDENTS:")
            for student in context_data['struggling_students'][:5]:  # Top 5
                formatted_parts.append(
                    f"- {student['student__first_name']} {student['student__last_name']} "
                    f"({student['student__student_class__name']}): "
                    f"Avg {student['avg_grade']:.2f}"
                )
        
        # Format skill map
        if 'skill_map' in context_data and context_data['skill_map']:
            skills = context_data['skill_map']
            formatted_parts.append("\nSKILL MAP:")
            formatted_parts.append(f"- Critical Thinking: {skills['critical_thinking']}/100")
            formatted_parts.append(f"- Creativity: {skills['creativity']}/100")
            formatted_parts.append(f"- Communication: {skills['communication']}/100")
            formatted_parts.append(f"- Teamwork: {skills['teamwork']}/100")
            formatted_parts.append(f"- Adaptive Learning: {skills['adaptive_learning']}/100")
        
        # Format resources
        if 'resources' in context_data and context_data['resources']:
            formatted_parts.append("\nAVAILABLE RESOURCES:")
            for res in context_data['resources'][:5]:
                formatted_parts.append(
                    f"- {res['title']} ({res['resource_type']}): {res['description'][:100]}"
                )
        
        return "\n".join(formatted_parts) if formatted_parts else None
    
    def add_conversation_history(self, messages, history):
        """
        Add previous conversation messages to prompt
        
        Args:
            messages: Current messages list
            history: List of previous Message objects
        
        Returns:
            Updated messages list
        """
        # Insert history after system prompt but before current user message
        user_message = messages.pop()  # Remove current user message
        
        for msg in history[-10:]:  # Last 10 messages for context
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        messages.append(user_message)  # Add current user message back
        return messages
