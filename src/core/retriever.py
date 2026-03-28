from typing import List, Dict
from schemas import Resume, Vacancy
from models import BiEncoder, CrossEncoder
from lib import bm25_search, format_resume, format_vacancy, apply_softmax
from collections import defaultdict

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
    
    def search(self, resume: Resume) -> List[Dict]:        
        query = format_resume(resume)
        if not query or not query.strip():
            return []
            
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
        
        
        import sys
        print(f"[DEBUG] query_emb type: {type(query_emb)}", file=sys.stderr)
        print(f"[DEBUG] query_emb shape: {query_emb.shape}", file=sys.stderr)
        print(f"[DEBUG] query_emb ndim: {query_emb.ndim}", file=sys.stderr)
        print(f"[DEBUG] FAISS index.d: {self.index.d}", file=sys.stderr)
        sys.stderr.flush()
        
        distances, indices = self.index.search(query_emb, self.retrieval_top_k)
        
        candidates = []
        for idx, dist in zip(indices[0], distances[0]):
            if dist < self.min_score:
                continue
            
            meta = self.vacancy_meta[idx] if self.vacancy_meta else {}            
            candidates.append(meta)
                
        return candidates

    def _bm25_search(self, query: str) -> List[Dict]:
        bm25_results = bm25_search(self.bm25, query, top_k=self.retrieval_top_k)

        results = [{
            **self.vacancy_meta[idx],
            "score": score,
        } for idx, score in bm25_results if score > 0]
        
        return results

    def _combine_results(self, dense: List[Dict], bm25: List[Dict], k: int = 60) -> List[Dict]:
        rrf_scores = defaultdict(float)
        
        for rank, item in enumerate(dense, start=1):
            link = item.get('link')
            if link:
                rrf_scores[link] += 1.0 / (k + rank)
        
        for rank, item in enumerate(bm25, start=1):
            link = item.get('link')
            if link:
                rrf_scores[link] += 1.0 / (k + rank)

        all_items = {item.get('link'): item for item in dense if item.get('link')}
        all_items.update({item.get('link'): item for item in bm25 if item.get('link')})
        
        combined = []
        for link, score in rrf_scores.items():
            if score < self.min_score:
                continue
                
            source = all_items.get(link, {})
            
            combined.append({
                "job_title": source.get("job_title"),
                "city": source.get("city", ""),
                "salary": source.get("salary", ""),
                "body": source.get("body", ""),
                "link": link,
                "score": score,
            })
        
        combined.sort(key=lambda x: x["score"], reverse=True)
           
        return [{
            "job_title": data.get("job_title"),
            "city": data.get("city"),
            "salary": data.get("salary"),
            "body": source.get("body", ""),
            "link": data.get("link"),
        } for data in combined]
    
    def _rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:        
        vacancies = [format_vacancy(Vacancy.from_dict(c)) for c in candidates]
        
        if not vacancies:
            return []
        
        ce_scores = self.cross_encoder.get_scores(query, vacancies)        
        ce_scores = apply_softmax(ce_scores)
        
        for candidate, score in zip(candidates, ce_scores):
            if score >= self.min_score:
                candidate["score"] = score
        
        return sorted(candidates, key=lambda x: x["score"], reverse=True)
