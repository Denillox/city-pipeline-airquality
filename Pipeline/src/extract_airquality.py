import json
from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()
api_key = os.getenv("OPENAQ_API_KEY")
headers = {"X-API-KEY": api_key}

# Station: Göteborg Femman
location_id = 2163295
location_url = f"https://api.openaq.org/v3/locations/{location_id}"

print(f"Fetching active sensors for station {location_id}...")
loc_res = requests.get(location_url, headers=headers)

if loc_res.status_code == 200:
    # Get the list with sensors from the API-answer
    sensors = loc_res.json().get("results", [{}])[0].get("sensors", [])
    print(f"Found {len(sensors)} active sensors at the station.")
    
    all_measurements = []
    
    # Loop through each sensor and get the measurement-data
    for sensor in sensors:
        sensor_id = sensor.get("id")
        parameter_name = sensor.get("parameter", {}).get("name")
        print(f" -> Hämtar mätdata för Sensor {sensor_id} ({parameter_name})...")
        
        measurements_url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements?limit=1000"
        meas_res = requests.get(measurements_url, headers=headers)
        
        if meas_res.status_code == 200:
            sensor_data = meas_res.json().get("results", [])
            all_measurements.extend(sensor_data)
        else:
            print(f"Could not fetch data for sensor {sensor_id}. Status: {meas_res.status_code}")
        
        time.sleep(0.5)

    # Save all data to one JSON-file, instead of having three different ones for each sensor
    os.makedirs('data/raw', exist_ok=True)
    output_data = {"results": all_measurements}
    
    with open('data/raw/airquality_raw.json', 'w') as f:
        json.dump(output_data, f)
        
    print(f"Totally {len(all_measurements)} measurements from all sensors has been saved")

else:
    print(f"Could not get the station. Status code: {loc_res.status_code}")
    print(loc_res.text)