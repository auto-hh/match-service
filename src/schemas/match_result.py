from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from schemas import Vacancy

class VacancyMatch(Vacancy):
    score: float = Field(default=0.0, description="Скор релевантности (0..1)")
        
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
        return (f"VacancyMatch(job_title='{d.get('job_title', '')[:30]}...', "
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
        best_info = f"{top.to_dict(by_alias=True).get('job_title', '')[:30]}... ({top.score:.3f})" if top else "None"
        return f"MatchResult(status='{self.status}', best_match={best_info}, total={len(self.matches)})"


if __name__ == '__main__':
    vacancy = Vacancy(
        job_title="Python Developer",
        salary="150000 - 200000 RUB",
        city="Москва",
        body="Разработка бэкенда на FastAPI, PostgreSQL.",
        link="https://hh.ru/vacancy/12345"
    )
    
    result = MatchResult()
    
    result.add_match(vacancy, score=0.87)
    
    # 4. Получаем топ-матчи
    top = result.get_top_matches(n=3, min_score=0.7)
    print(f"Найдено {len(top)} релевантных вакансий:")
    for m in top:
        print(f"  • {m.job_title} — {m.score:.3f}")
    
    print("\nJSON:")
    print(result.to_dict(by_alias=True, indent=2))
