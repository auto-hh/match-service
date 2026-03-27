from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # HF & Models
    hf_token: Optional[str] = None
    bi_encoder_name: str
    bi_encoder_temperature: float = 0.1
    cross_encoder: str
    faiss_path: str
    model_path: Optional[str] = None
    
    # Retrieval Params
    retrieval_top_k: int = 50
    final_top_k: int = 5
    min_score: float = 0.0
    
    # LLM
    llm_mode: Optional[str] = None
    llm_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: Optional[str] = None
    generate_letters: bool = False
        
    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()