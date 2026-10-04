"""
Data schemas for the AI Disease Diagnosis & Management Module (ai_disease).

Defines standard request/response models used across ingestion, vector retrieval,
vision analysis, disease agent, and public pipeline interfaces.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class VisionResult(BaseModel):
    """Output schema from the vision analysis component."""
    crop: str = Field(default="paddy", description="Identified or provided crop type")
    possible_disease: str = Field(..., description="Predicted disease name or 'uncertain' / 'healthy'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    observations: List[str] = Field(default_factory=list, description="Visual observations and morphological traits")


class RetrievalChunk(BaseModel):
    """Schema for retrieved RAG chunks from the vector store."""
    content: str = Field(..., description="Extracted textual content from verified agricultural corpus")
    source: str = Field(..., description="Source citation (e.g., ICAR-NRRI Bulletin, TNAU Agritech)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata such as crop, disease, category")
    score: float = Field(..., description="Similarity or relevance score")


class ChemicalRecommendation(BaseModel):
    """Strict schema for verified chemical management entries."""
    active_ingredient: str = Field(..., description="Verified active chemical ingredient")
    product_name: Optional[str] = Field(default=None, description="Verified commercial product name if documented")
    manufacturer: Optional[str] = Field(default=None, description="Verified manufacturer if documented without marketing hype")
    source: str = Field(..., description="Official agricultural extension source")
    verification_date: Optional[str] = Field(default=None, description="Verification date or year")


class DiseaseAnalysisResult(BaseModel):
    """
    Standard output schema for the analyze_crop() pipeline.
    This schema is frozen and contract-bound for integration by Member 1 (LangGraph).
    """
    crop: str = Field(default="paddy", description="Target crop")
    disease: str = Field(..., description="Identified disease name or 'Healthy' or 'Uncertain'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Diagnosis confidence score")
    observations: List[str] = Field(default_factory=list, description="Visual observations from image analysis")
    symptoms: List[str] = Field(default_factory=list, description="Validated symptoms from agricultural corpus")
    organic_management: List[str] = Field(default_factory=list, description="Cultural, biological, and organic practices")
    chemical_management: List[str] = Field(default_factory=list, description="Evidence-backed chemical treatments")
    evidence: List[str] = Field(default_factory=list, description="Textual evidence retrieved from verified sources")
    sources: List[str] = Field(default_factory=list, description="List of authoritative source citations")
    warning: str = Field(..., description="Advisory disclaimer and guidance verification warning")
    language: str = Field(default="English", description="Response language (e.g., English, Telugu, Hindi)")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to standard dictionary matching integration contract."""
        return {
            "crop": self.crop,
            "disease": self.disease,
            "confidence": round(self.confidence, 2),
            "observations": self.observations,
            "symptoms": self.symptoms,
            "organic_management": self.organic_management,
            "chemical_management": self.chemical_management,
            "evidence": self.evidence,
            "sources": self.sources,
            "warning": self.warning,
            "language": self.language
        }
