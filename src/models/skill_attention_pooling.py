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
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # 1. Сохраняем веса модели
        torch.save(self.state_dict(), path / "pytorch_model.bin")
        
        # 2. Сохраняем конфиг
        config = self.get_config_dict()
        with open(path / "config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        # 3. Сохраняем modules.json (для SentenceTransformers)
        modules_json = [
            {
                "idx": 0,
                "name": "pooling",
                "path": ".",
                "type": "models.SkillAttentionPooling"
            }
        ]
        with open(path / "modules.json", "w", encoding="utf-8") as f:
            json.dump(modules_json, f, indent=2)
        
        print(f"✅ Модель сохранена в: {path}")
        
    @classmethod
    def load(cls, path: str, **kwargs):
        """Загружает модель из директории."""
        path = Path(path)
        
        # 1. Загружаем конфиг
        with open(path / "config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 2. Создаём модель
        model = cls(word_embedding_dimension=config["word_embedding_dimension"])
        
        # 3. Загружаем веса
        model.load_state_dict(
            torch.load(path / "pytorch_model.bin", map_location="cpu", weights_only=True)
        )
        
        print(f"✅ Модель загружена из: {path}")
        return model