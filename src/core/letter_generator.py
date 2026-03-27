from typing import Optional
from openai import OpenAI
from lib import format_resume, format_vacancy
from schemas import CoverLetterResult, Vacancy, Resume


class LetterGenerator:    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):       
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API key is required")
        
        self.base_url = base_url
        if not self.base_url:
            raise ValueError("base url is required")
        
        self.model = model
        if not self.model:
            raise ValueError("model is required")
        
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def generate(
        self,
        resume: Resume,
        vacancy: Vacancy,
    ) -> CoverLetterResult:
        prompt = self._build_prompt(resume, vacancy)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты — профессиональный карьерный консультант. "
                            "Пишешь краткие, персонализированные сопроводительные письма "
                            "без шаблонных фраз. Отвечай только текстом письма, без пояснений."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            letter = response.choices[0].message.content.strip()
            
            return CoverLetterResult(
                job_title=vacancy.job_title,
                letter=letter,
                status="success",
            )
            
        except Exception as e:
            return CoverLetterResult(
                job_title=vacancy.job_title,
                letter=f"Ошибка генерации: {str(e)}",
                status="error",
            )
    
    def _build_prompt(self, resume: Resume, vacancy: Vacancy) -> str:
        """Создаёт промпт для LLM из структурированных данных."""
        
        formatted_resume = format_resume(resume)
        formatted_vacancy = format_vacancy(vacancy)
        
        return f"""Сгенерируй сопроводительное письмо от кандидата на вакансию.

Требования:
1. Объём: 150–250 слов
2. Тон: профессиональный, но живой
3. Подчеркни соответствие между навыками кандидата и требованиями
4. Упомяни 2–3 конкретных достижения из опыта
5. Без шаблонных фраз вроде "прошу рассмотреть мою кандидатуру"
6. Язык: русский

=== ВАКАНСИЯ ===
{formatted_vacancy}

=== РЕЗЮМЕ КАНДИДАТА ===
{formatted_resume}

=== СОПРОВОДИТЕЛЬНОЕ ПИСЬМО (только текст, без пояснений) ===
"""
