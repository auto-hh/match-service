from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ExplorationResult:
    resume_id: int
    word_weights: Dict[str, float]
    status: str = "success"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "resume_id": self.resume_id,
            "word_weights": self.word_weights,
            "status": self.status,
        }