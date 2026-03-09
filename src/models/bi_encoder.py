from sentence_transformers import SentenceTransformer, models
from langchain_core.embeddings import Embeddings
from pathlib import Path
import torch
from typing import Optional, Dict, Any


class BiEncoder(SentenceTransformer):
    def __init__(self, model_name: str, need_attention: bool,
                 use_lora: bool = False, lora_config: Optional[Dict[str, Any]] = None):
        transformer = models.Transformer(model_name)
        self.embedding_dim = transformer.get_word_embedding_dimension()

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
        from peft import LoraConfig, get_peft_model, TaskType

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

    # def forward(self, features: Dict[str, torch.Tensor]):
    #     output_states = self[0](features, return_dict=True, output_attentions=True)
    #
    #     token_embeddings = output_states['token_embeddings']
    #     attention_mask = features['attention_mask']
    #     attentions = output_states.get('attentions', None)
    #
    #     if attentions is None or len(attentions) == 0:
    #         input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    #         sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    #         sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    #         sentence_embedding = sum_embeddings / sum_mask
    #     else:
    #         last_layer_attentions = attentions[-1]
    #         avg_attentions = last_layer_attentions.mean(dim=1)
    #
    #         cls_attention_weights = avg_attentions[:, 0, :]
    #         cls_attention_weights = cls_attention_weights * attention_mask
    #
    #         weights_sum = cls_attention_weights.sum(dim=1, keepdim=True) + 1e-9
    #         normalized_weights = cls_attention_weights / weights_sum
    #
    #         weighted_embeddings = token_embeddings * normalized_weights.unsqueeze(-1)
    #         sentence_embedding = weighted_embeddings.sum(dim=1)
    #
    #     return {'sentence_embedding': sentence_embedding}

    def count_trainable_parameters(self):
            return sum(p.numel() for p in self.parameters() if p.requires_grad)

    @classmethod
    def load_trained(cls, path: str, model_name: str, need_attention: bool = True, use_lora: bool = False):
        from safetensors.torch import load_file as safetensors_load
        
        path = Path(path)
        model = cls(model_name=model_name, need_attention=need_attention, use_lora=False)

        root_weights_file = path / "model.safetensors"
        if root_weights_file.exists():
            all_weights = safetensors_load(root_weights_file)
            
            transformer_weights = {}
            for k, v in all_weights.items():
                new_key = k.replace("LayerNorm.beta", "LayerNorm.bias").replace("LayerNorm.gamma", "LayerNorm.weight")
                transformer_weights[new_key] = v
            
            model[0].auto_model.load_state_dict(transformer_weights, strict=False)
        else:
            if not use_lora:
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

    def get_attention_weights(self, text: str, layer_idx: int = -1) -> Dict[str, float]:
        from transformers import AutoTokenizer

        self.eval()
        tokenizer = AutoTokenizer.from_pretrained(self[0].auto_model.name_or_path)

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        with torch.no_grad():
            peft_model = self[0].auto_model
            base_model = peft_model.base_model.model

            outputs = base_model(**inputs, output_attentions=True)

        if outputs.attentions is None:
            raise ValueError("Attention weights = None. Проверь output_attentions=True")

        attentions = outputs.attentions[layer_idx]

        avg_attention = attentions.mean(dim=1)[0]

        cls_attention = avg_attention[0, :]

        tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

        token_weights = {}
        for i, (token, weight) in enumerate(zip(tokens, cls_attention.cpu().numpy())):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                clean_token = token.replace('##', '')
                token_weights[clean_token] = float(weight)

        return token_weights