from sqlalchemy import text
import sys, os

# This tells Python to look in the current folder for db.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from common.db import get_engine

# Professional Structured Schema
DDL = """
CREATE TABLE IF NOT EXISTS public.raw_data (
    record_id TEXT,
    location_id TEXT,
    location_name TEXT,
    lat TEXT,
    long TEXT,
    timestamp TIMESTAMP,
    temperature TEXT,
    humidity TEXT,
    is_public_holiday TEXT,
    day_of_week FLOAT,
    hour_of_day FLOAT,
    timezone_info TEXT
);

CREATE TABLE IF NOT EXISTS public.clean_data (
    record_id TEXT PRIMARY KEY,
    location_id TEXT,
    location_name TEXT,
    lat FLOAT,
    long FLOAT,
    timestamp TIMESTAMP,
    temperature FLOAT,
    humidity FLOAT,
    is_weekend BOOLEAN,
    is_public_holiday BOOLEAN,
    day_of_week INT,
    hour_of_day INT
);

CREATE TABLE IF NOT EXISTS public.features (
    location_id TEXT,
    temp_celsius FLOAT,
    humidity FLOAT,
    weather_type INT,
    location_popularity INT,
    hour_sin FLOAT,
    hour_cos FLOAT,
    day_sin FLOAT,
    day_cos FLOAT,
    is_weekend INT,
    is_holiday INT,
    crowd_level INT, 
    timestamp TIMESTAMP 
);
"""

if __name__ == "__main__":
    engine = get_engine()
    with engine.begin() as conn:
        for stmt in DDL.strip().split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))
    print("Tables created: raw_data, clean_data, features")