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
        
    def __repr__(self) -> str:
        return f"Token(text={self.text!r}, weight={self.weight}, is_word={self.is_word})"


@dataclass
class ExplorationResult:
    resume_id: int
    tokens: List[Token] = field(default_factory=list)
    status: str = "success"
    
    def to_dict(self) -> dict:
        return {
            "resume_id": self.resume_id,
            "tokens": [t.to_dict() for t in self.tokens],
            "status": self.status,
        }

    def __repr__(self) -> str:
        if self.tokens:
            tokens_repr = ",\n        ".join(repr(t) for t in self.tokens)
            tokens_str = f"[\n        {tokens_repr},\n    ]"
        else:
            tokens_str = "[]"
        
        return (
            f"ExplorationResult(\n"
            f"    resume_id={self.resume_id},\n"
            f"    tokens={tokens_str},\n"
            f"    status={self.status!r}\n"
            f")"
        )