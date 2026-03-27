from pydantic import BaseModel, Field
from typing import Dict, Any


class CoverLetterResult(BaseModel):
    letter: str = Field(default="", description="Текст письма")
    status: str = Field(default="success", pattern="^(success|error|pending)$", description="Статус")
        
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
        return f"CoverLetterResult(letter='{self.letter}', status='{self.status}')"
