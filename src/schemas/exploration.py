from dataclasses import dataclass, field
from typing import List


@dataclass
class Token:
    text: str
    weight: float
    is_word: bool
    
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "weight": self.weight,
            "is_word": self.is_word,
        }


@dataclass
class ExplorationResult:
    """
    Результат анализа для фронтенда.
    Готов к прямому рендерингу.
    """
    resume_id: int
    tokens: List[Token] = field(default_factory=list)
    status: str = "success"
    
    def to_dict(self) -> dict:
        return {
            "resume_id": self.resume_id,
            "tokens": [t.to_dict() for t in self.tokens],
            "status": self.status,
        }
