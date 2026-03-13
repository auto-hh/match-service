from kafka import KafkaConsumer
import json

print("📡 Слушаю топик resume_in... (Ctrl+C для остановки)")

consumer = KafkaConsumer(
    'resume_in',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    consumer_timeout_ms=float('inf'),
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

for message in consumer:
    print("\n" + "="*50)
    print(f"📩 Topic: {message.topic}")
    print(f"🔑 Key: {message.key}")
    print(f"📝 Value: {json.dumps(message.value, ensure_ascii=False, indent=2)}")
    print("="*50)

print("\n⏹️  Сообщения закончились")
consumer.close()