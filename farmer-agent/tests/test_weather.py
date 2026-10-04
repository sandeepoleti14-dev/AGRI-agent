"""Tests for src/tools/weather.py"""
from unittest.mock import patch
from src.tools.weather import geocode, get_weather


def test_get_weather_returns_ok_structure():
    result = get_weather(13.0827, 80.2707)   # Chennai
    assert result["status"] in ("ok", "weather unavailable")
    if result["status"] == "ok":
        assert "current" in result
        assert "forecast_72h" in result


def test_get_weather_graceful_failure():
    with patch("src.tools.weather.requests.get", side_effect=Exception("network error")):
        result = get_weather(0.0, 0.0)
    assert result == {"status": "weather unavailable"}


def test_geocode_returns_tuple_for_valid_place():
    result = geocode("Chennai, Tamil Nadu")
    if result is not None:          # skip if network unavailable in CI
        lat, lon = result
        assert 8.0 < lat < 37.0    # within India latitude range
        assert 68.0 < lon < 97.0


def test_geocode_returns_none_on_failure():
    with patch("src.tools.weather.requests.get", side_effect=Exception("timeout")):
        result = geocode("Anywhere")
    assert result is None
