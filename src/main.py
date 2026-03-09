import os
import argparse
from .app import App
from dotenv import load_dotenv
from api import MatchingWorker

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bi-encoder-name", required=True, help="BiEncoder модель")
    parser.add_argument("--cross-encoder", required=True, help="CrossEncoder модель")
    parser.add_argument("--model-path", default=None, help="Путь к своей модели")
    parser.add_argument("--faiss-path", required=True, help="Путь к FAISS индексу")

    parser.add_argument("--llm-mode", default=None, choices=["api", "ollama", "none"],
                        help="Режим LLM (api=Groq, ollama=локально, none=отключить)")
    parser.add_argument("--llm-api-key", default=None, help="API ключ для LLM")
    parser.add_argument("--llm-base-url", default=None, help="URL для LLM API")
    parser.add_argument("--llm-model", default=None, help="Название модели LLM")
    
    args = parser.parse_args()
    
    retrieval_top_k = int(os.getenv("RETRIEVAL_TOP_K", "50"))
    final_top_k = int(os.getenv("FINAL_TOP_K", "5"))
    min_score = float(os.getenv("MIN_SCORE", "0.0"))
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
    input_topic = os.getenv("INPUT_TOPIC", "resume_in")
    output_topic = os.getenv("OUTPUT_TOPIC", "resume_out")
    llm_mode = args.llm_mode if args.llm_mode != "none" else None
    llm_api_key = args.llm_api_key or os.getenv("GROQ_API_KEY")
    llm_base_url = args.llm_base_url or os.getenv("LLM_BASE_URL")
    llm_model = args.llm_model or os.getenv("LLM_MODEL")
    
    print("Инициализация приложения...")
    app = App(
        bi_encoder_name=args.bi_encoder_name,
        cross_encoder_model=args.cross_encoder,
        faiss_path=args.faiss_path,
        model_path=args.model_path,
        retrieval_top_k=retrieval_top_k,
        final_top_k=final_top_k,
        min_score=min_score,
        llm_mode=llm_mode,
        llm_api_key=llm_api_key,
        llm_base_url=llm_base_url,
        llm_model=llm_model
    )
    
    stats = app.get_stats()
    print(f"BiEncoder: {stats['bi_encoder']}")
    print(f"Модель: {stats['model_type']}")
    print(f"Вакансий: {stats['total_vacancies']}")
    print(f"Device: {stats['device']}")
    
    if app.matcher is None:
        print("Matcher не загружен (нет FAISS)")
        return
    
    worker = MatchingWorker(
        matcher=app.matcher,
        kafka_bootstrap=kafka_bootstrap,
        input_topic=input_topic,
        output_topic=output_topic,
    )
    
    worker.run()

if __name__ == "__main__":
    main()