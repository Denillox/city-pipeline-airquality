import json
import os
import requests

parameters = [1, 4, 3, 7]
station = 71420 # Göteborg

for p in parameters:
    url = f"https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/{p}/station/{station}/period/corrected-archive.json"


    res = requests.get(url)
    if res.status_code == 200:
        os.makedirs('data/raw', exist_ok=True)
        with open(f'data/raw/weather_{p}_raw.json', 'w') as f:
            data = res.json()
            json.dump(data, f)
    else:
        print(f"Något gick fel för parameter {p}! Statuskod: {res.status_code}")