# 🚀 Быстрый старт

1. Установка зависимостей

```bash
pip install -r requirements.txt
```

2. Настройка окружения

а. Скопируйте шаблон

```bash
cp .env.example .env
```

б. Отредактируйте поля под свои нужды

Обязательные поля: BI_ENCODER_NAME, CROSS_ENCODER, FAISS_PATH

3. Запуск кафки

```bash

docker run -d --name kafka -p 9092:9092 \
  -e KAFKA_NODE_ID=1 \
  -e KAFKA_PROCESS_ROLES=broker,controller \
  -e KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 \
  -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  apache/kafka:3.7.0

```

4. Запуск приложения

```bash
python ./src/main.py
```

# 🧪 Тестирование Kafka

1. Отправка тестового резюме

```bash
python ./src/test/test_kafka.py
```

2. Просмотр сообщений в топиках

а. Отправленное сообщение

```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh `  --bootstrap-server localhost:9092`
--topic resume_in `
--from-beginning
```

б. Полученное сообщение

```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh `  --bootstrap-server localhost:9092`
--topic resume_out `
--from-beginning
```
