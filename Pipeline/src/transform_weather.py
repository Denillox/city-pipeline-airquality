import json
import os
import requests
import pandas as pd

# Parameters retrieved from SMHI raw data
parameters = [1, 4, 3, 7]

# Mapping to translate SMHI parameter IDs to standardized English names and units
parameter_mapping = {
    1: {'name': 'temperature', 'unit': 'C'},
    3: {'name': 'wind_speed', 'unit': 'm/s'},
    4: {'name': 'wind_direction', 'unit': 'degrees'},
    7: {'name': 'precipitation', 'unit': 'mm'}
}

# List to collect processed DataFrames before consolidation
all_dfs = []

print("Starting transformation of weather data...")

# ETL - TRANSFORM LOOP
for p in parameters:
    file_path = f'data/raw/weather_{p}_raw.json'
    
    # Ensure raw file exists before attempting processing
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}, skipping...")
        continue
        
    with open(file_path, 'r') as f:
        d = json.load(f)

    # Extract the CSV download URL from the JSON metadata
    url = d["data"][0]["link"][0]["href"]
    print(f"Processing parameter {p} ({parameter_mapping[p]['name']})...")

    res = requests.get(url)
    csv_lines = res.text.split('\n')
    skip_rows_count = 0
    for i, line in enumerate(csv_lines):
        if "Datum" in line:
            skip_rows_count = i
            break

    # Read the CSV file into Pandas using the dynamically calculated skiprows
    df_weather = pd.read_csv(url, sep=';', skiprows=skip_rows_count)

    # Select the first three columns (Date, Time, Value) and exclude trailing metadata
    df_clean = df_weather.iloc[:, [0, 1, 2]].copy()
    df_clean.columns = ['date', 'time', 'value']

    # Combine date and time strings into a standardized datetime object
    df_clean['datetime'] = pd.to_datetime(df_clean['date'] + ' ' + df_clean['time'])

    df_clean['parameter'] = parameter_mapping[p]['name']
    df_clean['unit'] = parameter_mapping[p]['unit']

    # Filter and retain only the final standardized columns
    df_clean = df_clean[['datetime', 'parameter', 'value', 'unit']]
    
    # Append the processed DataFrame to the collection list
    all_dfs.append(df_clean)


if all_dfs:
    df_weather_final = pd.concat(all_dfs, ignore_index=True)
    
    # Since SMHIs historical archive dates back to 1961, old records are filtered out, and
    # only retains data from 2024-01-01 onwards to match the scope of the OpenAQ dataset
    df_weather_final = df_weather_final[df_weather_final['datetime'] >= '2024-01-01']
    
    # Sort the dataset chronologically by timestamp for structured ordering
    df_weather_final = df_weather_final.sort_values(by='datetime').reset_index(drop=True)
    
    # Save the finalized clean data to the processed data directory
    os.makedirs('data/processed', exist_ok=True)
    output_path = 'data/processed/weather_processed.csv'
    df_weather_final.to_csv(output_path, index=False)
    
    print("\nData transformation completed successfully.")
    print(f"Output saved to: {output_path}")
    print(f"Total rows remaining (2024-present): {len(df_weather_final)}")
    
    print("\n--- PREVIEW OF FINAL DATA ---")
    print(df_weather_final.head(5))
else:
    print("Error: No data could be processed.")