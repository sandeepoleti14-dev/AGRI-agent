"""
Main public entry point for Part 2: RAG + Vision module (ai_disease).

Provides the single analyze_crop() interface required by Member 1 for LangGraph integration:

    IMAGE
      ↓
    VISION ANALYSIS
      ↓
    POSSIBLE DISEASE + CONFIDENCE + OBSERVATIONS
      ↓
    RAG RETRIEVAL
      ↓
    RELEVANT AGRICULTURAL EVIDENCE
      ↓
    DISEASE AGENT
      ↓
    STRUCTURED RESULT
"""

import os
import re
from typing import Dict, Any, Optional

from .schemas import DiseaseAnalysisResult
from .vision.disease_vision import DiseaseVision
from .retrieval.retriever import retrieve_disease_information
from .agent.disease_agent import DiseaseAgent

SUPPORTED_CROP_ALIASES = {
    "paddy": "paddy",
    "rice": "paddy",
    "tomato": "tomato",
    "tamato": "tomato",
    "brinjal": "brinjal",
    "eggplant": "brinjal",
    "chilli": "chilli",
    "chili": "chilli",
    "okra": "okra",
    "ladyfinger": "okra",
    "ladies finger": "okra",
    "ladies_finger": "okra",
    "lady_finger": "okra"
}

SUPPORTED_LANGUAGES = {
    "english": "English",
    "telugu": "Telugu",
    "hindi": "Hindi",
    "tamil": "Tamil"
}


# Re-usable module instances for high performance
_vision_analyzer: Optional[DiseaseVision] = None
_disease_agent: Optional[DiseaseAgent] = None


def normalize_crop_name(crop: Optional[str]) -> str:
    """Canonicalizes crop names and supports the new crop set alongside paddy."""
    if not crop:
        return "paddy"
    cleaned = crop.strip().lower().replace("-", " ").replace("_", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return SUPPORTED_CROP_ALIASES.get(cleaned, cleaned)


def normalize_language_name(language: Optional[str]) -> str:
    """Canonicalizes the supported language names."""
    if not language:
        return "English"
    normalized = language.strip().lower()
    return SUPPORTED_LANGUAGES.get(normalized, "English")


def get_vision_analyzer() -> DiseaseVision:
    global _vision_analyzer
    if _vision_analyzer is None:
        _vision_analyzer = DiseaseVision()
    return _vision_analyzer


def get_disease_agent() -> DiseaseAgent:
    global _disease_agent
    if _disease_agent is None:
        _disease_agent = DiseaseAgent()
    return _disease_agent


def analyze_crop(
    image_path: Optional[str] = None,
    crop: Optional[str] = "paddy",
    language: str = "English",
    query: Optional[str] = None
) -> Dict[str, Any]:
    """
    ONE PUBLIC FUNCTION FOR ALL INTEGRATION.

    Analyzes a crop leaf image or symptom query, retrieves verified agricultural
    evidence from ChromaDB, and returns an evidence-backed structured diagnosis.

    Parameters:
        image_path: Local filepath to the leaf/crop photograph (optional if query is provided)
        crop: Crop name (defaults to 'paddy' if omitted)
        language: Desired output language ('English', 'Telugu', 'Hindi', etc.)
        query: Optional text symptom query (used when image is omitted or as additional context)

    Returns:
        Structured dictionary matching Phase 7 schema:
        {
            "crop": "paddy",
            "disease": "Sheath Blight",
            "confidence": 0.87,
            "observations": [...],
            "symptoms": [...],
            "organic_management": [...],
            "chemical_management": [...],
            "evidence": [...],
            "sources": [...],
            "warning": "...",
            "language": "English"
        }
    """
    # Normalize inputs
    crop_name = normalize_crop_name(crop)
    output_language = normalize_language_name(language)

    vision_module = get_vision_analyzer()
    agent_module = get_disease_agent()

    # Phase 11: Error handling - Empty inputs
    if not image_path and not query:
        return DiseaseAnalysisResult(
            crop=crop_name,
            disease="Uncertain",
            confidence=None,
            observations=["Neither crop photograph nor text symptom query was provided"],
            symptoms=[],
            organic_management=[],
            chemical_management=[],
            evidence=[],
            sources=[],
            warning="Please provide an image of the affected plant or a description of the symptoms.",
            language=output_language
        ).to_dict()

    # Step 1: Vision Analysis (or query-based symptom extraction)
    vision_result: Dict[str, Any] = {}
    if image_path:
        # Check image existence
        if not os.path.exists(image_path):
            return DiseaseAnalysisResult(
                crop=crop_name,
                disease="Uncertain",
                confidence=None,
                observations=[f"Image file not found: {image_path}"],
                symptoms=[],
                organic_management=[],
                chemical_management=[],
                evidence=[],
                sources=[],
                warning="Specified image file does not exist on disk. Please check the path.",
                language=output_language
            ).to_dict()

        try:
            vision_result = vision_module.analyze_image(image_path=image_path, crop=crop_name)
            vision_result["input_mode"] = "image_and_text" if query else "image"
        except (OSError, ValueError) as vision_err:
            return DiseaseAnalysisResult(
                crop=crop_name,
                disease="Uncertain",
                confidence=None,
                observations=[f"Image analysis error: {str(vision_err)}"],
                symptoms=[],
                organic_management=[],
                chemical_management=[],
                evidence=[],
                sources=[],
                warning="Failed to decode or inspect image. Please verify file format (JPG, PNG, WEBP).",
                language=output_language
            ).to_dict()
    else:
        vision_result = {
            "crop": crop_name,
            "possible_disease": "uncertain",
            "confidence": None,
            "input_mode": "text",
            "observations": [f"Farmer-reported symptoms (not visually verified): {query}"]
        }

    possible_disease = vision_result.get("possible_disease", "uncertain")
    raw_confidence = vision_result.get("confidence")
    try:
        confidence = float(raw_confidence) if raw_confidence is not None else None
    except (TypeError, ValueError):
        confidence = None

    # Step 2: RAG Retrieval
    retrieved_evidence = []
    has_disease_prediction = (
        possible_disease.lower() not in ["healthy", "uncertain", "unknown"]
        and confidence is not None
        and confidence > 0.30
    )
    if has_disease_prediction or query:
        query_parts = []
        if has_disease_prediction:
            query_parts.append(possible_disease)
        query_parts.extend(vision_result.get("observations", []))
        if query:
            query_parts.append(query)

        try:
            retrieved_evidence = retrieve_disease_information(
                crop=crop_name,
                disease=possible_disease if has_disease_prediction else None,
                query=" ".join(query_parts),
                top_k=8
            )
        except Exception as rag_err:
            print(f"Warning: ChromaDB retrieval failed: {rag_err}")
            retrieved_evidence = []

    # Step 3: Disease Agent Grounded Synthesis
    result_dict = agent_module.process(
        vision_result=vision_result,
        retrieved_evidence=retrieved_evidence,
        crop=crop_name,
        language=output_language
    )

    return result_dict
