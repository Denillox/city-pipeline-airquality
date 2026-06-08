import json
import pandas as pd
import os

with open('data/raw/airquality_raw.json', 'r') as f:
    d = json.load(f)

measurements = d["results"]

df = pd.DataFrame(measurements)
print(df.head(2))
print(df.columns)

df['datetime'] = df['period'].apply(lambda x: x.get('datetimeFrom').get('utc') if isinstance(x, dict) else None)
df['datetime'] = pd.to_datetime(df['datetime'])
df['parameter_clean'] = df['parameter'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
df['unit'] = df['parameter'].apply(lambda x: x.get('units') if isinstance(x, dict) else None)

df_final_transformed = df[['datetime', 'parameter_clean', 'value', 'unit']]
print(df_final_transformed.head())
print(df_final_transformed.dtypes)

os.makedirs('data/processed', exist_ok=True)
df_final_transformed.to_csv('data/processed/airquality_clean.csv', index=False)