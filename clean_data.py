import sys
import os

# Able to just click play button
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np
import re
from common.db import get_engine

def clean_data_pipeline():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM raw_data", engine)

    # Remove duplicates
    df = df.drop_duplicates(subset=['record_id'], keep='first')

    # Standardize types and fill missing timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').ffill().bfill()
    df['hour_of_day'] = df['timestamp'].dt.hour.astype(int)
    df = df[(df['hour_of_day'] >= 6) & (df['hour_of_day'] <= 22)]
    df['day_of_week'] = df['timestamp'].dt.dayofweek.astype(int)

    # Clean numeric columns
    for col in ['temperature', 'humidity']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.\-]', '', regex=True), errors='coerce')
    
    # Fahrenheit conversion
    df.loc[df['temperature'] > 45, 'temperature'] = (df['temperature'] - 32) * 5/9

    # Impute missing values with location median
    df['temperature'] = df.groupby('location_id')['temperature'].transform(lambda x: x.fillna(x.median()))
    df['humidity'] = df.groupby('location_id')['humidity'].transform(lambda x: x.fillna(x.median()))

    # Clean boolean strings
    def fix_bool(val):
        v = str(val).lower()
        return True if 'true' in v or '1' in v else False

    df['is_weekend'] = df['is_weekend'].apply(fix_bool).astype(int)
    df['is_public_holiday'] = df['is_public_holiday'].apply(fix_bool).astype(int)

    for col in ['weather', 'location_name']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[{}()\[\]@*&|°\\ø$%//#/]', '', regex=True).str.strip().str.lower()

    # Final table update
    df.to_sql("clean_data", engine, if_exists='replace', index=False)
    print(f"Cleaned data saved. Final count: {len(df)}")

if __name__ == "__main__":
    clean_data_pipeline()