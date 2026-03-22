from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple
import pickle
from pathlib import Path


def create_bm25_index(texts: List[str]) -> BM25Okapi:
    tokenized_docs = [text.lower().split() for text in texts]
    bm25 = BM25Okapi(tokenized_docs)
    return bm25


def save_bm25_index(bm25: BM25Okapi, path: str):
    with open(path, 'wb') as f:
        pickle.dump(bm25, f)


def load_bm25_index(path: str) -> BM25Okapi:
    with open(path, 'rb') as f:
        return pickle.load(f)


def bm25_search(bm25: BM25Okapi, query: str, top_k: int = 50) -> List[Tuple[int, float]]:
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    top_indices = scores.argsort()[::-1][:top_k]
    return [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]