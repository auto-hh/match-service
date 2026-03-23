import os
import torch
import threading
from pathlib import Path
from app import App
from dotenv import load_dotenv
from api import MatchingWorker, ExplorationWorker
from huggingface_hub import login

load_dotenv()

def main():
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
        print("hf_token успешно применен")
        
    bi_encoder_name = os.getenv("BI_ENCODER_NAME")
    if not bi_encoder_name:
        raise ValueError("BI_ENCODER_NAME не задан")
    
    bi_encoder_temperature = float(os.getenv("BI_ENCODER_TEMPERATURE") or "0.1")
    
    cross_encoder = os.getenv("CROSS_ENCODER")
    if not cross_encoder:
        raise ValueError("CROSS_ENCODER не задан")

    faiss_path = os.getenv("FAISS_PATH")
    if not faiss_path:
        raise ValueError("FAISS_PATH не задан")

    model_path = os.getenv("MODEL_PATH")

    retrieval_top_k = int(os.getenv("RETRIEVAL_TOP_K") or "50")
    final_top_k = int(os.getenv("FINAL_TOP_K", "5"))
    min_score = float(os.getenv("MIN_SCORE", "0.0"))

    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP") or "localhost:9092"
    matching_input_topic = os.getenv("MATCHING_INPUT_TOPIC") or "resume_in"
    matching_output_topic = os.getenv("MATCHING_OUTPUT_TOPIC") or "resume_out"
    exploration_input_topic = os.getenv("EXPLORATION_INPUT_TOPIC") or "resume_explore_in"
    exploration_output_topic = os.getenv("EXPLORATION_OUTPUT_TOPIC") or "resume_explore_out"

    llm_mode = os.getenv("LLM_MODE")
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY")
    llm_base_url = os.getenv("LLM_BASE_URL")
    llm_model = os.getenv("LLM_MODEL")
    
    generate_letters = bool(True if os.getenv("GENERATE_LETTERS") == "True" else False)

    print(f"device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

    print("Инициализация приложения...")
    app = App(
        bi_encoder_name=bi_encoder_name,
        bi_encoder_temperature=bi_encoder_temperature,
        cross_encoder_model=cross_encoder,
        faiss_path=faiss_path,
        model_path=model_path,
        retrieval_top_k=retrieval_top_k,
        final_top_k=final_top_k,
        min_score=min_score,
        llm_mode=llm_mode,
        llm_api_key=llm_api_key,
        llm_base_url=llm_base_url,
        llm_model=llm_model,
        generate_letters=generate_letters,
    )
    
    stats = app.get_stats()
    print(f"BiEncoder: {stats['bi_encoder']}")
    print(f"Модель: {stats['model_type']}")
    print(f"Вакансий: {stats['total_vacancies']}")
    print(f"Device: {stats['device']}")
    
    if app.matcher is None:
        print("Matcher не загружен")
        return
    
    if app.explorer is None:
        print("Explorer не загружен")
        return
    
    workers = [
        MatchingWorker(
            matcher=app.matcher,
            kafka_bootstrap=kafka_bootstrap,
            input_topic=matching_input_topic,
            output_topic=matching_output_topic,
        ),
        ExplorationWorker(
            explorer=app.explorer,
            kafka_bootstrap=kafka_bootstrap,
            input_topic=exploration_input_topic,
            output_topic=exploration_output_topic,
        ),
    ]
    
    threads = []
    for worker in workers:
        thread = threading.Thread(target=worker.run, daemon=False)
        thread.start()
        threads.append(thread)
        
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
