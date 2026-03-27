from typing import List, Dict, Optional
from sentence_transformers import CrossEncoder as CrEnc

class CrossEncoder:
    def __init__(self, model_name: str, device: str):
        print(f"🔄 Загрузка Cross-Encoder {model_name} на {device}")
        self.model = CrEnc(model_name, device=device)
        print("✅ Cross-Encoder готов!")

    def get_scores(self, query: str, documents: List[str], top_k: Optional[int] = None) -> List[float]:
        pairs = [[query, doc] for doc in documents]
        scores = self.model.predict(pairs)
        
        scores = list(map(float, scores))
        scores = scores[:len(documents)]

        if top_k is not None:
            scores = scores[:top_k]

        return scores