import json
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ROLE1_ENV_FILE = (
    PROJECT_ROOT
    / "role1-agent-graph"
    / ".env"
)

if ROLE1_ENV_FILE.exists():
    for line in ROLE1_ENV_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        line = line.strip()

        if (
            not line
            or line.startswith("#")
            or "=" not in line
        ):
            continue

        key, value = line.split("=", 1)

        key = key.strip()
        value = (
            value.strip()
            .strip('"')
            .strip("'")
        )

        os.environ.setdefault(
            key,
            value
        )

ROLE3_ROOT = (
    PROJECT_ROOT
    / "role3-agent"
)

sys.path.insert(
    0,
    str(ROLE3_ROOT),
)

from src.tools.weather import (
    geocode,
    get_weather,
)

from src.tools.soil_crop import (
    get_farmer_profile,
    get_farmer_by_name,
)

from src.agents.decision import (
    run_decision_agent,
)


def serialize_result(value):
    if value is None:
        return None

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if isinstance(value, dict):
        return {
            key: serialize_result(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            serialize_result(item)
            for item in value
        ]

    return value


def success_response(result):
    print(
        json.dumps(
            {
                "status": "success",
                "result": serialize_result(result),
            },
            ensure_ascii=False,
        )
    )


def error_response(error):
    print(
        json.dumps(
            {
                "status": "error",
                "error": str(error),
            },
            ensure_ascii=False,
        )
    )


def main():
    raw_input = sys.stdin.read().strip()

    if not raw_input:
        error_response(
            "No input received."
        )
        return

    try:
        request = json.loads(raw_input)

        result = {}

        farmer_id = request.get("farmer_id")
        farmer_name = request.get("farmer_name")
        password = request.get("password")

        farmer_profile = None

        if farmer_id is not None:
            farmer_profile = get_farmer_profile(
                int(farmer_id)
            )

        elif farmer_name and password:
            farmer_profile = get_farmer_by_name(
                farmer_name,
                password,
            )

        result["farmer_profile"] = serialize_result(
            farmer_profile
        )

        weather = None

        lat = request.get("lat")
        lon = request.get("lon")
        place_name = request.get("place_name")

        if (
            lat is not None
            and lon is not None
        ):
            weather = get_weather(
                float(lat),
                float(lon),
            )

        elif place_name:
            coordinates = geocode(place_name)

            if coordinates:
                lat, lon = coordinates

                weather = get_weather(
                    float(lat),
                    float(lon),
                )

        result["weather"] = serialize_result(
            weather
        )

        candidates = request.get(
            "candidates",
            [],
        )

        rag_chunks = request.get(
            "rag_chunks",
            [],
        )

        soil_crop = farmer_profile

        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            decision = run_decision_agent(
                candidates=candidates,
                rag_chunks=rag_chunks,
                weather=weather,
                soil_crop=soil_crop,
            )

        result["decision"] = serialize_result(
            decision
        )

        success_response(result)

    except Exception as error:
        error_response(error)


if __name__ == "__main__":
    main()