import re
import pandas as pd

def load_dataset(path: str):
    return pd.read_csv(path).fillna('')

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_vacancy(v: dict) -> str:
    job_title = v.get('job_title') or v.get('target_role') or "Не указано"
    
    return (
        f"ВАКАНСИЯ: {job_title}. "
        f"ОПЫТ: {v.get('experience', 'Не указано')}. "
        f"ЗАРПЛАТА: {v.get("salary")}. "
        f"НАВЫКИ: {v.get('skills_vac', 'Не указано')}. "
        f"ОПИСАНИЕ: {clean_text(v.get('vacancy_text', 'Не указано'))}"
    )

def format_resume(r: dict) -> str:
    if r.get('edu_uni') and r.get("edu_uni") != "Не указано":
        edu_info = f"{r.get('edu_uni', 'Не указано')} (год выпуска: {r.get('edu_year', 'Не указано')})" if r.get('edu_uni') else "Не указано"
    else:
        edu_info = "Не указано"
        
    if r.get("salary_val"):
        salary = f"{r.get("salary_val")} {r.get("salary_curr")}"
    else:
        salary = "Не указано"
    
    return (
        f"РЕЗЮМЕ: {r.get('job_title', 'Не указано')}. "
        f"ЗАРПЛАТА: {salary}. "
        f"ОПЫТ: {clean_text(r.get('exp_text', 'Не указано'))}. "
        f"ОБРАЗОВАНИЕ: {edu_info}. "
        f"НАВЫКИ: {r.get('skills_res', 'Не указано')}. "
        f"О СЕБЕ: {clean_text(r.get('about_me', 'Не указано'))}"   
    )