"""Central configuration for Smart Checklist AI."""


PROJECT_NAME = "Smart Checklist AI"
PROJECT_SUBTITLE = "A Weather-Aware Visual Readiness Assistant"

# Routine checklists use only classes supported by the bundled YOLO model.
ROUTINE_MODES = {
    "office": ["laptop", "phone", "water_bottle"],
    "college": ["book", "phone", "water_bottle"],
    "travel": ["suitcase", "phone", "water_bottle"],
}

# Detection settings.
WEBCAM_SCAN_DURATION_SECONDS = 30
DETECTION_CONFIDENCE_THRESHOLD = 0.60
SAMPLE_IMAGE_RELATIVE_PATH = "test_media/checklist_items.png"

# Live-weather and fallback settings.
WEATHER_API_URL = "https://api.weatherapi.com/v1/forecast.json"
WEATHER_AUTO_LOCATION_QUERY = "auto:ip"
WEATHER_FORECAST_HOURS = 8
WEATHER_FORECAST_DAYS = 2
WEATHER_REQUEST_TIMEOUT_SECONDS = 10
WEATHER_FALLBACK_CITY = "New Delhi"
WEATHER_FALLBACK_SCENARIO = "extreme"


ENVIRONMENT_THRESHOLDS = {
    "rain_probability": 50,
}


EXTREME_WEATHER_FALLBACK = {
    "rain_probability": 100,
    "uv_index": 11,
    "aqi": 500,
    "temperature_celsius": 45,
}


ENVIRONMENTAL_ALERT_MESSAGES = {
    "umbrella": "Rain alert: umbrella is missing.",
}
