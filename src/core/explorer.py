from schemas import Resume, ExplorationResult
from models import BiEncoder
from lib import format_resume

class Explorer:
    def __init__(self, bi_encoder: BiEncoder):
        self.bi_encoder = bi_encoder
    
    def analyze(self, resume: Resume) -> ExplorationResult:       
        try:            
            text = format_resume(resume)        
            tokens = self.bi_encoder.get_weights(text)
                                        
            return ExplorationResult(
                tokens=tokens,
                status="success",
            )
            
        except Exception as e:
            print(e)
            return ExplorationResult(
                tokens=[],
                status="error",
            )
