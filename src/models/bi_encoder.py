from sentence_transformers import SentenceTransformer, models
from langchain_core.embeddings import Embeddings
from .skill_attention_pooling import SkillAttentionPooling
from pathlib import Path
import torch

class BiEncoder(SentenceTransformer):
    def __init__(self, model_name: str, need_attention: bool):
        transformer = models.Transformer(model_name)
        self.embedding_dim = transformer.get_word_embedding_dimension()
        
        if need_attention:
            pooling = SkillAttentionPooling(word_embedding_dimension=self.embedding_dim)
        else:
            pooling = models.Pooling(self.embedding_dim, pooling_mode='mean')
        
        transformer.name = "0_Transformer"
        pooling.name = "1_SkillAttentionPooling"
        
        super().__init__(modules=[transformer, pooling])
        
        for param in self[0].parameters():
            param.requires_grad = False

    @classmethod
    def load_trained(cls, path: str, model_name: str, need_attention: bool = True):          
        from safetensors.torch import load_file as safetensors_load
        
        path = Path(path)        
        model = cls(model_name=model_name, need_attention=need_attention)
        
        root_weights_file = path / "model.safetensors"
        if root_weights_file.exists():
            all_weights = safetensors_load(root_weights_file)
            
            transformer_weights = {}
            for k, v in all_weights.items():
                new_key = k.replace("LayerNorm.beta", "LayerNorm.bias").replace("LayerNorm.gamma", "LayerNorm.weight")
                transformer_weights[new_key] = v
            
            model[0].auto_model.load_state_dict(transformer_weights)
        else:
            raise FileNotFoundError(f"Не найдены веса модели: {root_weights_file}")
        
        pooling_path = path / "1_SkillAttentionPooling"
        if pooling_path.exists():
            pooling_weights_file = pooling_path / "pytorch_model.bin"
            if pooling_weights_file.exists():
                pooling_weights = torch.load(pooling_weights_file, map_location="cpu", weights_only=True)
                model[1].load_state_dict(pooling_weights)
            else:
                raise FileNotFoundError(f"Не найдены веса pooling: {pooling_weights_file}")
        else:
            raise FileNotFoundError(f"Папка pooling не найдена: {pooling_path}")
        
        return model
