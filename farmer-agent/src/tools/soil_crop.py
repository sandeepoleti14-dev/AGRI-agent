"""
Fetches farmer profile from SQLite and computes crop growth stage
from the planting date. No LLM involved — pure deterministic logic.
"""

import sqlite3
from datetime import date, datetime
from src.config import DB_PATH


# ---------------------------------------------------------------------------
# Growth stage thresholds (days after planting) — per crop
# ---------------------------------------------------------------------------

GROWTH_STAGES: dict[str, list[tuple[int, str]]] = {
    "tomato":  [(0, "Germination"), (14, "Seedling"), (35, "Vegetative"),
                (60, "Flowering"), (80, "Fruit Set"), (110, "Maturity")],
    "brinjal": [(0, "Germination"), (14, "Seedling"), (30, "Vegetative"),
                (55, "Flowering"), (75, "Fruit Development"), (100, "Maturity")],
    "okra":    [(0, "Germination"), (10, "Seedling"), (25, "Vegetative"),
                (40, "Flowering"), (55, "Pod Development"), (70, "Maturity")],
    "chilli":  [(0, "Germination"), (14, "Seedling"), (35, "Vegetative"),
                (60, "Flowering"), (85, "Fruit Set"), (120, "Maturity")],
    "paddy":   [(0, "Germination"), (7, "Seedling"), (30, "Tillering"),
                (60, "Panicle Initiation"), (75, "Flowering"), (110, "Maturity")],
}

DEFAULT_STAGES: list[tuple[int, str]] = [
    (0, "Germination"), (14, "Seedling"), (35, "Vegetative"),
    (60, "Flowering"), (90, "Maturity"),
]


def _compute_growth_stage(crop: str, planting_date_str: str) -> str:
    try:
        planted = datetime.strptime(planting_date_str, "%Y-%m-%d").date()
    except ValueError:
        return "Unknown"

    days = (date.today() - planted).days
    if days < 0:
        return "Not yet planted"

    stages = GROWTH_STAGES.get(crop.lower(), DEFAULT_STAGES)
    stage = stages[0][1]
    for threshold, name in stages:
        if days >= threshold:
            stage = name
    return stage


def _attach_growth_stage(profile: dict) -> dict:
    profile.pop("password", None)   # never expose password outside auth
    profile["growth_stage"] = _compute_growth_stage(
        profile.get("crop", ""), profile.get("planting_date", "")
    )
    return profile


def get_farmer_profile(farmer_id: int) -> dict | None:
    """
    Fetch profile by numeric ID (autoincrement primary key).
    Returns profile dict with growth_stage added, or None if not found.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM farmers WHERE id = ?", (farmer_id,))
        row = cur.fetchone()
        conn.close()
    except sqlite3.Error:
        return None

    if row is None:
        return None

    return _attach_growth_stage(dict(row))


def get_farmer_by_name(name: str, password: str) -> dict | None:
    """
    Used by frontend login — matches name + password.
    Returns profile (without password) or None if credentials are wrong.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM farmers WHERE name = ? AND password = ?",
            (name, password),
        )
        row = cur.fetchone()
        conn.close()
    except sqlite3.Error:
        return None

    if row is None:
        return None

    return _attach_growth_stage(dict(row))
