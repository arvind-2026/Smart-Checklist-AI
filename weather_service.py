"""Automatic live weather with location and offline fallbacks."""

import math
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from config import (
    EXTREME_WEATHER_FALLBACK,
    WEATHER_API_URL,
    WEATHER_AUTO_LOCATION_QUERY,
    WEATHER_FALLBACK_CITY,
    WEATHER_FALLBACK_SCENARIO,
    WEATHER_FORECAST_DAYS,
    WEATHER_FORECAST_HOURS,
    WEATHER_REQUEST_TIMEOUT_SECONDS,
)


PROJECT_DIRECTORY = Path(__file__).resolve().parent
PM25_AQI_BREAKPOINTS = [
    (0.0, 9.0, 0, 50),
    (9.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 125.4, 151, 200),
    (125.5, 225.4, 201, 300),
    (225.5, 325.4, 301, 500),
]


def calculate_pm25_aqi(pm25_value):
    """Estimate numeric US AQI from a current PM2.5 concentration."""
    concentration = max(0.0, math.floor(float(pm25_value) * 10) / 10)

    for low_pm, high_pm, low_aqi, high_aqi in PM25_AQI_BREAKPOINTS:
        if low_pm <= concentration <= high_pm:
            scaled_aqi = (
                (high_aqi - low_aqi)
                / (high_pm - low_pm)
                * (concentration - low_pm)
                + low_aqi
            )
            return int(scaled_aqi + 0.5)

    return 500


def load_weather_api_key():
    """Load the WeatherAPI key from the project .env file or environment."""
    load_dotenv(PROJECT_DIRECTORY / ".env")
    return os.getenv("WEATHER_API_KEY")


def parse_live_weather_response(response_data):
    """Summarize the next eight forecast hours for checklist rules."""
    current = response_data["current"]
    location = response_data["location"]
    current_epoch = int(location["localtime_epoch"])
    forecast_hours = []

    for forecast_day in response_data["forecast"]["forecastday"]:
        forecast_hours.extend(forecast_day["hour"])

    next_hours = sorted(
        (hour for hour in forecast_hours if int(hour["time_epoch"]) >= current_epoch),
        key=lambda hour: int(hour["time_epoch"]),
    )[:WEATHER_FORECAST_HOURS]

    if not next_hours:
        raise ValueError("No upcoming hourly forecast was returned")

    pm25_values = [
        hour["air_quality"]["pm2_5"]
        for hour in next_hours
        if hour.get("air_quality") and "pm2_5" in hour["air_quality"]
    ]
    if not pm25_values:
        pm25_values = [current["air_quality"]["pm2_5"]]

    weather_data = {
        "rain_probability": max(int(hour["chance_of_rain"]) for hour in next_hours),
        "uv_index": max(float(hour["uv"]) for hour in next_hours),
        "aqi": calculate_pm25_aqi(max(pm25_values)),
        "temperature_celsius": max(float(hour["temp_c"]) for hour in next_hours),
    }
    location_name = f"{location['name']}, {location['country']}"
    return location_name, weather_data


def fetch_live_weather(location_query, api_key=None):
    """Fetch live weather, returning None instead of stopping the application."""
    if api_key is None:
        api_key = load_weather_api_key()

    if not api_key:
        print("Weather API key is missing. Add WEATHER_API_KEY to the .env file.")
        return None

    parameters = {
        "key": api_key,
        "q": location_query,
        "days": WEATHER_FORECAST_DAYS,
        "aqi": "yes",
        "alerts": "no",
    }

    try:
        response = requests.get(
            WEATHER_API_URL,
            params=parameters,
            timeout=WEATHER_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return parse_live_weather_response(response.json())
    except requests.RequestException as error:
        print(f"Live weather is unavailable: {error}")
    except (KeyError, IndexError, TypeError, ValueError) as error:
        print(f"The live weather response was incomplete: {error}")

    return None


def get_automatic_weather():
    """Try automatic location, New Delhi, then extreme offline weather."""
    automatic_result = fetch_live_weather(WEATHER_AUTO_LOCATION_QUERY)
    if automatic_result is not None:
        location, weather = automatic_result
        return "Automatic live forecast", location, weather

    delhi_result = fetch_live_weather(WEATHER_FALLBACK_CITY)
    if delhi_result is not None:
        location, weather = delhi_result
        return f"{WEATHER_FALLBACK_CITY} fallback forecast", location, weather

    scenario_name = WEATHER_FALLBACK_SCENARIO.replace("_", " ").title()
    return (
        f"{scenario_name} offline fallback",
        WEATHER_FALLBACK_CITY,
        EXTREME_WEATHER_FALLBACK.copy(),
    )
