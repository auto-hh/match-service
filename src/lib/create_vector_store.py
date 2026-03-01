import faiss
import json
import numpy as np
from pathlib import Path
from lib import load_dataset, format_vacancy


def create_vector_store(model, input_path: str, output_path: str):
    print("📦 Создание FAISS индекса...")
    
    df = load_dataset(input_path)
    
    texts = [format_vacancy(row) for _, row in df.iterrows()]
    print(f"✅ Текстов: {len(texts):,}")
    
    print("🔢 Векторизация...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    print(f"✅ Эмбеддинги: {embeddings.shape}")
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype('float32'))
    print(f"✅ Индекс: {index.ntotal:,} векторов")
    
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    faiss.write_index(index, str(output_path / "vacancy_index.faiss"))
    
    np.save(str(output_path / "vacancy_ids.npy"), df['id'].values)
    
    meta_cols = [col for col in ['id', 'target_role', 'experience', 'grade'] if col in df.columns]
    if meta_cols:
        metadata = df[meta_cols].to_dict('records')
        with open(output_path / "vacancy_meta.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    np.save(str(output_path / "vacancy_texts.npy"), np.array(texts, dtype=object))
    print(f"✅ Тексты сохранены: {len(texts)}")
    
    print(f"✅ Сохранено в: {output_path}")
    return index