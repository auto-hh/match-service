import math
from typing import List

def apply_softmax(scores: List[float], temperature: float = 1.0) -> List[float]:
    if not scores:
        return []
    
    if temperature <= 0:
        raise ValueError("Temperature must be positive")
    
    scaled = [s / temperature for s in scores]
    
    max_score = max(scaled)
    exp_scores = [math.exp(s - max_score) for s in scaled]
    
    sum_exp = sum(exp_scores)
    if sum_exp == 0:
        return [1.0 / len(scores)] * len(scores)
    
    scores = [e / sum_exp for e in exp_scores]
    
    max_score = max(scores)
    if max_score == 0:
        return [0.0] * len(scores)
    
    scores = [e / max_score for e in scores]
    
    return scores
