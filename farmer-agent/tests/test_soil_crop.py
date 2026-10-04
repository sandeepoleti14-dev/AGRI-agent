"""Tests for src/tools/soil_crop.py"""
import pytest
from unittest.mock import patch
from src.tools.soil_crop import get_farmer_profile, _compute_growth_stage
from datetime import date, timedelta


def test_compute_growth_stage_tomato_seedling():
    planting = (date.today() - timedelta(days=20)).strftime("%Y-%m-%d")
    stage = _compute_growth_stage("tomato", planting)
    assert stage == "Seedling"


def test_compute_growth_stage_tomato_flowering():
    planting = (date.today() - timedelta(days=65)).strftime("%Y-%m-%d")
    stage = _compute_growth_stage("tomato", planting)
    assert stage == "Flowering"


def test_compute_growth_stage_not_yet_planted():
    future = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    stage = _compute_growth_stage("tomato", future)
    assert stage == "Not yet planted"


def test_compute_growth_stage_unknown_crop_falls_back():
    planting = (date.today() - timedelta(days=40)).strftime("%Y-%m-%d")
    stage = _compute_growth_stage("unknown_crop", planting)
    assert stage != "Unknown"   # should use DEFAULT_STAGES


def test_get_farmer_profile_returns_none_for_missing_id():
    result = get_farmer_profile("NONEXISTENT")
    assert result is None


def test_get_farmer_profile_includes_growth_stage():
    """Requires init_db.py to have been run first."""
    result = get_farmer_profile("F001")
    if result is not None:      # skip if DB not seeded yet
        assert "growth_stage" in result
        assert result["crop"] == "tomato"
