"""
Decision Agent — synthesises vision candidates, RAG chunks, weather,
and soil/crop profile into a validated Decision schema.

Hard rule enforced here AND in the prompt:
  chemical names/doses must come from RAG text only.
"""

import json
from pathlib import Path
from google import genai
from src.config import DECISION_MODEL, GEMINI_API_KEY
from src.schemas import Decision, DiseaseCandidate, EvidenceItem, ActionItem

_client = genai.Client(api_key=GEMINI_API_KEY)
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "decision.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def _build_prompt(
    candidates: list[DiseaseCandidate],
    rag_chunks: list[dict],
    weather: dict | None,
    soil_crop: dict | None,
) -> str:
    return f"""{_SYSTEM_PROMPT}

DISEASE_CANDIDATES:
{json.dumps([c.model_dump() for c in candidates], indent=2)}

RAG_CHUNKS:
{json.dumps(rag_chunks, indent=2)}

WEATHER:
{json.dumps(weather or {"status": "weather unavailable"}, indent=2)}

SOIL_CROP:
{json.dumps(soil_crop or {}, indent=2)}

Return only the JSON object. No explanation outside the JSON.
""".strip()


def run_decision_agent(
    candidates: list[DiseaseCandidate],
    rag_chunks: list[dict],
    weather: dict | None,
    soil_crop: dict | None,
) -> Decision:
    """
    Calls Gemini and parses the response into a validated Decision object.
    Raises ValueError if the model returns unparseable or schema-invalid JSON.
    """
    response = _client.models.generate_content(
        model=DECISION_MODEL,
        contents=_build_prompt(candidates, rag_chunks, weather, soil_crop),
    )

    raw = response.text.strip()

    # Strip markdown code fences if the model wraps output in ```json ... ```
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Decision agent returned invalid JSON: {e}\nRaw: {raw}") from e

    return Decision(
        candidates=[DiseaseCandidate(**c) for c in data["candidates"]],
        evidence=[EvidenceItem(**e) for e in data["evidence"]],
        actions=[ActionItem(**a) for a in data["actions"]],
        confidence_score=data["confidence_score"],
        caveats=data.get("caveats", []),
        escalate=data["escalate"],
        escalation_reason=data.get("escalation_reason"),
    )
