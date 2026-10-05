"""
Fetches farmer profile from SQLite and computes crop growth stage
from the planting date. No LLM involved — pure deterministic logic.
"""

import sqlite3
import hashlib
import hmac
import secrets
from datetime import date, datetime
from pathlib import Path
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
PASSWORD_HASH_ITERATIONS = 310_000


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
    for credential_field in ("password", "password_hash", "password_salt"):
        profile.pop(credential_field, None)
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
        cur.execute("PRAGMA table_info(farmers)")
        columns = {row["name"] for row in cur.fetchall()}
        if not columns:
            conn.close()
            return None

        cur.execute(
            "SELECT * FROM farmers WHERE name = ? COLLATE NOCASE",
            (name,),
        )
        row = cur.fetchone()
        conn.close()
    except sqlite3.Error:
        return None

    if row is None:
        return None

    profile = dict(row)
    stored_hash = profile.get("password_hash")
    salt = profile.get("password_salt")

    if stored_hash and salt:
        supplied_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            PASSWORD_HASH_ITERATIONS,
        ).hex()
        if not hmac.compare_digest(stored_hash, supplied_hash):
            return None
    elif "password" in columns and profile.get("password") == password:
        pass
    else:
        return None

    return _attach_growth_stage(profile)


def register_farmer(
    name: str,
    password: str,
    crop: str,
    soil_type: str,
    planting_date: str,
    place_name: str,
    pincode: str,
) -> dict | None:
    """Create a farmer record and return its public profile, or None if taken."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    ).hex()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                crop TEXT NOT NULL,
                soil_type TEXT NOT NULL,
                planting_date TEXT NOT NULL,
                place_name TEXT NOT NULL,
                pincode TEXT NOT NULL,
                lat REAL,
                lon REAL
            )
            """
        )
        try:
            cursor = conn.execute(
                """
                INSERT INTO farmers (
                    name, password_hash, password_salt, crop,
                    soil_type, planting_date, place_name, pincode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name.strip(),
                    password_hash,
                    salt.hex(),
                    crop,
                    soil_type,
                    planting_date,
                    place_name.strip(),
                    pincode,
                ),
            )
        except sqlite3.IntegrityError:
            conn.rollback()
            return None

        farmer_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()

    return get_farmer_profile(farmer_id)
