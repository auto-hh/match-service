from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class Resume:  
    resume_id: int = 0
    grade: str = ""
    job_title: str = ""
    location: str = ""
    salary_val: int = 0
    salary_curr: str = "RUB"
    skills_res: str = ""
    about_me: str = ""
    exp_count: int = 0
    exp_text: str = ""
    edu_uni: str = ""
    edu_year: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            resume_id=int(data.get("resume_id", data.get("vacancy_id", 0))),
            grade=str(data.get("grade", "Не указано")),
            job_title=str(data.get("job_title", "Не указано")),
            location=str(data.get("location", "Не указано")),
            salary_val=int(data["salary_val"]) if data.get("salary_val") else "Не указано",
            salary_curr=str(data.get("salary_curr", "RUB")),
            skills_res=str(data.get("skills_res", "Не указано")),
            about_me=str(data.get("about_me", "Не указано")),
            exp_count=int(data.get("exp_count", 0)),
            exp_text=str(data.get("exp_text", "Не указано")),
            edu_uni=str(data.get("edu_uni", "Не указано")),
            edu_year=int(data["edu_year"]) if data.get("edu_year") else None,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)