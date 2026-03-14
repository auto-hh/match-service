from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class Vacancy:    
    vacancy_id: int = 0
    target_role: str = ""
    job_title: str = ""
    experience: str = ""
    grade: str = ""
    skills_vac: str = ""
    vacancy_text: str = ""
    salary: str = ""
    
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
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)