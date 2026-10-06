"""
Retrieval engine for agricultural disease knowledge.
Supports crop filtering, semantic similarity search, and score normalization.
"""

from typing import List, Dict, Any, Optional

from ..vectorstore.chroma_store import ChromaStore


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
    "lady_finger": "okra",
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
    "ustilaginoidea": "false_smut",
}


class DiseaseRetriever:
    """Retrieve agricultural disease knowledge from ChromaDB."""

    def __init__(self, persist_dir: Optional[str] = None):
        self.store = ChromaStore(persist_dir=persist_dir)

    @staticmethod
    def normalize_crop_name(crop: Optional[str]) -> str:
        if not crop:
            return "paddy"

        normalized = crop.strip().lower()
        return SUPPORTED_CROP_ALIASES.get(normalized, normalized)

    @staticmethod
    def normalize_disease_name(disease: Optional[str]) -> Optional[str]:
        if not disease:
            return None

        normalized = disease.strip().lower()

        if normalized in {"uncertain", "unknown", "healthy"}:
            return normalized

        return DISEASE_NAME_MAP.get(
            normalized,
            normalized.replace(" ", "_")
        )

    def retrieve(
        self,
        query: str,
        crop: Optional[str] = None,
        disease: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve evidence while keeping results restricted to the requested crop."""

        norm_crop = self.normalize_crop_name(crop)
        norm_disease = self.normalize_disease_name(disease)

        search_query = query.strip() if query else ""

        if not search_query:
            search_query = norm_disease or norm_crop

        filter_clauses = [
            {"crop": norm_crop}
        ]

        if (
            norm_disease
            and norm_disease not in {"uncertain", "unknown", "healthy"}
        ):
            filter_clauses.append({"disease": norm_disease})

        if category:
            filter_clauses.append({"category": category})

        if len(filter_clauses) == 1:
            where_filter = filter_clauses[0]
        else:
            where_filter = {"$and": filter_clauses}

        raw_results = self.store.search(
            query=search_query,
            where_filter=where_filter,
            n_results=top_k,
        )

        documents = raw_results.get("documents", [[]])
        metadatas = raw_results.get("metadatas", [[]])
        distances = raw_results.get("distances", [[]])

        documents = documents[0] if documents else []
        metadatas = metadatas[0] if metadatas else []
        distances = distances[0] if distances else []

        results = []

        for index, document in enumerate(documents):
            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            results.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                    "score": self._normalize_score(distance),
                }
            )

        return results

    @staticmethod
    def _normalize_score(distance: Optional[float]) -> Optional[float]:
        if distance is None:
            return None

        try:
            distance = float(distance)
        except (TypeError, ValueError):
            return None

        # Chroma distance: lower is better.
        # Convert it to a simple bounded similarity-style score.
        return max(0.0, min(1.0, 1.0 / (1.0 + distance)))


def retrieve_disease_information(
    query: str,
    crop: Optional[str] = None,
    disease: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Convenience wrapper used by the main disease pipeline."""

    retriever = DiseaseRetriever()

    return retriever.retrieve(
        query=query,
        crop=crop,
        disease=disease,
        category=category,
        top_k=top_k,
    )