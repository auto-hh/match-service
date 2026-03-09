from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from .vacancy import Vacancy

@dataclass
class VacancyMatch(Vacancy):
    score: float = 0.0
    cover_letter: str = ''
    company: str = ""

    def to_dict(self) -> Dict[str, Any]:
        base = asdict(self)
        base["score"] = self.score
        base["cover_letter"] = self.cover_letter
        base["company"] = self.company
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        text = data.get("text", data.get("vacancy_text", ""))

        job_title = data.get("title", "") or data.get("job_title", "")
        if not job_title and "ВАКАНСИЯ:" in text:
            job_title = text.split("ВАКАНСИЯ:")[1].split(".")[0].strip()
        if not job_title:
            job_title = data.get("target_role", "Не указано")

        salary = "Не указано"
        if "ЗАРПЛАТА:" in text:
            salary_part = text.split("ЗАРПЛАТА:")[1].split(".")[0].strip()
            if salary_part and salary_part != "Не указано":
                salary = salary_part

        skills_vac = ""
        if "НАВЫКИ:" in text:
            skills_part = text.split("НАВЫКИ:")[1].split(".")[0].strip()
            if skills_part and skills_part != "Не указано":
                skills_vac = skills_part

        experience = ""
        if "ОПЫТ:" in text:
            exp_part = text.split("ОПЫТ:")[1].split(".")[0].strip()
            if exp_part and exp_part != "Не указано":
                experience = exp_part

        return cls(
            vacancy_id=int(data.get("vacancy_id", data.get("id", 0))),
            target_role=str(data.get("target_role", "Не указано")),
            job_title=job_title,
            experience=experience,
            grade=str(data.get("grade", "Не указано")),
            skills_vac=skills_vac,
            vacancy_text=text,
            salary=salary,
            score=float(data.get("score", 0.0)),
            cover_letter=str(data.get("cover_letter", "")),
            company=str(data.get("company", "")),
        )

    def __repr__(self):
        return (f"VacancyMatch(id={self.vacancy_id}, job_title='{self.job_title}', score={self.score:.4f}, "
                f"salary='{self.salary}', cover_letter={self.cover_letter})")

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
    def from_dict(cls, data: Dict[str, Any]):
        matches = [VacancyMatch.from_dict(m) for m in data.get("matches", [])]
        return cls(
            resume_id=int(data.get("resume_id", 0)),
            matches=matches,
            status=str(data.get("status", "success")),
        )

    def __repr__(self):
        matches_str = ",\n  ".join(repr(m) for m in self.matches) if self.matches else "None"
        return f"MatchResult(resume_id={self.resume_id}, status='{self.status}', matches=[\n  {matches_str}\n])"