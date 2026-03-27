from typing import List, Optional
from core import Retriever
from .letter_generator import LetterGenerator
from schemas import Resume, VacancyMatch, MatchResult
from lib import format_resume

class Matcher:
    def __init__(self, retriever: Retriever, generate_letters: bool = False, letter_generator: Optional[LetterGenerator] = None):
        self.retriever = retriever
        self.letter_generator = letter_generator
        self.generate_letters = generate_letters
    
    def match(self, resume: Resume) -> MatchResult:
        results = self.retriever.search(resume)
        matches: List[VacancyMatch] = [VacancyMatch.from_dict(r) for r in results]        
        status = "success" if matches else "no_matches"

        # if self.generate_letters and self.letter_generator:
        #     print('Генерирую письма...')
            
        #     resume_text = f"""
        #     {resume.about_me or ''}
        #     {resume.exp_text or ''}
        #     Навыки: {resume.skills_res or ''}
        #     """.strip()

        #     for match in matches[:final_top_k]:
        #         vacancy_data = {
        #             "vacancy_id": match.vacancy_id,
        #             "job_title": match.job_title,
        #             "skills_vac": match.skills_vac,
        #             "vacancy_text": match.vacancy_text,
        #             "salary": match.salary,
        #             "company": getattr(match, 'company', ''),
        #         }

        #         result = self.letter_generator.generate(resume_text, vacancy_data)
        #         match.cover_letter = result.letter
        
        return MatchResult(
            matches=matches,
            status=status,
        )
    
    def get_stats(self) -> dict:
        return {
            "total_vacancies": self.retriever.index.ntotal,
            "embedding_dim": self.retriever.index.d,
        }