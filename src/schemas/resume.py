from pydantic import BaseModel, Field
from typing import Dict, Any


class Resume(BaseModel):
    experience: str = Field(default="", description="Опыт работы (время)")
    job_title: str = Field(default="", description="Желаемая должность")
    grade: str = Field(default="", description="Грейд: junior/middle/senior")
    work_format: str = Field(default="", description="Формат работы: офис/удалёнка/гибрид")
    salary: str = Field(default="", description="Ожидаемая зарплата")
    city: str = Field(default="", description="Город")
    about_me: str = Field(default="", description="О себе")
    recent_jobs: str = Field(default="", description="Опыт работы")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resume':
        mapped = {
            "experience": data.get("experience", ""),
            "job_title": data.get("job_title"),
            "grade": data.get("grade", ""),
            "work_format": data.get("work_format"),
            "salary": data.get("salary", ""),
            "city": data.get("city", ""),
            "about_me": data.get("about_me"),
            "recent_jobs": data.get("recent_jobs"),
        }
        cleaned = {k: (v if v is not None else "") for k, v in mapped.items()}
        return cls(**cleaned)

    def to_dict(self) -> Dict[str, Any]:
        """Экспорт в dict"""
        return self.model_dump(exclude_none=True)

    def to_json(self, **kwargs) -> str:
        """Экспорт в JSON-строку."""
        return self.model_dump_json(**kwargs)

    def __repr__(self):
        return f"Resume(job_title='{self.job_title[:30]}...', city='{self.city}', grade='{self.grade}')"
    
