from dataclasses import dataclass, field
from typing import List, Dict, Any
from .vacancy import Vacancy

@dataclass
class VacancyMatch(Vacancy):
    score: float = 0.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            vacancy_id=int(data.get("id", data.get("vacancy_id", 0))),
            target_role=str(data.get("target_role", "Не указано")),
            job_title=str(data.get("job_title", "Не указано")),
            experience=str(data.get("experience", "Не указано")),
            grade=str(data.get("grade", "Не указано")),
            skills_vac=str(data.get("skills", "Не указано")),
            vacancy_text=str(data.get("vacancy_text", "Не указано")),
            salary=str(data.get("salary", "Не указано")),
            score=float(data.get("score", 0.0))
        )

@dataclass
class MatchResult:
    resume_id: int = 0
    matches: List[VacancyMatch] = field(default_factory=list)
    status: str = "success"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "resume_id": self.resume_id,
            "matches": [m.to_dict() for m in self.matches],
            "status": self.status,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MatchResult":
        matches = [VacancyMatch.from_dict(m) for m in data.get("matches", [])]
        return cls(
            resume_id=int(data.get("resume_id", 0)),
            matches=matches,
            status=str(data.get("status", "success")),
        )