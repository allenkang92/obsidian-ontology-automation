"""
Gemini API wrapper for text processing
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiAPI:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using Gemini API
        """
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating text: {e}")
            return ""

    async def summarize(self, text: str) -> str:
        """
        Summarize the given text
        """
        prompt = f"""다음 텍스트를 요약해주세요. 핵심 내용만 간단히 정리해주세요:

{text}"""
        return await self.generate_text(prompt)

    async def explain_concept(self, concept: str) -> str:
        """
        Explain the given concept
        """
        prompt = f"""다음 개념에 대해 자세히 설명해주세요:

{concept}"""
        return await self.generate_text(prompt)

    async def generate_questions(self, text: str) -> str:
        """
        Generate questions based on the given text
        """
        prompt = f"""다음 텍스트를 바탕으로 학습 내용을 점검할 수 있는 질문들을 생성해주세요:

{text}"""
        return await self.generate_text(prompt)

    async def extract_keywords(self, text: str) -> str:
        """
        Extract keywords from the given text
        """
        prompt = f"""다음 텍스트에서 중요한 키워드들을 추출해주세요:

{text}"""
        return await self.generate_text(prompt)

    async def expand_idea(self, idea: str) -> str:
        """
        Expand the given idea
        """
        prompt = f"""다음 아이디어나 주제에 대해 연관된 내용을 확장해서 설명해주세요:

{idea}"""
        return await self.generate_text(prompt)
