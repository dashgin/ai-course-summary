from fastapi import HTTPException, status


class OpenAILLMService:
    """OpenAI implementation of the LLM service"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_summary(self, text: str) -> str:
        """Generate a summary using OpenAI's API"""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise, informative summaries of online courses.",
                },
                {
                    "role": "user",
                    "content": f"Summarize this online course in 2-3 sentences: {text}",
                },
            ],
            max_tokens=150,
            temperature=0.5,
        )
        return response.choices[0].message.content

    def generate_course_summary(self, course_description: str) -> str:
        """
        Generate a summary of a course description using OpenAI's GPT API.

        Args:
            course_description: The full course description to summarize
            llm_service: The LLM service to use for generating the summary

        Returns:
            A concise summary of the course description
        """
        try:
            return self.generate_summary(course_description)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate summary: {str(e)}",
            )
