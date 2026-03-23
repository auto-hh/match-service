from typing import List, Dict
from models import BiEncoder, CrossEncoder
from lib import bm25_search

class Retriever:
    def __init__(
        self,
        bi_encoder: BiEncoder,
        cross_encoder: CrossEncoder,
        store: Dict,
        retrieval_top_k: int = 100,
        final_top_k: int = 10,
        min_score: float = 0.0,
        bm25_weight: float = 0.3,
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

        self.bm25 = store.get("bm25")
        self.bm25_weight = bm25_weight
    
    def search(self, query: str) -> List[Dict]:
        bi_results = self._search(query)
        bm25_results = self._bm25_search(query)

        hybrid_results = self._combine_results(bi_results, bm25_results)
        
        if not hybrid_results:
            return []
                
        ce_results = self._rerank(query, hybrid_results)
        final_results = ce_results[:self.final_top_k]
        
        return final_results
    
    def _search(self, query: str) -> Dict[int, Dict]:
        query_emb = self.bi_encoder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        distances, indices = self.index.search(query_emb, self.retrieval_top_k)
        
        candidates = {}
        for idx, dist in zip(indices[0], distances[0]):
            if dist < self.min_score:
                continue
            
            vac_id = int(self.vacancy_ids[idx])
            meta = self.vacancy_meta[idx] if self.vacancy_meta else {}
            text = self.vacancy_texts[idx] if self.vacancy_texts is not None else ""
            
            candidates[int(idx)] = {
                "idx": int(idx),
                "vacancy_id": vac_id,
                "score": float(dist),
                "text": text,
                "target_role": meta.get("target_role", ""),
                "grade": meta.get("grade", ""),
                "title": meta.get("title", ""),
                "company": meta.get("company", ""),
            }
                
        return candidates

    def _bm25_search(self, query: str) -> List[Dict]:
        bm25_results = bm25_search(self.bm25, query, top_k=self.retrieval_top_k)

        results = {}
        for idx, score in bm25_results:
            if score > 0:
                results[idx] = {
                    "idx": idx,
                    "vacancy_id": int(self.vacancy_ids[idx]),
                    "score": score,
                    "dense_score": 0.0,
                    "bm25_score": float(score),
                }
        return results

    def _combine_results(self, dense: Dict, bm25: Dict) -> List[Dict]:
        all_indices = set(dense.keys()) | set(bm25.keys())

        combined = []
        for idx in all_indices:
            d_score = dense.get(idx, {}).get("dense_score", 0.0)
            b_score = bm25.get(idx, {}).get("bm25_score", 0.0)

            hybrid_score = (1 - self.bm25_weight) * d_score + self.bm25_weight * b_score

            if hybrid_score >= self.min_score:
                combined.append({
                    "idx": idx,
                    "vacancy_id": int(self.vacancy_ids[idx]),
                    "score": hybrid_score,
                    "dense_score": d_score,
                    "bm25_score": b_score,
                    "text": self.vacancy_texts[idx] if self.vacancy_texts else "",
                    "target_role": self.vacancy_meta[idx].get("target_role", "") if self.vacancy_meta else "",
                    "grade": self.vacancy_meta[idx].get("grade", "") if self.vacancy_meta else "",
                    "title": self.vacancy_meta[idx].get("title", "") if self.vacancy_meta else "",
                    "company": self.vacancy_meta[idx].get("company", "") if self.vacancy_meta else "",
                })

        combined.sort(key=lambda x: x["score"], reverse=True)
        return combined
    
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
