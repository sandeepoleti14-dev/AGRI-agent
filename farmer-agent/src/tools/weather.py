"""
Weather tool using Open-Meteo (free, no API key needed).
Returns current conditions + 72-hour forecast.
Fails gracefully — never crashes the graph.
"""

import requests
from src.config import WEATHER_TIMEOUT_SECONDS

GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
UNAVAILABLE = {"status": "weather unavailable"}


def geocode(place_name: str) -> tuple[float, float] | None:
    """Converts a place name string to (lat, lon). Returns None on failure."""
    try:
        resp = requests.get(
            GEOCODE_URL,
            params={"q": place_name, "format": "json", "limit": 1},
            headers={"User-Agent": "farmer-agent/1.0"},
            timeout=WEATHER_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        return None


def get_weather(lat: float, lon: float) -> dict:
    """
    Fetches current weather + 72-hour hourly forecast for (lat, lon).
    Returns UNAVAILABLE dict instead of raising on any failure.
    """
    try:
        resp = requests.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
                "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability",
                "forecast_days": 3,
                "timezone": "auto",
            },
            timeout=WEATHER_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})

        # Summarise 72-hour forecast into max humidity + max rain probability
        humidity_list = hourly.get("relative_humidity_2m", [])
        rain_prob_list = hourly.get("precipitation_probability", [])

        return {
            "status": "ok",
            "current": {
                "temperature_c": current.get("temperature_2m"),
                "humidity_pct": current.get("relative_humidity_2m"),
                "precipitation_mm": current.get("precipitation"),
                "weather_code": current.get("weather_code"),
            },
            "forecast_72h": {
                "max_humidity_pct": max(humidity_list) if humidity_list else None,
                "max_rain_probability_pct": max(rain_prob_list) if rain_prob_list else None,
                "hourly_humidity": humidity_list[:72],
                "hourly_rain_probability": rain_prob_list[:72],
            },
        }
    except Exception:
        return UNAVAILABLE
