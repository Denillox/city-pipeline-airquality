import pyodbc
from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()
server = os.getenv("DB_SERVER")
db = os.getenv("DB_NAME")

############
# CONNECTION
############

# Connection with the database to insert values (hardcoded for both dim_parameter and dim_station)
connection = pyodbc.connect(f"Driver={{ODBC Driver 18 for SQL Server}};"
                             f"Server={server};"
                             f"Database={db};"
                             f"Trusted_Connection=yes;"
                             f"TrustServerCertificate=yes;"
                             )


################################
# Dimension tables - Static data
################################


# dim_parameter values
parameters = [
    (1, "temperature", "C"),
    (2, "wind_speed", "m/s"),
    (3, "wind_direction", "degrees"),
    (4, "precipitation", "mm"),
    (5, "no2", "µg/m³"),
    (6, "pm10", "µg/m³"),
    (7, "pm25", "µg/m³")
]

# dim_station values
stations = [
    (1, "Göteborg Femman", "Gothenburg", "OpenAQ", 57.7064, 11.9734),
    (2, "Göteborg A", "Gothenburg", "SMHI", 57.7156, 11.9924)
]

cursor = connection.cursor()

# Truncate all tables before reloading to ensure
cursor.execute("DELETE FROM fact_measurements")
cursor.execute("DELETE FROM dim_parameter")
cursor.execute("DELETE FROM dim_station")
cursor.execute("DELETE FROM dim_date")

cursor.executemany("INSERT INTO dim_parameter (parameter_id, parameter, unit) VALUES (?, ?, ?)", parameters)
cursor.executemany("INSERT INTO dim_station (station_id, station_name, city, source, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)", stations)

connection.commit()
print("Dimension tables loaded successfully")

######################################
# dim_date - Built from CSV timestamps
######################################

df_quality = pd.read_csv('Pipeline/data/processed/airquality_clean.csv')
df_weather = pd.read_csv('Pipeline/data/processed/weather_processed.csv')

# Cleaning up and aligning the datetime columns
df_quality['datetime'] = pd.to_datetime(df_quality['datetime']).dt.tz_localize(None)
df_weather['datetime'] = pd.to_datetime(df_weather['datetime'])

df_weather = df_weather[df_weather['datetime'] >= '2024-01-28']

all_datetimes = pd.concat([df_quality['datetime'], df_weather['datetime']]).drop_duplicates().reset_index(drop=True)

dim_date = pd.DataFrame()
dim_date['date_id'] = all_datetimes.dt.strftime('%Y%m%d%H').astype(int)
dim_date['full_date'] = all_datetimes.dt.date
dim_date['year'] = all_datetimes.dt.year
dim_date['month'] = all_datetimes.dt.month
dim_date['day'] = all_datetimes.dt.day
dim_date['hour'] = all_datetimes.dt.hour
dim_date['weekday'] = all_datetimes.dt.day_name()
dim_date['weekday_number'] = all_datetimes.dt.dayofweek + 1

engine = create_engine(f"mssql+pyodbc://{server}/{db}?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes")
dim_date.to_sql('dim_date', con=engine, if_exists='append', index=False)
print("dim_date loaded successfully")


############
# Fact Table
############

df_quality['station_id'] = 1
df_weather['station_id'] = 2
df_quality = df_quality.rename(columns={'parameter_clean': 'parameter'})

df_facts = pd.concat([df_quality, df_weather]).reset_index(drop=True)

parameter_map = {
    "temperature": 1,
    "wind_direction": 2,
    "wind_speed": 3,
    "precipitation": 4,
    "no2": 5,
    "pm10": 6,
    "pm25": 7
}

df_facts['parameter_id'] = df_facts['parameter'].map(parameter_map)
df_facts['date_id'] = df_facts['datetime'].dt.strftime('%Y%m%d%H').astype(int)
df_facts['measurement_id'] = range(1, len(df_facts) + 1)

fact_measurements = df_facts[['measurement_id', 'value', 'date_id', 'parameter_id', 'station_id']]
# print(fact_measurements.head())

fact_measurements.to_sql('fact_measurements', con=engine, if_exists='append', index=False)
print("Fact_measurements loaded successfully")