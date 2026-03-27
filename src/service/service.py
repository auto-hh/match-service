from fastapi import HTTPException, Depends, FastAPI
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

from core import Matcher, Explorer, LetterGenerator
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import HTTPException

from core import Matcher, Retriever, LetterGenerator, LLMMode, Explorer
from lib import load_vector_store, load_bi_encoder, load_cross_encoder
from config import settings, Settings
from huggingface_hub import login
import torch

_service: Optional["ResumeService"] = None

class ResumeService:
    def __init__(
        self,
        bi_encoder_name: str,
        bi_encoder_temperature: float,
        cross_encoder_model: str,
        faiss_path: str,
        retrieval_top_k: int,
        final_top_k: int,
        model_path: Optional[str] = None,
        min_score: float = 0.0,
        llm_mode: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
        generate_letters: bool = False
    ):
        self.bi_encoder_name = bi_encoder_name
        self.model_path = model_path
        
        print("Загрузка BiEncoder...")
        self.bi_encoder = load_bi_encoder(
            model_path=model_path,
            bi_encoder_name=bi_encoder_name,
            temperature=bi_encoder_temperature,
        )
        
        print("Загрузка CrossEncoder...")
        self.cross_encoder = load_cross_encoder(model_name=cross_encoder_model)
        
        print("Загрузка Vector Store...")
        self.store = load_vector_store(faiss_path, self.bi_encoder)

        self.retriever = Retriever(
            bi_encoder=self.bi_encoder,
            cross_encoder=self.cross_encoder,
            store=self.store,
            retrieval_top_k=retrieval_top_k,
            final_top_k=final_top_k,
            min_score=min_score,
        )

        if llm_mode and llm_api_key:
            print("Инициализация LLM...")
            self.letter_generator = LetterGenerator(
                mode=llm_mode,
                api_key=llm_api_key,
                base_url=llm_base_url,
                model=llm_model,
            )
        else:
            self.letter_generator = None
        
        self.explorer = Explorer(bi_encoder=self.bi_encoder)
        self.matcher = Matcher(
            retriever=self.retriever, 
            generate_letters=generate_letters, 
            letter_generator=self.letter_generator
        )
        
    @classmethod
    def from_settings(cls, settings: Settings):
        """Фабричный метод для создания приложения из настроек"""
        if settings.hf_token:
            login(token=settings.hf_token)
            print("✅ HF Token применен")
            
        print(f"💻 Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
        
        return cls(
            bi_encoder_name=settings.bi_encoder_name,
            bi_encoder_temperature=settings.bi_encoder_temperature,
            cross_encoder_model=settings.cross_encoder,
            faiss_path=settings.faiss_path,
            model_path=settings.model_path,
            retrieval_top_k=settings.retrieval_top_k,
            final_top_k=settings.final_top_k,
            min_score=settings.min_score,
            llm_mode=settings.llm_mode,
            llm_api_key=settings.llm_api_key,
            llm_base_url=settings.llm_base_url,
            llm_model=settings.llm_model,
            generate_letters=settings.generate_letters,
        )
        
    def get_stats(self) -> dict:
        index = getattr(self.store, 'index', None) or (self.store.get("index") if isinstance(self.store, dict) else None)
        return {
            "total_vacancies": index.ntotal if index else 0,
            "embedding_dim": index.d if index else 0,
            "device": "cuda" if self.bi_encoder.device.type == "cuda" else "cpu",
            "model_type": "custom" if self.model_path else "pretrained",
            "bi_encoder": self.bi_encoder_name,
        }

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    global _service
    _service = ResumeService.from_settings(settings)
    yield
    _service = None

def get_matcher() -> Matcher:
    """Зависимость только для Matcher"""
    if _service is None or _service.matcher is None:
        raise HTTPException(503, "Matcher не доступен")
    return _service.matcher

def get_explorer() -> Explorer:
    """Зависимость только для Explorer"""
    if _service is None or _service.explorer is None:
        raise HTTPException(503, "Explorer не доступен")
    return _service.explorer

def get_letter_generator() -> LetterGenerator:
    """Зависимость только для LetterGenerator"""
    if _service is None or _service.letter_generator is None:
        raise HTTPException(503, "LetterGenerator не доступен")
    return _service.letter_generator
