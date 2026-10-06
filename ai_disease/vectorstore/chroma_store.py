"""
ChromaDB vector store module for agricultural knowledge base.
Encapsulates ChromaDB collection creation, persistent storage, and querying.
"""

import os
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings

from ..embeddings.embedding_service import EmbeddingService
from ..ingestion.document_loader import DocumentLoader
from ..ingestion.text_chunker import TextChunker


CROP_BY_FILENAME = {
    "rice": "paddy",
    "paddy": "paddy",
    "tomato": "tomato",
    "tamato": "tomato",
    "brinjal": "brinjal",
    "eggplant": "brinjal",
    "chilli": "chilli",
    "chili": "chilli",
    "okra": "okra",
    "ladyfinger": "okra",
    "ladies_finger": "okra",
}


def detect_crop_from_source(source: str) -> str:
    """Detect crop from the agricultural document filename."""
    filename = os.path.basename(source).lower()

    for keyword, crop in CROP_BY_FILENAME.items():
        if keyword in filename:
            return crop

    return "paddy"


class ChromaStore:
    """Manages the agricultural disease knowledge ChromaDB collection."""

    COLLECTION_NAME = "paddy_disease_knowledge"

    def __init__(self, persist_dir: Optional[str] = None):
        if persist_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_dir = os.path.join(
                base_dir,
                "data",
                "processed",
                "chroma_db"
            )

        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)

        self.embedding_service = EmbeddingService()
        self.loader = DocumentLoader()
        self.chunker = TextChunker()

        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Initialize or retrieve the agricultural disease collection."""
        try:
            return self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={
                    "description": (
                        "Verified agricultural disease management "
                        "knowledge base"
                    )
                }
            )

        except Exception as e:
            print(f"Notice: Resetting Chroma collection due to: {e}")

            try:
                self.client.delete_collection(self.COLLECTION_NAME)
            except Exception:
                pass

            return self.client.create_collection(
                name=self.COLLECTION_NAME,
                metadata={
                    "description": (
                        "Verified agricultural disease management "
                        "knowledge base"
                    )
                }
            )

    def create_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """Delegate vector embedding computation."""
        return self.embedding_service.create_embeddings(texts)

    def store_documents(
        self,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """
        Store structured chunks into the ChromaDB collection.

        Returns:
            Number of chunks added.
        """
        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = chunk.get("id") or f"chunk_{i}"
            text = chunk.get("text", "")
            meta = chunk.get("metadata", {})

            # Chroma metadata values must be primitive types.
            clean_meta = {}

            for key, value in meta.items():
                if isinstance(value, (str, int, float, bool)):
                    clean_meta[key] = value
                else:
                    clean_meta[key] = str(value)

            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(clean_meta)

        embeddings = self.create_embeddings(documents)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        return len(ids)

    def ingest_documents(
        self,
        pdf_dir: Optional[str] = None
    ) -> int:
        """
        Full ingestion pipeline:

        PDF
          -> Text extraction
          -> Cleaning
          -> Crop detection
          -> Chunking
          -> Metadata
          -> Embeddings
          -> ChromaDB
        """
        if pdf_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pdf_dir = os.path.join(
                base_dir,
                "data",
                "pdf"
            )

        if not os.path.exists(pdf_dir):
            raise FileNotFoundError(
                f"PDF directory does not exist: {pdf_dir}"
            )

        docs = self.loader.load_directory(pdf_dir)

        if not docs:
            print(
                f"Warning: No PDF documents found in {pdf_dir}"
            )
            return 0

        all_chunks = []

        for doc in docs:
            source = doc.get("source", "")
            crop = detect_crop_from_source(source)

            chunks = self.chunker.chunk_document(
                doc,
                crop=crop
            )

            all_chunks.extend(chunks)

        count = self.store_documents(all_chunks)

        print(
            f"Ingested {count} chunks into collection "
            f"'{self.COLLECTION_NAME}'"
        )

        return count

    def search(
        self,
        query: str,
        where_filter: Optional[Dict[str, Any]] = None,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Perform semantic similarity search with optional metadata filtering."""

        query_vec = self.embedding_service.embed_query(query)

        kwargs = {
            "query_embeddings": [query_vec],
            "n_results": n_results,
            "include": [
                "documents",
                "metadatas",
                "distances"
            ]
        }

        if where_filter:
            kwargs["where"] = where_filter

        try:
            return self.collection.query(**kwargs)

        except Exception as e:
            # Do NOT fall back to an unconstrained search.
            # Cross-crop agricultural evidence must never leak
            # into the result when a crop filter is requested.
            print(f"Chroma query failed: {e}")

            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

    def get_stats(self) -> Dict[str, Any]:
        """Return statistics about the vector store."""

        return {
            "collection_name": self.COLLECTION_NAME,
            "document_count": self.collection.count(),
            "persist_dir": self.persist_dir
        }