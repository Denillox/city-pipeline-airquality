import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()
server = os.getenv("DB_SERVER")
db = os.getenv("DB_NAME")

print(f"Server: {server}")
print(f"Database: {db}")

# Connection with the database to insert values (hardcoded for both dim_parameter and dim_station)
connection = pyodbc.connect(f"Driver={{ODBC Driver 18 for SQL Server}};"
                             f"Server={server};"
                             f"Database={db};"
                             f"Trusted_Connection=yes;"
                             f"TrustServerCertificate=yes;"
                             )

# dim_parameter values
parameters = [
    (1, "temperature", "C"),
    (2, "wind_direction", "degrees"),
    (3, "wind_speed", "m/s"),
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

cursor.executemany("INSERT INTO dim_parameter (parameter_id, parameter, unit) VALUES (?, ?, ?)", parameters)
cursor.executemany("INSERT INTO dim_station (station_id, station_name, city, source, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)", stations)

connection.commit()
print("Dimension tables loaded successfully")