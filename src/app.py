from core import Matcher, Retriever
from lib import load_vector_store, load_bi_encoder, load_cross_encoder

class App:    
    def __init__(
        self,
        bi_encoder_name: str,
        cross_encoder_model: str,
        faiss_path: str,
        retrieval_top_k: int,
        final_top_k: int,
        model_path: str = None,
        min_score: float = 0.0,
    ):
        self.bi_encoder_name = bi_encoder_name
        self.model_path = model_path
        
        self.bi_encoder = load_bi_encoder(
            model_path=model_path,
            bi_encoder_name=bi_encoder_name,
        )
        self.cross_encoder = load_cross_encoder(model_name=cross_encoder_model)
        self.store = load_vector_store(self.bi_encoder, faiss_path)

        self.retriever = Retriever(
            bi_encoder=self.bi_encoder,
            cross_encoder=self.cross_encoder,
            store=self.store,
            retrieval_top_k=retrieval_top_k,
            final_top_k=final_top_k,
            min_score=min_score,
        )
        
        self.matcher = Matcher(retriever=self.retriever)
        
    def get_stats(self) -> dict:
        return {
            "total_vacancies": self.store["index"].ntotal,
            "embedding_dim": self.store["index"].d,
            "device": "cuda" if self.bi_encoder.device.type == "cuda" else "cpu",
            "model_type": "custom" if self.model_path else "pretrained",
            "bi_encoder": self.bi_encoder_name,
        }