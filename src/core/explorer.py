from schemas import Resume, ExplorationResult
from models import BiEncoder
from lib import format_resume

class Explorer:
    def __init__(self, bi_encoder: BiEncoder):
        self.bi_encoder = bi_encoder
    
    def analyze(self, resume: Resume) -> ExplorationResult:       
        try:            
            text = format_resume(resume.to_dict())           
            word_weights = self.bi_encoder.get_weights(text)
            
            print(f"word_weights: {word_weights}")
                        
            return ExplorationResult(
                resume_id=resume.resume_id,
                word_weights=word_weights,
                status="success",
            )
            
        except Exception as e:
            return ExplorationResult(
                resume_id=resume.resume_id,
                word_weights={},
                status="error",
            )