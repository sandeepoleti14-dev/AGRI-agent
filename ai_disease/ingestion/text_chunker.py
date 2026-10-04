"""
Modular text chunker for agricultural knowledge documents.
Extracts semantic sections and enriches chunks with disease and crop metadata.
"""

import re
from typing import List, Dict, Any


# Standard recognized diseases in knowledge base
KNOWN_DISEASES = {
    "rice blast": "rice_blast",
    "blast": "rice_blast",
    "pyricularia": "rice_blast",
    "bacterial leaf blight": "bacterial_leaf_blight",
    "bacterial blight": "bacterial_leaf_blight",
    "xanthomonas": "bacterial_leaf_blight",
    "sheath blight": "sheath_blight",
    "rhizoctonia": "sheath_blight",
    "brown spot": "brown_spot",
    "bipolaris": "brown_spot",
    "cochliobolus": "brown_spot",
    "false smut": "false_smut",
    "ustilaginoidea": "false_smut"
}

CATEGORY_KEYWORDS = {
    "symptoms": ["symptom", "lesion", "spot", "identif", "morpholog", "appearance", "damage", "spindle", "ooze", "spore ball"],
    "causes_and_context": ["epidemiol", "cause", "weather", "favor", "humid", "temperat", "trigger", "overwinter", "famine"],
    "cultural_prevention": ["prevent", "cultural", "spacing", "drainage", "fertiliz", "stubble", "weed", "sanitation"],
    "organic_management": ["organic", "biolog", "pseudomonas", "trichoderma", "neem", "cow dung", "bio-agent", "hot water"],
    "chemical_management": ["chemical", "fungicide", "active ingredient", "spray", "tricyclazole", "hexaconazole", "validamycin", "copper hydroxide", "streptocycline", "propiconazole", "thifluzamide", "azoxystrobin"]
}


class TextChunker:
    """Chunks agricultural text into semantically cohesive passages enriched with metadata."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def detect_disease(self, text: str, source: str = "") -> str:
        """Identifies which target disease a text or source belongs to."""
        combined = (source + " " + text[:300]).lower()
        for phrase, disease_id in KNOWN_DISEASES.items():
            if phrase in combined:
                return disease_id
        return "general_paddy_disease"

    def detect_category(self, chunk_text: str) -> str:
        """Classifies chunk into agricultural category."""
        text_lower = chunk_text.lower()
        score_per_cat = {}
        for cat, keywords in CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                score_per_cat[cat] = matches

        if score_per_cat:
            return max(score_per_cat, key=score_per_cat.get)
        return "general_management"

    def chunk_document(self, doc_data: Dict[str, Any], crop: str = "paddy") -> List[Dict[str, Any]]:
        """
        Splits a loaded document page into semantic sections.
        Detects section headings (e.g. '1. Identification...', '2. Environmental Epidemiology...').
        """
        text = doc_data.get("text", "")
        source = doc_data.get("source", "Agricultural Advisory")
        disease_id = self.detect_disease(text, source)

        # Regex split by section headers (e.g., "1. Identification...", "2. Environmental...")
        section_pattern = r'(?=\n?(?:[0-9]+\.\s+[A-Z][^\n]+|Official Agricultural Extension Advisory))'
        raw_sections = re.split(section_pattern, text)

        chunks = []
        chunk_idx = 0

        for raw_sec in raw_sections:
            sec_cleaned = raw_sec.strip()
            if not sec_cleaned or len(sec_cleaned) < 40:
                continue

            # If section is very large, split into sub-chunks
            if len(sec_cleaned) > self.chunk_size * 2:
                paragraphs = [p.strip() for p in sec_cleaned.split("\n\n") if p.strip()]
                for para in paragraphs:
                    if len(para) < 30:
                        continue
                    category = self.detect_category(para)
                    chunk_id = f"{disease_id}_{category}_{chunk_idx}"
                    chunks.append({
                        "id": chunk_id,
                        "text": para,
                        "metadata": {
                            "crop": crop,
                            "disease": disease_id,
                            "category": category,
                            "source": source,
                            "page": doc_data.get("page", 1)
                        }
                    })
                    chunk_idx += 1
            else:
                category = self.detect_category(sec_cleaned)
                chunk_id = f"{disease_id}_{category}_{chunk_idx}"
                chunks.append({
                    "id": chunk_id,
                    "text": sec_cleaned,
                    "metadata": {
                        "crop": crop,
                        "disease": disease_id,
                        "category": category,
                        "source": source,
                        "page": doc_data.get("page", 1)
                    }
                })
                chunk_idx += 1

        return chunks
