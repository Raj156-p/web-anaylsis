import pandas as pd
import numpy as np

INPUT = 'user_behaviour_data.csv'
OUTPUT = 'cleaned_session_metrics.csv'

try:
    df = pd.read_csv(INPUT)
except FileNotFoundError:
    raise SystemExit('Error: Raw data file not found.')

df.drop_duplicates(inplace=True)
df['element_id'] = df['element_id'].fillna('None')
df['scroll_depth'] = pd.to_numeric(df['scroll_depth'], errors='coerce').fillna(0)
df['time_on_page'] = pd.to_numeric(df['time_on_page'], errors='coerce').fillna(0)

session_data = df.groupby('session_id').agg(
    page_views=('page_visited','nunique'),
    total_events=('event_type','count'),
    session_duration=('time_on_page','max'),
    max_scroll=('scroll_depth','max')
).reset_index()

session_data['is_bounce'] = np.where(
    (session_data['page_views'] == 1) & (session_data['total_events'] < 3), 1, 0
)

successful_events = {'form_submitted', 'checkout_completed'}
form_success_sessions = df[df['event_type'].isin(successful_events)]['session_id'].unique()
session_data['task_success'] = np.where(
    session_data['session_id'].isin(form_success_sessions), 1, 0
)

session_data.to_csv(OUTPUT, index=False)
print('Data cleaning complete. Output saved to:', OUTPUT)
print('Total Sessions Processed:', len(session_data))
print('Overall Task Success Rate: {:.2f}%'.format(session_data['task_success'].mean()*100 if len(session_data) else 0))
