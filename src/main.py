import os
from app import App
from dotenv import load_dotenv
from api import MatchingWorker

load_dotenv()

def main():
    bi_encoder_name = os.getenv("BI_ENCODER_NAME")
    if not bi_encoder_name:
        raise ValueError("BI_ENCODER_NAME не задан")

    cross_encoder = os.getenv("CROSS_ENCODER")
    if not cross_encoder:
        raise ValueError("CROSS_ENCODER не задан")

    faiss_path = os.getenv("FAISS_PATH")
    if not faiss_path:
        raise ValueError("FAISS_PATH не задан")

    model_path = os.getenv("MODEL_PATH")

    retrieval_top_k = int(os.getenv("RETRIEVAL_TOP_K", "50"))
    final_top_k = int(os.getenv("FINAL_TOP_K", "5"))
    min_score = float(os.getenv("MIN_SCORE", "0.0"))

    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
    input_topic = os.getenv("INPUT_TOPIC", "resume_in")
    output_topic = os.getenv("OUTPUT_TOPIC", "resume_out")

    llm_mode = os.getenv("LLM_MODE")
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY")
    llm_base_url = os.getenv("LLM_BASE_URL")
    llm_model = os.getenv("LLM_MODEL")

    print("Инициализация приложения...")
    app = App(
        bi_encoder_name=bi_encoder_name,
        cross_encoder_model=cross_encoder,
        faiss_path=faiss_path,
        model_path=model_path,
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
        print("Matcher не загружен")
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
