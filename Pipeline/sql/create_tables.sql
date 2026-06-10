CREATE DATABASE AirQualityAnalytics;
GO
USE AirQualityAnalytics;
GO

CREATE TABLE dim_parameter (
    parameter_id INT PRIMARY KEY,
    parameter NVARCHAR(20) NOT NULL,
    unit NVARCHAR(20)      NOT NULL
);

CREATE TABLE dim_station (
    station_id INT PRIMARY KEY,
    station_name NVARCHAR(30) NOT NULL,
    city NVARCHAR(30) NOT NULL,
    source NVARCHAR(20),
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT,
    month INT,
    day INT,
    hour INT,
    weekday NVARCHAR(15),
    weekday_number INT
);

CREATE TABLE fact_measurements (
    measurement_id INT PRIMARY KEY,
    value FLOAT NOT NULL,
    date_id INT NOT NULL,
    parameter_id INT NOT NULL,
    station_id INT NOT NULL,
    FOREIGN KEY (parameter_id) REFERENCES dim_parameter (parameter_id),
    FOREIGN KEY (station_id) REFERENCES dim_station (station_id),
    FOREIGN KEY (date_id) REFERENCES dim_date (date_id)
);