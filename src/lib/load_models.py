import torch
from models import BiEncoder, CrossEncoder
from typing import Optional

def load_bi_encoder(bi_encoder_name: str, model_path: Optional[str] = None) -> BiEncoder:
    need_attention = model_path is not None
    if model_path:
        print(f"📥 Загрузка модели из: {model_path}")
        model = BiEncoder.load_trained(model_path, bi_encoder_name, need_attention=need_attention)
    else:
        print(f"📥 Загрузка готовой модели: {bi_encoder_name}")
        model = BiEncoder.load_from_pretrained(bi_encoder_name, need_attention=need_attention)
    
    model.eval()
    if torch.cuda.is_available():
        model = model.to('cuda')
    
    return model


def load_cross_encoder(model_name: str) -> CrossEncoder:
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    return CrossEncoder(model_name, device)