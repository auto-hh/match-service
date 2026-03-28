import pandas as pd
from .clean_text import clean_text
from schemas import Resume, Vacancy

def load_dataset(path: str):
    return pd.read_csv(path).fillna('')

def format_vacancy(v: Vacancy) -> str:
    job_title = (v.job_title or '').strip()
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
    if salary:
        meta.append(f"зарплата: {salary}")
    
    if meta:
        parts.append(f"[META] {'; '.join(meta)}")
    
    return ' | '.join(parts)

def format_resume(r: Resume) -> str:
    parts = []
    
    if r.job_title and r.job_title.strip():
        parts.append(f"[ROLE] {r.job_title.strip()}")
    
    if r.grade and r.grade.strip():
        parts.append(f"[GRADE] {r.grade.strip()}")
    
    if r.city and r.city.strip():
        parts.append(f"[LOC] {r.city.strip()}")
    
    if r.work_format and r.work_format.strip():
        parts.append(f"[FORMAT] {r.work_format.strip()}")
    
    if r.salary:
        parts.append(f"[SALARY] {r.salary} рублей")
    
    if r.recent_jobs and r.recent_jobs.strip():
        text = r.recent_jobs.strip()
        parts.append(f"[SKILLS] {text}")
    
    if r.experience and r.experience.strip():
        text = r.experience.strip()
        parts.append(f"[EXP] {text}")
    
    if r.about_me and r.about_me.strip():
        text = r.about_me.strip()
        parts.append(f"[ABOUT] {text}")
    
    return ' | '.join(parts)