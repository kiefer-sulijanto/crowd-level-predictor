import sys
import os

# can press the run button instead
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np

def build_feature_dict(row: dict) -> dict:
    feat = {}

    # 1. Direct Mappings
    feat["location_id"] = str(row.get("location_id"))
    feat["temp_celsius"] = float(row.get("temperature", 0))
    feat["humidity"] = float(row.get("humidity", 0))
    # Requirement: Weather Impact (using the dummy mapping from your notebook)
    feat["weather_type"] = int(row.get("weather_final", 0))
    # Requirement: Location Analysis
    feat["location_popularity"] = int(row.get("location_freq", 0))
    
    # 2. Cyclical Time Features (Requirement: Temporal Analysis)
    ts_val = row.get("timestamp")
    if ts_val is not None:
        ts = pd.to_datetime(ts_val, errors="coerce")
        if pd.notna(ts):
            hour = ts.hour
            day = ts.dayofweek
            
            # Sine/Cosine for Hour (24-hour cycle)
            feat["hour_sin"] = np.sin(2 * np.pi * hour / 24)
            feat["hour_cos"] = np.cos(2 * np.pi * hour / 24)
            
            # Sine/Cosine for Day of Week (7-day cycle)
            feat["day_sin"] = np.sin(2 * np.pi * day / 7)
            feat["day_cos"] = np.cos(2 * np.pi * day / 7)
            
            feat["is_weekend"] = int(row.get("is_weekend", 0))
            feat["is_holiday"] = int(row.get("is_public_holiday", 0))

    # 3. ML Target
    # Ensure 'scan_count' exists in SQL table 'clean_data'
    feat["crowd_level"] = row.get("scan_count", 0)

    return feat