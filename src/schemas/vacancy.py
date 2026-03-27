from typing import Dict, Any
from pydantic import BaseModel, Field

class Vacancy(BaseModel):
    job_title: str = Field(default="", description="Название вакансии")
    salary: str = Field(default="", description="Зарплата (от - до)")
    city: str = Field(default="", description="Город")
    body: str = Field(default="", description="Описание вакансии")
    link: str = Field(default="", description="Ссылка на вакансию")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vacancy':
        """Создаёт модель из dict (поддерживает оба стиля ключей)."""
        return cls.model_validate(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Vacancy':
        return cls.model_validate_json(json_str)
    
    def to_dict(self, by_alias: bool = True) -> Dict[str, Any]:
        return self.model_dump(by_alias=by_alias, exclude_none=True)
    
    def to_json(self, by_alias: bool = True, **kwargs) -> str:
        return self.model_dump_json(by_alias=by_alias, **kwargs)
    

if __name__ == '__main__':
    data = {
        "jobTitle": "Python Developer",
        "salary": "150000 - 200000 RUB",
        "city": "Москва",
        "body": "<p>Разработка <b>бэкенда</b> на FastAPI</p>",
        "link": "https://hh.ru/vacancy/12345"
    }
    
    vacancy = Vacancy.from_dict(data)
    
    print("Для Go (camelCase):", vacancy.to_dict(by_alias=True))