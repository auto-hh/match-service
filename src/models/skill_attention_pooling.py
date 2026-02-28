import torch
import torch.nn as nn
from pathlib import Path
import json

class SkillAttentionPooling(nn.Module):
    def __init__(self, word_embedding_dimension: int):
        super().__init__()
        self.word_embedding_dimension = word_embedding_dimension
        self.attention_weights = nn.Linear(word_embedding_dimension, 1)
    
    def forward(self, features: dict) -> dict:
        token_embeddings = features['token_embeddings'] 
        attention_mask = features['attention_mask']
        
        scores = self.attention_weights(token_embeddings).squeeze(-1)
        scores = scores.masked_fill(attention_mask == 0, -1e4)
        weights = torch.softmax(scores, dim=1)
        
        sentence_embedding = torch.bmm(
            weights.unsqueeze(1),
            token_embeddings
        ).squeeze(1)
        
        features['sentence_embedding'] = sentence_embedding
        return features
    
    def get_config_dict(self):
        """Возвращает конфиг для сериализации SentenceTransformer."""
        return {
            "word_embedding_dimension": self.word_embedding_dimension,
            "_type": "SkillAttentionPooling",
        }
        
    def save(self, path: str, **kwargs):
        """Переопределяем save для корректного modules.json"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # 1. Сохраняем базовую модель
        super().save(path, **kwargs)
        
        # 2. Исправляем modules.json с правильным типом
        modules_path = path / "modules.json"
        with open(modules_path, "r", encoding="utf-8") as f:
            modules = json.load(f)
        
        # Обновляем тип для кастомного pooling
        for mod in modules:
            if "SkillAttentionPooling" in mod.get("name", ""):
                mod["type"] = "models.SkillAttentionPooling"
        
        with open(modules_path, "w", encoding="utf-8") as f:
            json.dump(modules, f, indent=2)
        
        print(f"✅ Модель сохранена в: {path}")