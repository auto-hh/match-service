import re
import pandas as pd

def load_dataset(path: str):
    return pd.read_csv(path).fillna('')

def clean_text(text: str) -> str:
    if not text: return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_vacancy(v: dict) -> str:
    return (
        f"ВАКАНСИЯ: {v.get('target_role', v.get('job_title', 'None'))}. "
        f"НАВЫКИ: {v.get('skills_vac', 'None')}. "
        f"ОПИСАНИЕ: {clean_text(v.get('vacancy_text', 'None'))}"
    )

def format_resume(r: dict) -> str:
    edu_info = f"{r.get('edu_uni', 'None')} (год выпуска: {r.get('edu_year', 'None')})" if r.get('edu_uni') else "Не указано"
    return (
        f"РЕЗЮМЕ: {r.get('job_title', 'None')}. "
        f"ОПЫТ: {clean_text(r.get('exp_text', 'None'))}. "
        f"ОБРАЗОВАНИЕ: {edu_info}. "
        f"НАВЫКИ: {r.get('skills_res', 'None')}. "
        f"О СЕБЕ: {clean_text(r.get('about_me', 'None'))}"   
    )