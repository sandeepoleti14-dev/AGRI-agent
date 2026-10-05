"""
Shared contract for the entire pipeline.
ALL teammates import State and Decision from here.
Change only after team agreement.

Quick field reference
---------------------
State fields are grouped into 6 sections:
  1. conversation   – raw input from the farmer (text + optional image)
  2. location       – resolved GPS, place name, and how it was sourced
  3. farmer profile – crop/soil fetched from SQLite by soil_crop.py
  4. tool outputs   – weather dict, RAG chunks, disease candidates from vision
  5. final output   – Decision object, verifier result, escalation summary
  6. routing flags  – booleans/strings that drive LangGraph conditional edges

Decision fields:
  candidates       – top 2-3 diseases with confidence % and visual evidence
  evidence[]       – every claim must cite source + page from RAG text only
  actions[]        – ordered by urgency (step 1 = most urgent)
  confidence_score – 0-100; verifier rejects if < 75
  caveats          – limitations / when to seek local advice
  escalate         – True → route to escalation node (KVK contact)
  escalation_reason – required when escalate=True
"""

from __future__ import annotations
from typing import Annotated, Any
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


# ---------------------------------------------------------------------------
# Sub-models used inside Decision
# ---------------------------------------------------------------------------

class EvidenceItem(BaseModel):
    """One cited claim. Every action must be backed by at least one EvidenceItem."""
    claim: str                   # the factual statement being made
    source: str                  # document name e.g. "ICAR Tomato Guide"
    page: str | None = None      # page or section reference if available


class ActionItem(BaseModel):
    """A single recommended action. List is ordered by urgency (step 1 = most urgent)."""
    step: int                    # 1-based ordering; 1 = do this first
    action: str                  # plain-language instruction for the farmer
    chemical: str | None = None  # MUST come verbatim from RAG text — never invented
    dose: str | None = None      # MUST come verbatim from RAG text — never invented


class DiseaseCandidate(BaseModel):
    """One disease hypothesis produced by the vision model (agents/disease.py)."""
    name: str                    # disease name e.g. "Early Blight"
    confidence_pct: float        # 0-100 e.g. 70.0
    visual_evidence: str         # one-line description of what the model observed


# ---------------------------------------------------------------------------
# Decision — structured output of agents/decision.py
# ---------------------------------------------------------------------------

class Decision(BaseModel):
    """
    Final structured recommendation returned by the Decision Agent.
    The Verifier node checks this object before it reaches the frontend.
    """
    candidates: list[DiseaseCandidate] = Field(
        description="Top 2-3 disease candidates ranked by confidence"
    )
    evidence: list[EvidenceItem] = Field(
        description="Every claim must be cited with source + page from RAG chunks"
    )
    actions: list[ActionItem] = Field(
        description="Recommended steps ordered by urgency (step 1 = most urgent)"
    )
    confidence_score: float = Field(
        ge=0.0, le=100.0,
        description="Overall confidence 0-100; verifier rejects if below CONFIDENCE_THRESHOLD"
    )
    caveats: list[str] = Field(
        default_factory=list,
        description="Limitations or conditions that affect the recommendation"
    )
    escalate: bool = Field(
        description="True if farmer should contact KVK / local expert"
    )
    escalation_reason: str | None = Field(
        default=None,
        description="Why escalation is needed — required when escalate=True"
    )


# ---------------------------------------------------------------------------
# State — the LangGraph graph state shared across ALL nodes
# ---------------------------------------------------------------------------

class State(BaseModel):
    """
    Single source of truth passed between every node in the graph.
    Nodes read what they need and write only their own output fields.
    """

    # ── 1. conversation ───────────────────────────────────────────────────
    # messages     : full chat history; LangGraph appends automatically via add_messages
    # farmer_query : raw text the farmer typed — set by the master agent node
    # image_path   : local file path or S3 key; None means no image was uploaded
    messages: Annotated[list[Any], add_messages] = Field(default_factory=list)
    farmer_query: str = ""
    image_path: str | None = None

    # ── 2. location ───────────────────────────────────────────────────────
    # gps             : (lat, lon) tuple populated by tools/location.py
    # place_name      : human-readable name e.g. "Chennai, Tamil Nadu"
    # location        : display string shown in the UI (usually same as place_name)
    # location_source : how location was resolved — "gps" | "profile" | "manual"
    gps: tuple[float, float] | None = None
    place_name: str | None = None
    location: str | None = None
    location_source: str | None = None

    # ── 3. farmer profile (populated by tools/soil_crop.py) ───────────────
    # farmer_id    : autoincrement integer primary key from farmers.db e.g. 1, 2, 3
    #                set after login via get_farmer_by_name() in soil_crop.py
    # crop         : lowercase crop name e.g. "tomato" — used to filter RAG chunks
    # soil_type    : e.g. "red loamy", "black cotton"
    # planting_date: ISO string "YYYY-MM-DD"; used to compute growth_stage
    # growth_stage : computed by soil_crop.py e.g. "Flowering", "Vegetative"
    # pincode      : farmer's area pincode — used to geocode lat/lon at signup
    farmer_id: int | None = None
    crop: str | None = None
    soil_type: str | None = None
    planting_date: str | None = None
    growth_stage: str | None = None
    pincode: int | None = None

    # ── 4. tool outputs ───────────────────────────────────────────────────
    # weather           : dict from tools/weather.py
    #                     keys: status, current, forecast_72h
    #                     always set — either real data or {"status": "weather unavailable"}
    # rag_chunks        : list of dicts from rag/retriever.py
    #                     each chunk has keys: text, source, page, crop
    # disease_candidates: list of DiseaseCandidate set by agents/disease.py
    #                     decision.py reads this — do not rename fields
    weather: dict[str, Any] | None = None
    rag_chunks: list[dict[str, Any]] = Field(default_factory=list)
    disease_candidates: list[DiseaseCandidate] = Field(default_factory=list)

    # ── 5. final output ───────────────────────────────────────────────────
    # decision           : filled by agents/decision.py; read by verifier + frontend
    # verifier_passed    : set by agents/verifier.py; None = not yet checked
    # escalation_summary : filled by agents/escalation.py when escalate=True
    decision: Decision | None = None
    verifier_passed: bool | None = None
    escalation_summary: str | None = None

    # ── 6. routing flags (read by graph/routing.py) ───────────────────────
    # needs_image         : True → master agent asks farmer to upload a photo
    # clarifying_question : non-None → graph pauses and surfaces this to the farmer
    # skip_disease        : True → bypass disease + vision nodes (e.g. market query)
    needs_image: bool = False
    clarifying_question: str | None = None
    skip_disease: bool = False

    class Config:
        arbitrary_types_allowed = True
