from typing import List, Optional
from core import Retriever
from .letter_generator import LetterGenerator
from schemas import Resume, VacancyMatch, MatchResult
from lib import format_resume

class Matcher:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever
    
    def match(self, resume: Resume) -> MatchResult:
        results = self.retriever.search(resume)
        matches: List[VacancyMatch] = [VacancyMatch.from_dict(r) for r in results]        
        status = "success" if matches else "no_matches"
        
        return MatchResult(
            matches=matches,
            status=status,
        )
    
    def get_stats(self) -> dict:
        return {
            "total_vacancies": self.retriever.index.ntotal,
            "embedding_dim": self.retriever.index.d,
        }
