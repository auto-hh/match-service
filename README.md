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
```

2. Тест /analyze:

```json
{
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
```
