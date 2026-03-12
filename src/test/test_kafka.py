from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

msg = {
    "resume_id": 12345,
    "grade": "middle",
    "job_title": "Python Backend Developer",
    "location": "Москва",
    "salary_val": 200000,
    "salary_curr": "RUB",
    "skills_res": "Python, FastAPI, PostgreSQL, Docker, Kafka",
    "about_me": "Разрабатываю бэкенд 3 года. Люблю чистый код и микросервисы.",
    "exp_count": 3,
    "exp_text": "Senior Developer @ TechCorp (2021-2024)",
    "edu_uni": "МГУ",
    "edu_year": "2020"
}

print("🚀 Отправляю резюме...")
future = producer.send('resume_in', value=msg)
producer.flush()

record = future.get(timeout=10)
print(f"✅ Отправлено: partition={record.partition}, offset={record.offset}")

producer.close()