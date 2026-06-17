import pandas as pd
import random
import uuid
from datetime import datetime, timedelta
import os

# Create data directories if they don't exist
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# Configuration parameters
NUM_USERS = 500
NUM_EVENTS = 15000
START_DATE = datetime(2026, 6, 1)

# Blueprint variables for realistic web behavior
pages = ['/home', '/product_list', '/product_detail_A', '/product_detail_B', '/cart', '/checkout_success']
event_types = ['page_view', 'button_click', 'add_to_cart', 'purchase']
devices = ['Mobile', 'Desktop', 'Tablet']
sources = ['Google_SEO', 'Direct', 'Meta_Ads', 'LinkedIn_Inbound']

# Generate stable User IDs and Session IDs
user_pool = [str(uuid.uuid4())[:8] for _ in range(NUM_USERS)]
sessions = {}

print("Synthesizing raw web traffic logs...")

event_list = []

for _ in range(NUM_EVENTS):
    user = random.choice(user_pool)
    
    # 30% chance a user starts a fresh session
    if user not in sessions or random.random() < 0.3:
        sessions[user] = str(uuid.uuid4())[:12]
        
    session = sessions[user]
    
    # Generate sequential time increments
    timestamp = START_DATE + timedelta(
        days=random.randint(0, 14),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    
    # Create realistic funnel paths (e.g., you can't purchase without visiting home)
    page = random.choices(pages, weights=[0.4, 0.3, 0.15, 0.1, 0.04, 0.01])[0]
    
    # Align events logically with pages
    if page == '/checkout_success':
        event = 'purchase'
    elif page == '/cart':
        event = random.choice(['page_view', 'button_click'])
    elif 'product_detail' in page:
        event = random.choices(['page_view', 'add_to_cart', 'button_click'], weights=[0.5, 0.3, 0.2])[0]
    else:
        event = random.choice(['page_view', 'button_click'])

    # Inject intentional data anomalies (5% chance of missing device info for cleaning practice)
    device = None if random.random() < 0.05 else random.choice(devices)
    
    event_list.append({
        'event_id': str(uuid.uuid4())[:16],
        'timestamp': timestamp,
        'user_id': user,
        'session_id': session,
        'url_path': page,
        'event_action': event,
        'device': device,
        'traffic_source': random.choice(sources)
    })

# Convert to DataFrame
df = pd.DataFrame(event_list)

# Inject intentional exact duplicate rows to test your deduplication logic
duplicates = df.sample(n=250)
df = pd.concat([df, duplicates], ignore_index=True)

# Sort chronologically
df = df.sort_values(by='timestamp').reset_index(drop=True)

# Export raw extraction to CSV
df.to_csv('data/raw/clickstream_raw.csv', index=False)
print(f"Extraction successful! Saved {len(df)} raw logs to 'data/raw/clickstream_raw.csv'")