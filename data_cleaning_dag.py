from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd

# Existing imports
from pipelines.cleaning.clean_data import clean_data_pipeline
from pipelines.features.build_features import build_feature_dict
from common.db import get_engine

def inline_feature_engineering():
    engine = get_engine()
    
    # 1. Loading
    print("Fetching cleaned records from Supabase...")
    df_clean = pd.read_sql("SELECT * FROM clean_data", engine)
    
    if df_clean.empty:
        print("No data found in clean_data. Skipping feature engineering.")
        return

    # 2. Transforming (The Human Way)
    # Using .apply(axis=1) is much cleaner and faster than iterrows loops
    print(f"Engineering features for {len(df_clean)} rows...")
    df_features = pd.DataFrame(df_clean.apply(lambda x: build_feature_dict(x.to_dict()), axis=1).tolist())
    
    # 3. Saving
    print(f"Uploading processed features to 'features' table...")
    df_features.to_sql('features', engine, if_exists='replace', index=False)
    print("Pipeline execution successful!")

default_args = {
    'owner': 'data_engineers',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'crowd_level_predictor_pipeline',
    default_args=default_args,
    description='End-to-end pipeline: Raw -> Clean -> Features',
    schedule_interval='@daily',
    catchup=False,
    tags=['dsa_academy', 'industry_project'] # Helpful for filtering in Airflow
) as dag:

    # Task 1: Fix the mess (Unit mismatches, special chars, etc.)
    task_clean_data = PythonOperator(
        task_id='step_1_clean_raw_data',
        python_callable=clean_data_pipeline
    )

    # Task 2: Prep for ML (Cyclical time, holiday flags, etc.)
    task_engineer_features = PythonOperator(
        task_id='step_2_build_ml_features',
        python_callable=inline_feature_engineering
    )

    # The Flow
    task_clean_data >> task_engineer_features