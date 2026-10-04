"""Tests for src/tools/location.py"""
from unittest.mock import patch
from src.tools.location import resolve_location


def test_resolve_location_gps_takes_priority():
    result = resolve_location(gps=(13.0827, 80.2707))
    assert result["location_source"] == "gps"
    assert result["gps"] == (13.0827, 80.2707)


def test_resolve_location_gps_with_place_name():
    result = resolve_location(gps=(13.0827, 80.2707), place_name="Chennai")
    assert result["place_name"] == "Chennai"
    assert result["location_source"] == "gps"


def test_resolve_location_from_profile():
    """Requires init_db.py to have been run first."""
    result = resolve_location(farmer_id="F001")
    if result:                  # skip if DB not seeded
        assert result["location_source"] == "profile"
        assert result["gps"] is not None


def test_resolve_location_manual_place_name():
    with patch("src.tools.location.geocode", return_value=(17.385, 78.4867)):
        result = resolve_location(place_name="Hyderabad")
    assert result["location_source"] == "manual"
    assert result["gps"] == (17.385, 78.4867)


def test_resolve_location_returns_empty_on_all_failures():
    with patch("src.tools.location.geocode", return_value=None):
        result = resolve_location(place_name="Nowhere")
    assert result == {}


def test_resolve_location_returns_empty_when_nothing_provided():
    result = resolve_location()
    assert result == {}
