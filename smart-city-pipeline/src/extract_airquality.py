import json
from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()
api_key = os.getenv("OPENAQ_API_KEY")
headers = {"X-API-KEY": api_key}

# 1. Vi utgår från stationens ID (Göteborg Femman)
location_id = 2163295
location_url = f"https://api.openaq.org/v3/locations/{location_id}"

print(f"Hämtar aktuella sensorer för station {location_id}...")
loc_res = requests.get(location_url, headers=headers)

if loc_res.status_code == 200:
    # Hämta listan med sensorer dynamiskt från API-svaret
    sensors = loc_res.json().get("results", [{}])[0].get("sensors", [])
    print(f"Hittade {len(sensors)} aktiva sensorer på stationen.")
    
    all_measurements = []

    # 2. Loopa igenom varje sensor och hämta mätdata
    for sensor in sensors:
        sensor_id = sensor.get("id")
        parameter_name = sensor.get("parameter", {}).get("name")
        print(f" -> Hämtar mätdata för Sensor {sensor_id} ({parameter_name})...")
        
        measurements_url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements?limit=1000"
        meas_res = requests.get(measurements_url, headers=headers)
        
        if meas_res.status_code == 200:
            sensor_data = meas_res.json().get("results", [])
            # .extend() lägger till alla mätobjekt i vår gemensamma lista
            all_measurements.extend(sensor_data)
        else:
            print(f"    [!] Kunde inte hämta data för sensor {sensor_id}. Status: {meas_res.status_code}")
        
        # En liten paus (0.5 sek) så vi är snälla mot API:et (Rate limiting)
        time.sleep(0.5)

    # 3. Spara ALL samlad mätdata till en och samma JSON-fil
    os.makedirs('data/raw', exist_ok=True)
    output_data = {"results": all_measurements}
    
    with open('data/raw/airquality_raw.json', 'w') as f:
        json.dump(output_data, f)
        
    print(f"Totalt {len(all_measurements)} mätvärden från alla sensorer har sparats!")

else:
    print(f"Kunde inte hämta station. Statuskod: {loc_res.status_code}")
    print(loc_res.text)