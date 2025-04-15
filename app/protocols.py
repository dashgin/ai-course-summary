from typing import Protocol


class LLMService(Protocol):
    """Protocol for LLM service"""

    def generate_summary(self, text: str) -> str:
        """Generate a summary of the given text"""

    def generate_course_summary(self, course_description: str) -> str:
        """Generate a summary of the given course description"""
