import sys
import os
import pandas as pd

# Path setup to find common.db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from common.db import get_engine

def seed_database():
    csv_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "data", "event_level_data_dirty.csv"
    ))
    
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    engine = get_engine()
    df.to_sql("raw_data", engine, if_exists='replace', index=False)
    print(f"Uploaded {len(df)} rows to raw_data.")

if __name__ == "__main__":
    seed_database()