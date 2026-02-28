import pandas as pd
from datasets import Dataset
from .prepare_data import format_vacancy, format_resume, load_dataset

def create_pairs(vacancies_path: str, resumes_path: str):
    v_df = load_dataset(vacancies_path)
    r_df = load_dataset(resumes_path)
    
    df = pd.merge(r_df, v_df, left_on='vacancy_id', right_on='id', suffixes=('_res', '_vac'))
    
    data_dict = {
        "anchor": [],
        "positive": [],
    }
    
    for _, row in df.iterrows():
        v_text = format_vacancy(row.to_dict())
        r_text = format_resume(row.to_dict())
        
        data_dict["anchor"].append(r_text)
        data_dict["positive"].append(v_text)
    
    return Dataset.from_dict(data_dict)
