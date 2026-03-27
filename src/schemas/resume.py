from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any

class Resume(BaseModel):
    resume_id: int = 0
    grade: str = "Не указано"
    job_title: str = "Не указано"
    location: str = "Не указано"
    salary_val: Optional[int] = None
    salary_curr: str = "RUB"
    skills_res: str = "Не указано"
    about_me: str = "Не указано"
    exp_count: int = 0
    exp_text: str = "Не указано"
    edu_uni: str = "Не указано"
    edu_year: Optional[str] = None
    
    # Для совместимости с вашим кодом (в Pydantic v2 это model_dump)
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
    
    # Валидатор для обработки дублирующихся полей (resume_id / vacancy_id)
    @field_validator("resume_id", mode="before")
    @classmethod
    def parse_resume_id(cls, value):
        # Если пришло vacancy_id вместо resume_id
        if value is None or value == 0:
            return 0
        return int(value)
    
    # Валидатор для salary_val (может прийти строка или None)
    @field_validator("salary_val", mode="before")
    @classmethod
    def parse_salary_val(cls, value):
        if value is None or value == "" or value == "Не указано":
            return None
        return int(value)
    
    # Валидатор для edu_year (может прийти числом или строкой)
    @field_validator("edu_year", mode="before")
    @classmethod
    def parse_edu_year(cls, value):
        if value is None or value == "" or value == "Не указано":
            return None
        return str(value)