import pandas as pd
import os

print("Initializing Web Analytics ETL Pipeline...")

# 1. Extract: Load the raw dataset
raw_path = 'data/raw/clickstream_raw.csv'
if not os.path.exists(raw_path):
    raise FileNotFoundError(f"Missing raw data file. Please run generate_clicks.py first.")

df = pd.read_csv(raw_path)
print(f"-> Successfully loaded {len(df)} raw events.")

# 2. Transform: Clean and handle structural anomalies
# Step A: Remove exact duplicate rows
initial_count = len(df)
df = df.drop_duplicates()
print(f"-> Deduplication complete. Removed {initial_count - len(df)} duplicate records.")

# Step B: Impute missing values in categorical data
df['device'] = df['device'].fillna('Unknown')
print("-> Imputed missing device fields with 'Unknown' flag.")

# Step C: Parse dates correctly for chronological ordering
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values(by=['user_id', 'session_id', 'timestamp']).reset_index(drop=True)

# Step D: Create a sequential index per session (Crucial for Power BI Funnels)
# This calculates if a click was the 1st, 2nd, or 3rd action inside that specific session
df['session_step_sequence'] = df.groupby(['user_id', 'session_id']).cumcount() + 1
print("-> Calculated sequential session step indices.")

# 3. Load: Export cleaned master table to the processed zone
processed_csv_path = 'data/processed/clickstream_clean.csv'
df.to_csv(processed_csv_path, index=False)
print(f"-> ETL pipeline execution successful! Saved {len(df)} clean events to '{processed_csv_path}'")