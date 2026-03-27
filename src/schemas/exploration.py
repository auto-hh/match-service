from pydantic import BaseModel, Field
from typing import List, Dict, Any


class Token(BaseModel):
    """Токен с весом для анализа текста."""
    text: str = Field(default="", max_length=500, description="Текст токена")
    weight: float = Field(default=0.0, ge=0.0, le=1.0, description="Вес токена (0..1)")
    is_word: bool = Field(default=True, description="Является ли токен словом")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Token':
        return cls.model_validate(data)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)
    
    def __repr__(self) -> str:
        return f"Token(text={self.text!r}, weight={self.weight}, is_word={self.is_word})"


class ExplorationResult(BaseModel):
    tokens: List[Token] = Field(default_factory=list, description="Список токенов")
    status: str = Field(default="success", pattern="^(success|error|pending)$", description="Статус анализа")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExplorationResult':
        return cls.model_validate(data)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)
    
    def __repr__(self) -> str:
        tokens_preview = f"{len(self.tokens)} tokens" if self.tokens else "no tokens"
        return f"ExplorationResult(tokens={tokens_preview}, status={self.status!r})"
