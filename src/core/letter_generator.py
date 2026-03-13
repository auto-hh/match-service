import os
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class LLMMode(Enum):
    API = "api"
    OLLAMA = "ollama"


@dataclass
class CoverLetterResult:
    vacancy_id: int
    job_title: str
    letter: str
    status: str = "success"
    mode: str = "api"


class LetterGenerator:
    def __init__(
            self,
            mode: Optional[LLMMode] = None,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            model: Optional[str] = None,
    ):
        """
        Инициализация генератора сопроводительных писем.

        Args:
            mode: Режим работы (API или OLLAMA). Если None, определяется автоматически.
            api_key: API ключ для API режима
            base_url: URL API (Groq или Ollama)
            model: Название модели
        """
        from openai import OpenAI

        self.mode = self._detect_mode(api_key, base_url, mode)
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or "ollama"
        self.base_url = (
            base_url or 
            os.getenv("LLM_BASE_URL") or 
            ("https://api.groq.com/openai/v1" if self.mode == LLMMode.API else "http://localhost:11434/v1")
        )
        self.model = (
            model or 
            os.getenv("LLM_MODEL") or 
            ("llama-3.3-70b-versatile" if self.mode == LLMMode.API else "llama3.1:8b")
        )
        
        print(f"mode: {self.mode}")
        print(f"llm: {self.model}")
        print(f"api_url: {self.base_url}")
        print(f"api_key: {self.api_key}")
    
        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def _detect_mode(self, api_key: Optional[str], base_url: Optional[str], mode: Optional[str]) -> LLMMode:
        """Автоматически определяет доступный режим"""
        key = api_key or os.getenv("GROQ_API_KEY")
        url = base_url or os.getenv("LLM_BASE_URL")

        if mode:
            if mode == 'api':
                return LLMMode.API
            elif mode == 'ollama':
                return LLMMode.OLLAMA

        if key and (not url or "localhost" not in url):
            return LLMMode.API
        else:
            return LLMMode.OLLAMA

    def generate(
            self,
            resume_text: str,
            vacancy: dict,
            max_tokens: int = 500,
            temperature: float = 0.7,
    ) -> CoverLetterResult:
        """
        Генерирует сопроводительное письмо для пары резюме-вакансия.
        """
        prompt = self._build_prompt(resume_text, vacancy)

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты — профессиональный карьерный консультант. Пишешь краткие, персонализированные сопроводительные письма без шаблонных фраз."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            letter = response.choices[0].message.content.strip()

            return CoverLetterResult(
                vacancy_id=vacancy.get("vacancy_id", 0),
                job_title=vacancy.get("job_title", ""),
                letter=letter,
                status="success",
                mode=self.mode.value
            )

        except Exception as e:
            return CoverLetterResult(
                vacancy_id=vacancy.get("vacancy_id", 0),
                job_title=vacancy.get("job_title", ""),
                letter=f"Ошибка генерации: {str(e)}",
                status="error",
                mode=self.mode.value
            )

    def _build_prompt(self, resume_text: str, vacancy: dict) -> str:
        """Создаёт промпт для LLM"""
        job_title = vacancy.get("job_title", "Не указано")
        skills_vac = vacancy.get("skills_vac", vacancy.get("skills_csv", ""))
        vacancy_text = vacancy.get("vacancy_text", "")
        company = vacancy.get("company", "")

        prompt = f"""
Сгенерируй сопроводительное письмо от кандидата на вакансию.

Требования:
1. Объём: 150–250 слов
2. Тон: профессиональный, но живой
3. Подчеркни соответствие между навыками кандидата и требованиями
4. Упомяни 2–3 конкретных достижения из опыта
5. Без шаблонных фраз вроде "прошу рассмотреть мою кандидатуру"
6. Язык: русский

=== ВАКАНСИЯ ===
Должность: {job_title}
Компания: {company if company else "Не указана"}
Ключевые навыки: {skills_vac}
Описание:
{vacancy_text[:1500]}

=== РЕЗЮМЕ КАНДИДАТА ===
{resume_text[:1500]}

=== СОПРОВОДИТЕЛЬНОЕ ПИСЬМО (только текст, без пояснений) ===
"""    
        return prompt