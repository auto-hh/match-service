from dataclasses import dataclass

@dataclass
class CoverLetterResult:
    vacancy_id: int
    job_title: str
    letter: str
    status: str = "success"
    mode: str = "api"