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

3. Запуск приложения

```bash
python ./src/main.py
```

# 🧪 Тестирование

1. откройте http://localhost:8000/docs

2. Тест /search:

```json
{
    "job_title": "Python Backend Developer",
    "grade": "senior",
    "city": "Москва",
    "salary": "300000 RUB",
    "work_format": "офис",
    "about_me": "Разрабатываю бэкенд 5 лет. Люблю чистый код и микросервисы.",
    "experience": "Senior Developer @ TechCorp (2020-2024)",
    "recent_jobs": "Python, FastAPI, PostgreSQL, Docker, Kafka, Redis"
}
```

2. Тест /analyze:

```json
{
    "job_title": "Python Backend Developer",
    "grade": "senior",
    "city": "Москва",
    "salary": "300000 RUB",
    "work_format": "офис",
    "about_me": "Разрабатываю бэкенд 5 лет. Люблю чистый код и микросервисы.",
    "experience": "Senior Developer @ TechCorp (2020-2024)",
    "recent_jobs": "Python, FastAPI, PostgreSQL, Docker, Kafka, Redis"
}
```
