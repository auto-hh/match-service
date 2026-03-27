from .base_worker import BaseWorker
from core import Explorer
from schemas import Resume
from typing import Any


class ExplorationWorker(BaseWorker):    
    def __init__(
        self,
        explorer: Explorer,
        kafka_bootstrap: str,
        input_topic: str,
        output_topic: str,
    ):
        super().__init__(kafka_bootstrap, input_topic, output_topic)
        self.explorer = explorer
    
    def get_worker_name(self) -> str:
        return "🔬 ExplorationWorker"
    
    def process_message(self, message: dict[str, Any]) -> dict[str, Any]:
        resume = Resume.from_dict(message)        
        result = self.explorer.analyze(resume)
        print(result)
        return result.to_dict()
