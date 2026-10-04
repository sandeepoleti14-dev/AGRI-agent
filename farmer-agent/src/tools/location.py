"""
Resolves the farmer's location from three possible sources (priority order):
  1. GPS coordinates passed directly
  2. Saved profile in SQLite (lat/lon + place_name)
  3. Manual place name typed by the farmer (geocoded)

Returns a dict that maps directly onto State location fields.
"""

from src.tools.weather import geocode
from src.tools.soil_crop import get_farmer_profile


def resolve_location(
    gps: tuple[float, float] | None = None,
    farmer_id: str | None = None,
    place_name: str | None = None,
) -> dict:
    """
    Returns:
        {
            "gps": (lat, lon),
            "place_name": str,
            "location": str,          # display string for UI
            "location_source": str,   # "gps" | "profile" | "manual"
        }
    Falls back to empty dict if nothing resolves.
    """
    # ── 1. GPS passed directly ────────────────────────────────────────────
    if gps and len(gps) == 2:
        lat, lon = gps
        display = f"{lat:.4f}°N, {lon:.4f}°E"
        return {
            "gps": (lat, lon),
            "place_name": place_name or display,
            "location": place_name or display,
            "location_source": "gps",
        }

    # ── 2. Saved farmer profile ───────────────────────────────────────────
    if farmer_id:
        profile = get_farmer_profile(farmer_id)
        if profile and profile.get("lat") and profile.get("lon"):
            lat, lon = profile["lat"], profile["lon"]
            name = profile.get("place_name") or f"{lat:.4f}°N, {lon:.4f}°E"
            return {
                "gps": (lat, lon),
                "place_name": name,
                "location": name,
                "location_source": "profile",
            }

    # ── 3. Manual place name → geocode ────────────────────────────────────
    if place_name:
        coords = geocode(place_name)
        if coords:
            lat, lon = coords
            return {
                "gps": (lat, lon),
                "place_name": place_name,
                "location": place_name,
                "location_source": "manual",
            }

    return {}
