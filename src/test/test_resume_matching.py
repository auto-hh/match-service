import os
import json
from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer

load_dotenv()

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP") or "localhost:9092"
INPUT_TOPIC = os.getenv("MATCHING_INPUT_TOPIC") or "resume_in"
OUTPUT_TOPIC = os.getenv("MATCHING_OUTPUT_TOPIC") or "resume_out"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

test_resume = {
    "resume_id": 12345,
    "grade": "middle",
    "job_title": "Python Backend Developer",
    "location": "Москва",
    "salary_val": 200000,
    "salary_curr": "RUB",
    "skills_res": "Python, FastAPI, PostgreSQL",
    "about_me": "Разрабатываю бэкенд 3 года",
    "exp_count": 3,
    "exp_text": "Senior Developer @ TechCorp",
    "edu_uni": "МГУ",
    "edu_year": "2020"
}

print(f"🚀 Отправляю в {INPUT_TOPIC}...")
producer.send(INPUT_TOPIC, value=test_resume)
producer.flush()
producer.close()
print(f"✅ Отправлено (resume_id={test_resume['resume_id']})\n")

print(f"👂 Слушаю {OUTPUT_TOPIC}...")

consumer = KafkaConsumer(
    OUTPUT_TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    auto_offset_reset='latest',
    consumer_timeout_ms=10000,  # Ждём 10 сек
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

found = False
for message in consumer:
    found = True
    print(f"✅ Получено из {OUTPUT_TOPIC}:\n")
    print(json.dumps(message.value, ensure_ascii=False, indent=2))
    break

consumer.close()

if not found:
    print("⏱️  Таймаут: ответ не пришёл за 10 секунд")
    print("💡 Проверьте, что воркер запущен")

print("\n🏁 Готово")