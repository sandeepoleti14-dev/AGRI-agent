"""
Embedding service for agricultural text chunks and user queries.
Utilizes ChromaDB's ONNX-based MiniLM embedding function with a resilient fallback.
"""

from typing import List
import numpy as np


class EmbeddingService:
    """Manages document and query vector generation."""

    def __init__(self):
        self._ef = None
        self._fallback_mode = False
        self._init_embedding_function()

    def _init_embedding_function(self):
        """Initializes the ChromaDB default ONNX embedding function."""
        try:
            from chromadb.utils import embedding_functions
            self._ef = embedding_functions.DefaultEmbeddingFunction()
        except Exception as e:
            print(f"Notice: ChromaDB DefaultEmbeddingFunction fallback active ({e})")
            self._fallback_mode = True

    def _deterministic_hash_vector(self, text: str, dim: int = 384) -> List[float]:
        """Resilient fallback dense embedding based on term hashing & normalization."""
        words = text.lower().split()
        vec = np.zeros(dim, dtype=np.float32)
        if not words:
            return vec.tolist()

        for i, word in enumerate(words):
            h = hash(word) % dim
            pos_weight = 1.0 / (1.0 + 0.05 * i)
            vec[h] += pos_weight

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text chunks."""
        if not texts:
            return []

        if not self._fallback_mode and self._ef is not None:
            try:
                embeddings = self._ef(texts)
                return [list(map(float, emb)) for emb in embeddings]
            except Exception as err:
                print(f"Embedding error: {err}. Switching to fallback vectorizer.")
                self._fallback_mode = True

        return [self._deterministic_hash_vector(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        """Generates embedding for a single query string."""
        results = self.create_embeddings([query])
        return results[0] if results else []
