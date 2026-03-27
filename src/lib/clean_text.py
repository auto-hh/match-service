import re
import pandas as pd
from bs4 import BeautifulSoup
from typing import Any

def clean_text(html: Any) -> str:
    if pd.isna(html) or not isinstance(html, str):
        return ""

    # 1. Парсим HTML и извлекаем текст
    text = BeautifulSoup(html, 'html.parser').get_text()

    # 2. Нормализуем пробелы (множественные пробелы/переносы → один пробел)
    text = re.sub(r'\s+', ' ', text).strip()

    # 3. (Опционально) Убираем явный шум: ссылки, телефоны, email
    text = re.sub(r'https?://\S+|t\.me/\S+|www\.\S+', '', text)
    text = re.sub(r'\+7[\d\s\-\(\)]{10,}', '', text)
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', text)
    
    return text