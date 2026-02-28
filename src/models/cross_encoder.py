import torch
from typing import List, Dict, Optional
from sentence_transformers import CrossEncoder as CrEnc

class CrossEncoder:
    def __init__(self, model_name: str):
        device='cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🔄 Загрузка Cross-Encoder {model_name} на {device}")
        self.model = CrEnc(model_name, device=device)
        print("✅ Cross-Encoder готов!")

    def rerank(self, query: str, documents: List[str], top_k: Optional[int] = None) -> List[Dict]:
        pairs = [[query, doc] for doc in documents]
        scores = self.model.predict(pairs)

        results = [
            {"document": doc, "score": float(score)}
            for doc, score in zip(documents, scores)
        ]
        results.sort(key=lambda x: x["score"], reverse=True)

        if top_k is not None:
            results = results[:top_k]

        return results