import os
import torch
from typing import Optional

def load_bi_encoder(bi_encoder_name: str, model_path: Optional[str] = None, temperature: float = 0.1):
    from models import BiEncoder
    
    use_lora = model_path is not None and os.path.exists(f'{model_path}/adapter')
    path = model_path or "fake-path"
    
    if model_path:
        print(f"📥 Загрузка модели из: {model_path}")
    else:
        print(f"📥 Загрузка готовой модели: {bi_encoder_name}")
    
    model = BiEncoder.load_trained(path, bi_encoder_name, use_lora=use_lora, temperature=temperature)
        
    model.eval()
    if torch.cuda.is_available():
        model = model.to('cuda')
    
    print(f"✅ Модель {bi_encoder_name} успешно загружена")
    
    return model


def load_cross_encoder(model_name: str):
    from models import CrossEncoder
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    try:
        return CrossEncoder(model_name, device)
    finally:
        print(f"✅ Модель {model_name} успешно загружена")