import json
from kafka import KafkaConsumer, KafkaProducer
from schemas import Resume, MatchResult
from core import Matcher

class MatchingWorker:   
    def __init__(
        self,
        matcher: Matcher,
        kafka_bootstrap: str,
        input_topic: str,
        output_topic: str,
    ):
        self.input_topic = input_topic
        self.output_topic = output_topic
        
        self.consumer = KafkaConsumer(
            input_topic,
            bootstrap_servers=kafka_bootstrap,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            consumer_timeout_ms=1000,
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
        )
        
        self.matcher = matcher
    
    def process_message(self, message: dict) -> MatchResult:
        resume = Resume.from_dict(message)
        result = self.matcher.match(resume)
        return result
    
    def send_result(self, result: MatchResult):
        self.producer.send(self.output_topic, value=result.to_dict())
    
    def run(self):
        print(f"🎧 Слушаю топик: {self.input_topic}")
        print(f"📤 Отправляю в топик: {self.output_topic}")
        
        try:
            for kafka_message in self.consumer:
                try:
                    message = kafka_message.value
                    resume_id = message.get("resume_id", 0)
                    
                    print(f"📩 Резюме {resume_id}...")
                    
                    result = self.process_message(message)
                    self.send_result(result)
                    
                    print(f"✅ {result.status} — {len(result.matches)} матчей")
                    
                except Exception as e:
                    print(f"❌ Ошибка обработки: {e}")
                    # Отправляем ошибку в output
                    error_result = MatchResult(
                        resume_id=message.get("resume_id", 0),
                        matches=[],
                        status="error",
                    )
                    self.send_result(error_result)
                    
        except KeyboardInterrupt:
            print("\n🛑 Остановка воркера...")
        finally:
            self.consumer.close()
            self.producer.close()