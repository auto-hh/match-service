import os
import json
from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer

load_dotenv()

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP") or "localhost:9092"
INPUT_TOPIC = os.getenv("EXPLORATION_INPUT_TOPIC") or "resume_explore_in"
OUTPUT_TOPIC = os.getenv("EXPLORATION_OUTPUT_TOPIC") or "resume_explore_out"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

test_resume = {
    "resume_id": 99999,
    "grade": "senior",
    "job_title": "Python Backend Developer",
    "location": "Москва",
    "salary_val": 300000,
    "salary_curr": "RUB",
    "skills_res": "Python, FastAPI, PostgreSQL, Docker, Kafka, Redis",
    "about_me": "Разрабатываю бэкенд 5 лет. Люблю чистый код и микросервисы.",
    "exp_count": 5,
    "exp_text": "Senior Developer @ TechCorp (2020-2024)",
    "edu_uni": "МГУ",
    "edu_year": "2018"
}

print(f"🚀 Отправляю в {INPUT_TOPIC}...")
producer.send(INPUT_TOPIC, value=test_resume)
producer.flush()
producer.close()

print(f"✅ Отправлено (resume_id={test_resume['resume_id']})\n")

print(f"👂 Слушаю {OUTPUT_TOPIC}... (Integrated Gradients может занять время)")

consumer = KafkaConsumer(
    OUTPUT_TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    auto_offset_reset='latest',
    consumer_timeout_ms=30000,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

found = False
for message in consumer:
    found = True
    print(f"\n✅ Получено из {OUTPUT_TOPIC}:\n")
    
    result = message.value
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("word_weights"):
        print("\n🔝 Топ-10 важных слов:")
        sorted_words = sorted(
            result["word_weights"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        for i, (word, score) in enumerate(sorted_words, 1):
            print(f"   {i}. {word}: {score:.4f}")
    
    print(f"\n⏱️  Время обработки: {result.get('processing_time_ms', 0):.2f}ms")
    break

consumer.close()

if not found:
    print("⏱️  Таймаут: ответ не пришёл за 30 секунд")
    print("💡 Проверьте, что exploration-воркер запущен")

print("\n🏁 Готово")