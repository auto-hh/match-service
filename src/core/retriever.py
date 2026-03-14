from typing import List, Dict
from models import BiEncoder, CrossEncoder

class Retriever:
    def __init__(
        self,
        bi_encoder: BiEncoder,
        cross_encoder: CrossEncoder,
        store: Dict,
        retrieval_top_k: int = 100,
        final_top_k: int = 10,
        min_score: float = 0.0,
    ):
        self.bi_encoder = bi_encoder
        self.cross_encoder = cross_encoder
        self.store = store
        self.retrieval_top_k = retrieval_top_k
        self.final_top_k = final_top_k
        self.min_score = min_score
        
        self.index = store["index"]
        self.vacancy_ids = store["vacancy_ids"]
        self.vacancy_meta = store.get("vacancy_meta")
        self.vacancy_texts = store.get("vacancy_texts")
    
    def search(self, query: str) -> List[Dict]:
        bi_results = self._search(query)
        
        if not bi_results:
            return []
                
        ce_results = self._rerank(query, bi_results)        
        final_results = ce_results[:self.final_top_k]
        
        return final_results
    
    def _search(self, query: str) -> List[Dict]:        
        query_emb = self.bi_encoder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        distances, indices = self.index.search(query_emb, self.retrieval_top_k)
        
        candidates = []
        for idx, dist in zip(indices[0], distances[0]):
            if dist < self.min_score:
                continue
            
            vac_id = int(self.vacancy_ids[idx])
            meta = self.vacancy_meta[idx] if self.vacancy_meta else {}
            text = self.vacancy_texts[idx] if self.vacancy_texts is not None else ""
            
            candidates.append({
                "idx": int(idx),
                "vacancy_id": vac_id,
                "score": float(dist),
                "text": text,
                "target_role": meta.get("target_role", ""),
                "grade": meta.get("grade", ""),
                "title": meta.get("title", ""),
                "company": meta.get("company", ""),
            })
                
        return candidates
    
    def _rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:        
        vacancies = [c.get("text") for c in candidates]
        
        if not vacancies:
            return []
        
        ce_scores = self.cross_encoder.rerank(query, vacancies)        
        
        for c, stats in zip(candidates, ce_scores):
            c["score"] = float(stats["score"])
        
        candidates = [c for c in candidates if c["score"] >= self.min_score] 
        # TODO: Проверить, что после реранкинга score не может быть отрицательным
        return sorted(candidates, key=lambda x: x["score"], reverse=True)
