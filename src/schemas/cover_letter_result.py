from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class CoverLetterResult(BaseModel):
    vacancy_id: int = Field(default=0, ge=0, description="ID вакансии")
    job_title: str = Field(default="", description="Название вакансии")
    letter: str = Field(default="", description="Текст письма")
    status: str = Field(default="success", pattern="^(success|error|pending)$", description="Статус")
    mode: str = Field(default="api", pattern="^(api|local|batch)$", description="Режим генерации")
    error: Optional[str] = Field(default=None, description="Ошибка, если status='error'")
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CoverLetterResult':
        """Создаёт из dict."""
        return cls.model_validate(data)
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Экспорт в dict."""
        return self.model_dump(exclude_none=exclude_none)
    
    def to_json(self, **kwargs) -> str:
        """Экспорт в JSON-строку."""
        return self.model_dump_json(**kwargs)
    
    def __repr__(self) -> str:
        return f"CoverLetterResult(vacancy_id={self.vacancy_id}, job_title='{self.job_title}', status='{self.status}')"
