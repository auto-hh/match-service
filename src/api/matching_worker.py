from .base_worker import BaseWorker
from schemas import Resume, MatchResult
from typing import Any
from core import Matcher

class MatchingWorker(BaseWorker):
    """Воркер для быстрого матчинга резюме → вакансии"""
    def __init__(
        self,
        matcher: Matcher,
        kafka_bootstrap: str,
        input_topic: str,
        output_topic: str,
    ):
        super().__init__(
            kafka_bootstrap=kafka_bootstrap,
            input_topic=input_topic,
            output_topic=output_topic,
        )
        
        self.matcher = matcher
    
    def get_worker_name(self) -> str:
        return "⚡ MatchingWorker"
    
    def process_message(self, message: dict[str, Any]) -> MatchResult:
        resume = Resume.from_dict(message)
        result = self.matcher.match(resume)
        return result