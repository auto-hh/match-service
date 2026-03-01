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
    
    args = parser.parse_args()
    
    retrieval_top_k = int(os.getenv("RETRIEVAL_TOP_K", "50"))
    final_top_k = int(os.getenv("FINAL_TOP_K", "5"))
    min_score = float(os.getenv("MIN_SCORE", "0.0"))
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
    input_topic = os.getenv("INPUT_TOPIC", "resume_in")
    output_topic = os.getenv("OUTPUT_TOPIC", "resume_out")
    
    print("🚀 Инициализация приложения...")
    app = App(
        bi_encoder_name=args.bi_encoder_name,
        cross_encoder_model=args.cross_encoder,
        faiss_path=args.faiss_path,
        model_path=args.model_path,
        retrieval_top_k=retrieval_top_k,
        final_top_k=final_top_k,
        min_score=min_score,
    )
    
    stats = app.get_stats()
    print(f"✅ BiEncoder: {stats['bi_encoder']}")
    print(f"✅ Модель: {stats['model_type']}")
    print(f"✅ Вакансий: {stats['total_vacancies']}")
    print(f"✅ Device: {stats['device']}")
    
    if app.matcher is None:
        print("⚠️ Matcher не загружен (нет FAISS)")
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