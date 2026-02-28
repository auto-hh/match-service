from typing import List
from core import Retriever
from schemas import Resume, VacancyMatch, MatchResult

class Matcher:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever
    
    def match(self, resume: Resume) -> MatchResult:      
        search_text = resume.to_search_text()
        
        if not search_text or not search_text.strip():
            return MatchResult(
                resume_id=resume.resume_id,
                matches=[],
                status="no_matches",
            )
        
        results = self.retriever.search(search_text)
        
        matches: List[VacancyMatch] = [VacancyMatch.from_dict(r) for r in results]
        status = "success" if matches else "no_matches"
        
        return MatchResult(
            resume_id=resume.resume_id,
            matches=matches,
            status=status,
        )
    
    def get_stats(self) -> dict:
        return {
            "total_vacancies": self.retriever.index.ntotal,
            "embedding_dim": self.retriever.index.d,
            "top_k": self.top_k,
            "min_score": self.min_score,
        }