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
    job_title = v.get('job_title_vac') or v.get("job_title") or v.get('target_role') or "Не указано"
    experience = v.get('experience') or "Не указано"
    salary = v.get("salary") or "Не указано"
    skills_vac = v.get("skills_vac") or "Не указано"
    vacancy_text = clean_text(v.get("vacancy_text") or "Не указано")
    
    return (
        f"ВАКАНСИЯ: {job_title}. "
        f"ЗАРПЛАТА: {salary}. "
        f"ОПЫТ: {experience}. "
        f"НАВЫКИ: {skills_vac}. "
        f"ОПИСАНИЕ: {vacancy_text}"
    )

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