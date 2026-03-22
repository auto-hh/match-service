import faiss
import json
import numpy as np
from pathlib import Path
from lib import load_bm25_index

def load_vector_store(index_path: str, model):
    print("📥 Загрузка FAISS индекса...")
    
    index_path = Path(index_path)
    
    index = faiss.read_index(str(index_path / "vacancy_index.faiss"))
    vacancy_ids = np.load(index_path / "vacancy_ids.npy")

    bm25 = None
    bm25_path = index_path / "bm25_index.pkl"
    if bm25_path.exists():
        bm25 = load_bm25_index(str(bm25_path))
        print(f"✅ BM25 индекс загружен")
    else:
        print("⚠️ BM25 индекс не найден")
    
    vacancy_meta = None
    meta_path = index_path / "vacancy_meta.json"
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            vacancy_meta = json.load(f)
    
    vacancy_texts = None
    texts_path = index_path / "vacancy_texts.npy"
    if texts_path.exists():
        raw_texts = np.load(texts_path, allow_pickle=True)
        
        cleaned_texts = []
        for t in raw_texts:
            if isinstance(t, np.ndarray):
                text = str(t.item()) if t.size == 1 else ""
            elif isinstance(t, str):
                text = t
            elif t is None or (isinstance(t, float) and str(t) == 'nan'):
                text = ""
            else:
                text = str(t)
            
            cleaned_texts.append(text)
        
        vacancy_texts = cleaned_texts
        print(f"✅ Тексты загружены и очищены: {len(vacancy_texts)}")
    else:
        print("⚠️ vacancy_texts.npy не найден")
    
    print(f"✅ Загружено: {index.ntotal:,} векторов")
    
    return {
        "index": index,
        "vacancy_ids": vacancy_ids,
        "vacancy_meta": vacancy_meta,
        "model": model,
        "bm25": bm25,
        "vacancy_texts": vacancy_texts,
    }