from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
# from schemas import Vacancy  # Твой новый Pydantic-класс Vacancy

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


class VacancyMatch(Vacancy):
    """
    Вакансия с добавлением скоринга для матчинга.
    Наследует все поля из Vacancy: jobTitle, salary, city, body, link
    """
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Скор релевантности (0..1)")
    
    # Разрешаем дополнительные поля, если они придут извне (опционально)
    model_config = ConfigDict(extra='ignore')
    
    # === Методы совместимости (если где-то используется старый API) ===
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VacancyMatch':
        """Создаёт из dict (алиас для model_validate)."""
        return cls.model_validate(data)
    
    def to_dict(self, by_alias: bool = True) -> Dict[str, Any]:
        """Экспорт в dict (by_alias=True → camelCase для Go/JSON)."""
        return self.model_dump(by_alias=by_alias, exclude_none=True)
    
    def __repr__(self):
        # Используем alias-имена для консистентности с JSON
        d = self.to_dict(by_alias=True)
        return (f"VacancyMatch(jobTitle='{d.get('jobTitle', '')[:30]}...', "
                f"score={self.score:.4f}, city='{d.get('city', '')}')")


class MatchResult(BaseModel):
    """
    Результат матчинга резюме с вакансиями.
    """
    matches: List[VacancyMatch] = Field(default_factory=list, description="Подходящие вакансии")
    status: str = Field(default="success", description="Статус обработки")
    error: Optional[str] = Field(default=None, description="Сообщение об ошибке, если status='error'")
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MatchResult':
        return cls.model_validate(data)
    
    def to_dict(self, by_alias: bool = True, **kwargs) -> str:
        """Экспорт в JSON-строку."""
        return self.model_dump_json(by_alias=by_alias, **kwargs)
    
    def add_match(self, vacancy: Vacancy, score: float) -> 'VacancyMatch':
        """
        Добавляет вакансию в результаты с указанным скором.
        Возвращает созданный VacancyMatch для удобства.
        """
        # Создаём VacancyMatch из существующей вакансии
        vacancy_data = vacancy.to_dict(by_alias=False)  # snake_case для инициализации
        vacancy_data['score'] = score
        
        match = VacancyMatch.model_validate(vacancy_data)
        self.matches.append(match)
        return match
    
    def get_top_matches(self, n: int = 5, min_score: float = 0.0) -> List[VacancyMatch]:
        """Возвращает топ-N вакансий, отсортированных по скорам."""
        filtered = [m for m in self.matches if m.score >= min_score]
        return sorted(filtered, key=lambda x: x.score, reverse=True)[:n]
    
    @property
    def best_match(self) -> Optional[VacancyMatch]:
        """Возвращает лучшую вакансию или None, если матчей нет."""
        top = self.get_top_matches(n=1)
        return top[0] if top else None
    
    def __repr__(self):
        top = self.best_match
        best_info = f"{top.to_dict(by_alias=True).get('jobTitle', '')[:30]}... ({top.score:.3f})" if top else "None"
        return f"MatchResult(resume_id={self.resume_id}, status='{self.status}', best_match={best_info}, total={len(self.matches)})"


if __name__ == '__main__':
    vacancy = Vacancy(
        jobTitle="Python Developer",
        salary="150000 - 200000 RUB",
        city="Москва",
        body="Разработка бэкенда на FastAPI, PostgreSQL.",
        link="https://hh.ru/vacancy/12345"
    )
    
    result = MatchResult(resume_id=42)
    
    result.add_match(vacancy, score=0.87)
    
    # 4. Получаем топ-матчи
    top = result.get_top_matches(n=3, min_score=0.7)
    print(f"Найдено {len(top)} релевантных вакансий:")
    for m in top:
        print(f"  • {m.job_title} — {m.score:.3f}")
    
    print("\nJSON:")
    print(result.to_dict(by_alias=True, indent=2))
