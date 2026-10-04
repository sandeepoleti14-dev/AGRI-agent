"""
Retrieval engine for agricultural disease knowledge.
Supports multi-field filtering, semantic similarity search, and score normalization.
"""

from typing import List, Dict, Any, Optional
from ..vectorstore.chroma_store import ChromaStore
from ..schemas import RetrievalChunk


SUPPORTED_CROP_ALIASES = {
    "rice": "paddy",
    "paddy": "paddy",
    "tamato": "tomato",
    "tomato": "tomato",
    "brinjal": "brinjal",
    "eggplant": "brinjal",
    "chilli": "chilli",
    "chili": "chilli",
    "okra": "okra",
    "ladies finger": "okra",
    "ladyfinger": "okra",
    "ladies_finger": "okra",
    "lady_finger": "okra"
}

DISEASE_NAME_MAP = {
    "rice blast": "rice_blast",
    "blast": "rice_blast",
    "pyricularia": "rice_blast",
    "magnaporthe": "rice_blast",
    "bacterial leaf blight": "bacterial_leaf_blight",
    "bacterial blight": "bacterial_leaf_blight",
    "blb": "bacterial_leaf_blight",
    "xanthomonas": "bacterial_leaf_blight",
    "sheath blight": "sheath_blight",
    "rhizoctonia": "sheath_blight",
    "brown spot": "brown_spot",
    "bipolaris": "brown_spot",
    "sesame spot": "brown_spot",
    "false smut": "false_smut",
    "smut": "false_smut",
    "ustilaginoidea": "false_smut"
}


class DiseaseRetriever:
    """Retrieves grounded agricultural knowledge from ChromaDB collection."""

    def __init__(self, chroma_store: Optional[ChromaStore] = None):
        self.store = chroma_store or ChromaStore()

    def normalize_disease_name(self, disease: Optional[str]) -> Optional[str]:
        """Maps user or model disease names to canonical metadata keys."""
        if not disease:
            return None
        cleaned = disease.strip().lower()
        return DISEASE_NAME_MAP.get(cleaned, cleaned.replace(" ", "_"))

    def normalize_crop_name(self, crop: Optional[str]) -> str:
        """Normalizes crop names used in the multi-crop extension."""
        if not crop:
            return "paddy"
        cleaned = crop.strip().lower().replace("-", " ").replace("_", " ")
        return SUPPORTED_CROP_ALIASES.get(cleaned, cleaned)

    def retrieve(
        self,
        crop: str = "paddy",
        disease: Optional[str] = None,
        query: str = "",
        category: Optional[str] = None,
        top_k: int = 6,
        min_score: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Retrieves relevant agricultural documents matching the crop, disease, and query.
        Returns a list of standardized dicts:
        [
            {
                "content": "...",
                "source": "...",
                "metadata": {...},
                "score": 0.91
            }
        ]
        """
        norm_disease = self.normalize_disease_name(disease)
        norm_crop = self.normalize_crop_name(crop)

        # Build search query string
        search_terms = []
        if norm_crop:
            search_terms.append(norm_crop)
        if disease and disease.lower() not in ["uncertain", "unknown", "healthy"]:
            search_terms.append(disease)
        if query:
            search_terms.append(query)

        search_query = " ".join(search_terms) if search_terms else "paddy disease symptoms and management"

        # Build metadata where filter if specific disease is known
        where_filter = None
        filter_clauses = []
        if norm_disease and norm_disease not in ["uncertain", "unknown", "healthy"]:
            filter_clauses.append({"disease": norm_disease})
        if category:
            filter_clauses.append({"category": category})

        if len(filter_clauses) == 1:
            where_filter = filter_clauses[0]
        elif len(filter_clauses) > 1:
            where_filter = {"$and": filter_clauses}

        # Query vector store
        raw_results = self.store.search(
            query=search_query,
            where_filter=where_filter,
            n_results=top_k
        )

        formatted_results = []
        docs = raw_results.get("documents", [[]])[0]
        metas = raw_results.get("metadatas", [[]])[0]
        distances = raw_results.get("distances", [[]])[0]

        for doc_text, meta, dist in zip(docs, metas, distances):
            # Chroma returns L2 or cosine distance. Normalize to [0.0, 1.0] score
            # For cosine distance, distance is in [0, 2], so score = 1 - dist/2
            score = max(0.0, min(1.0, 1.0 - (dist / 2.0))) if dist is not None else 1.0

            if score < min_score:
                continue

            source = meta.get("source", "Agricultural Research Compendium") if meta else "Agricultural Research Compendium"
            formatted_results.append({
                "content": doc_text,
                "source": source,
                "metadata": meta or {},
                "score": round(score, 3)
            })

        # Sort by relevance score descending
        formatted_results.sort(key=lambda x: x["score"], reverse=True)
        return formatted_results


# Module-level convenience function meeting the specification
_global_retriever: Optional[DiseaseRetriever] = None


def retrieve_disease_information(
    crop: str = "paddy",
    disease: Optional[str] = None,
    query: str = "",
    category: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Public retrieval API required by Phase 4:
    retrieve_disease_information(
        crop="paddy",
        disease="sheath blight",
        query="brown lesions near water level"
    )
    """
    global _global_retriever
    if _global_retriever is None:
        _global_retriever = DiseaseRetriever()

    return _global_retriever.retrieve(
        crop=crop,
        disease=disease,
        query=query,
        category=category,
        top_k=top_k
    )
