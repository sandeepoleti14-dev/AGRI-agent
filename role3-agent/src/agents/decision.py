"""
Decision Agent — synthesises vision candidates, RAG chunks, weather,
and soil/crop profile into a validated Decision schema.

Hard rule enforced here AND in the prompt:
chemical names/doses must come from RAG text only.
"""

import json
from pathlib import Path

from google import genai

from src.config import (
    DECISION_MODEL,
    GEMINI_API_KEY,
)

from src.schemas import (
    Decision,
    DiseaseCandidate,
    EvidenceItem,
    ActionItem,
)


_client = genai.Client(
    api_key=GEMINI_API_KEY
)

_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "decision.txt"
)

_SYSTEM_PROMPT = _PROMPT_PATH.read_text(
    encoding="utf-8"
)


def _normalise_candidates(
    candidates: list[DiseaseCandidate | dict],
) -> list[DiseaseCandidate]:

    normalised = []

    for candidate in candidates:

        if isinstance(
            candidate,
            DiseaseCandidate,
        ):
            normalised.append(candidate)

        elif isinstance(
            candidate,
            dict,
        ):
            normalised.append(
                DiseaseCandidate(
                    **candidate
                )
            )

        else:
            raise TypeError(
                "Invalid disease candidate type: "
                f"{type(candidate).__name__}"
            )

    return normalised


def _build_prompt(
    candidates: list[DiseaseCandidate | dict],
    rag_chunks: list[dict],
    weather: dict | None,
    soil_crop: dict | None,
) -> str:

    normalised_candidates = (
        _normalise_candidates(
            candidates
        )
    )

    return f"""{_SYSTEM_PROMPT}

DISEASE_CANDIDATES:
{json.dumps(
    [
        candidate.model_dump()
        for candidate in normalised_candidates
    ],
    indent=2
)}

RAG_CHUNKS:
{json.dumps(
    rag_chunks,
    indent=2
)}

WEATHER:
{json.dumps(
    weather or {
        "status": "weather unavailable"
    },
    indent=2
)}

SOIL_CROP:
{json.dumps(
    soil_crop or {},
    indent=2
)}

Return only the JSON object. No explanation outside the JSON.
""".strip()


def run_decision_agent(
    candidates: list[DiseaseCandidate | dict],
    rag_chunks: list[dict],
    weather: dict | None,
    soil_crop: dict | None,
) -> Decision:

    """
    Calls Gemini and parses the response into
    a validated Decision schema.

    Accepts both:
    - DiseaseCandidate objects
    - normal Python dictionaries
    """

    response = _client.models.generate_content(
        model=DECISION_MODEL,
        contents=_build_prompt(
            candidates,
            rag_chunks,
            weather,
            soil_crop,
        ),
    )

    raw = (
        response.text or ""
    ).strip()


    # -----------------------------------------------------
    # Remove markdown code fences if Gemini returns them
    # -----------------------------------------------------

    if raw.startswith("```"):

        parts = raw.split("```")

        if len(parts) >= 3:
            raw = parts[1]

        if raw.startswith("json"):
            raw = raw[4:]

        raw = raw.strip()


    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    try:

        data = json.loads(
            raw
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "Decision agent returned invalid JSON: "
            f"{error}\nRaw: {raw}"
        ) from error


    # -----------------------------------------------------
    # Validate Decision schema
    # -----------------------------------------------------

    try:

        decision = Decision(
            candidates=[
                DiseaseCandidate(**candidate)
                for candidate in data.get(
                    "candidates",
                    [],
                )
            ],

            evidence=[
                EvidenceItem(**evidence)
                for evidence in data.get(
                    "evidence",
                    [],
                )
            ],

            actions=[
                ActionItem(**action)
                for action in data.get(
                    "actions",
                    [],
                )
            ],

            confidence_score=data.get(
                "confidence_score",
                0.0,
            ),

            caveats=data.get(
                "caveats",
                [],
            ),

            escalate=data.get(
                "escalate",
                True,
            ),

            escalation_reason=data.get(
                "escalation_reason"
            ),
        )

        return decision

    except Exception as error:

        raise ValueError(
            "Decision agent returned JSON "
            "that does not match the Decision schema: "
            f"{error}\nData: {json.dumps(data, indent=2)}"
        ) from error