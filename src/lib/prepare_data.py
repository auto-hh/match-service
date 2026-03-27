import pandas as pd
from .clean_text import clean_text
from schemas import Vacancy

def load_dataset(path: str):
    return pd.read_csv(path).fillna('')

def format_vacancy(v: Vacancy) -> str:
    job_title = (v.jobTitle or '').strip()
    city = (v.city or '').strip()
    salary = (v.salary or '').strip()
    body = clean_text(v.body).strip()
    
    parts = []
    
    if job_title:
        parts.append(f"[ROLE] {job_title}")
    if city:
        parts.append(f"[LOC] {city}")
    
    if body:
        parts.append(f"[DESC] {body}")
    
    meta = []
    if salary and salary.lower() != 'не указана':
        meta.append(f"зарплата: {salary}")
    
    if meta:
        parts.append(f"[META] {'; '.join(meta)}")
    
    return ' | '.join(parts)

def format_resume(r: dict) -> str:
    job_title = r.get("job_title_res") or r.get("job_title") or "Не указано"
    
    if r.get("salary_val"):
        salary = f"{r.get('salary_val')} {r.get('salary_curr')}"
    else:
        salary = "Не указано"
    
    exp_text = clean_text(r.get("exp_text") or "Не указано")
    
    if r.get('edu_uni') and r.get("edu_uni") != "Не указано":
        edu_info = f"{r.get('edu_uni', 'Не указано')} (год выпуска: {r.get('edu_year', 'Не указано')})" if r.get('edu_uni') else "Не указано"
    else:
        edu_info = "Не указано"
        
    skills_res = r.get("skills_res") or "Не указано"
    about_me = r.get('about_me') or "Не указано"
    
    return (
        f"ВАКАНСИЯ: {job_title}. "
        f"ЗАРПЛАТА: {salary}. "
        f"ОПЫТ: {exp_text}. "
        f"ОБРАЗОВАНИЕ: {edu_info}. "
        f"НАВЫКИ: {skills_res}. "
        f"О СЕБЕ: {about_me}"   
    )