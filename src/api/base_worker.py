from abc import ABC, abstractmethod
from kafka import KafkaConsumer, KafkaProducer
import json
from typing import Any

class BaseWorker(ABC):    
    def __init__(
        self,
        kafka_bootstrap: str,
        input_topic: str,
        output_topic: str,
    ):
        self.input_topic = input_topic
        self.output_topic = output_topic
        
        self.consumer = KafkaConsumer(
            self.input_topic,
            bootstrap_servers=[kafka_bootstrap],
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset='earliest',
            consumer_timeout_ms=float('inf'),
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_bootstrap],
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
        )
    
    @abstractmethod
    def process_message(self, message: dict[str, Any]) -> Any:
        pass
    
    @abstractmethod
    def get_worker_name(self) -> str:
        pass
    
    def send_result(self, result: Any):
        if hasattr(result, 'to_dict'):
            data = result.to_dict()
        elif isinstance(result, dict):
            data = result
        else:
            data = {"result": result}
        
        self.producer.send(self.output_topic, value=data)
        self.producer.flush()
    
    def run(self):
        """Основной цикл воркера"""
        print(f"🚀 {self.get_worker_name()} запущен")
        print(f"📥 Вход: {self.input_topic}")
        print(f"📤 Выход: {self.output_topic}")
        
        try:
            for kafka_message in self.consumer:
                try:
                    message = kafka_message.value
                    resume_id = message.get("resume_id", 0)
                    
                    print(f"\n[{self.get_worker_name()}] Резюме {resume_id}...")
                    
                    result = self.process_message(message)
                    self.send_result(result)
                    
                    print(f"✅ Обработано")
                    
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    
        except KeyboardInterrupt:
            print(f"\n🛑 {self.get_worker_name()} остановлен")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        print("🔌 Закрытие соединений...")
        self.consumer.close()
        self.producer.close()