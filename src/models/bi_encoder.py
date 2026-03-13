from sentence_transformers import SentenceTransformer, models
from pathlib import Path
import torch
from typing import Optional, Dict, Any
from safetensors.torch import load_file as safetensors_load
from peft import LoraConfig, get_peft_model, TaskType
from transformers import AutoTokenizer
import numpy as np

class BiEncoder(SentenceTransformer):
    def __init__(self, model_name: str, use_lora: bool = False, lora_config: Optional[Dict[str, Any]] = None, temperature: float = 0.1):
        transformer = models.Transformer(model_name)
        self.embedding_dim = transformer.get_word_embedding_dimension()
        self.temperature = temperature

        pooling = models.Pooling(self.embedding_dim, pooling_mode='mean')

        transformer.name = "0_Transformer"
        pooling.name = "1_Pooling"

        super().__init__(modules=[transformer, pooling])

        if use_lora:
            self._apply_lora(lora_config)
        else:
            for param in self[0].parameters():
                param.requires_grad = False

    def _apply_lora(self, lora_config: Optional[Dict[str, Any]] = None):
        if lora_config is None:
            lora_config = {
                "r": 8,
                "lora_alpha": 32,
                "lora_dropout": 0.1,
                "target_modules": ["query", "value"],
                "bias": "none",
                "task_type": TaskType.FEATURE_EXTRACTION,
            }

        peft_config = LoraConfig(**lora_config)

        self[0].auto_model = get_peft_model(self[0].auto_model, peft_config)

        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.parameters())
        print(f"Применена LoRA. Обучаемых параметров: {trainable_params} / {total_params}")

    def count_trainable_parameters(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    @classmethod
    def load_trained(cls, path: str, model_name: str, use_lora: bool = False, temperature: float = 0.1):        
        path = Path(path)
        model = cls(model_name=model_name, use_lora=False, temperature=temperature)

        root_weights_file = path / "model.safetensors"
        if root_weights_file.exists():
            all_weights = safetensors_load(root_weights_file)
            
            transformer_weights = {}
            for k, v in all_weights.items():
                new_key = k.replace("LayerNorm.beta", "LayerNorm.bias").replace("LayerNorm.gamma", "LayerNorm.weight")
                transformer_weights[new_key] = v
            
            model[0].auto_model.load_state_dict(transformer_weights, strict=False)
        elif use_lora:
            raise FileNotFoundError(f"Не найдены веса модели: {root_weights_file}")

        if use_lora:
            adapter_path = path / "adapter"
            if adapter_path.exists():
                from peft import PeftModel
                model[0].auto_model = PeftModel.from_pretrained(model[0].auto_model, adapter_path)
                print(f"Адаптеры LoRA загружены из: {adapter_path}")
            else:
                print(f"Папка адаптеров не найдена: {adapter_path}")
        
        return model

    def get_weights(self, text: str, steps: int = 50) -> Dict[str, float]:
        from lib import merge_tokens_to_words
        
        self.eval()
        tokenizer = AutoTokenizer.from_pretrained(self[0].auto_model.name_or_path)
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        model = self[0].auto_model
        try:
            model = model.base_model.model
        except AttributeError:
            pass # No LoRA using
            
        embeddings_layer = model.embeddings.word_embeddings
        input_embeddings = embeddings_layer(inputs['input_ids'])
        baseline = torch.zeros_like(input_embeddings)

        integrated_grads = torch.zeros_like(input_embeddings)
        
        for step in range(steps + 1):
            alpha = step / steps
            interpolated = baseline + alpha * (input_embeddings - baseline)
            interpolated.requires_grad_(True)            
            outputs = model(inputs_embeds=interpolated, attention_mask=inputs['attention_mask'])
            
            cls_emb = outputs.last_hidden_state[:, 0, :]
            loss = cls_emb.norm()   
            
            grads = torch.autograd.grad(loss, interpolated)[0]
            integrated_grads += grads

        avg_grads = integrated_grads / (steps + 1)
        ig_scores = (input_embeddings - baseline) * avg_grads
        
        weights = np.abs(ig_scores.sum(dim=-1).squeeze(0).cpu().numpy())
        tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])     
        
        word_weights = merge_tokens_to_words(tokens, weights, tokenizer_type="auto")
        
        if word_weights:
            keys = list(word_weights.keys())
            vals = np.array([word_weights[k] for k in keys])
            vals = (vals - vals.max()) / self.temperature
            probs = np.exp(vals) / np.sum(np.exp(vals))
            
            max_prob = probs.max()
            if max_prob > 0:
                normalized = probs / max_prob
            else:
                normalized = probs
            
            word_weights = {k: float(v) for k, v in zip(keys, normalized)}

        return word_weights