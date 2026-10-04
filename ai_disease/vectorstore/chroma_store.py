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


class ChromaStore:
    """Manages the paddy_disease_knowledge ChromaDB collection."""

    COLLECTION_NAME = "paddy_disease_knowledge"

    def __init__(self, persist_dir: Optional[str] = None):
        if persist_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_dir = os.path.join(base_dir, "data", "processed", "chroma_db")

        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)

        self.embedding_service = EmbeddingService()
        self.loader = DocumentLoader()
        self.chunker = TextChunker()

        # Initialize Chroma persistent client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Initializes or retrieves the dedicated paddy_disease_knowledge collection."""
        try:
            return self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"description": "ICAR/IRRI Verified Rice Disease Management Knowledge Base"}
            )
        except Exception as e:
            # If collection schema mismatch or corrupt, reset collection cleanly
            print(f"Notice: Resetting Chroma collection due to: {e}")
            try:
                self.client.delete_collection(self.COLLECTION_NAME)
            except Exception:
                pass
            return self.client.create_collection(
                name=self.COLLECTION_NAME,
                metadata={"description": "ICAR/IRRI Verified Rice Disease Management Knowledge Base"}
            )

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Delegates vector embedding computation."""
        return self.embedding_service.create_embeddings(texts)

    def store_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Stores structured chunks into the ChromaDB collection.
        Returns the count of chunks added.
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

            # Chroma metadata values must be primitive types (str, int, float, bool)
            clean_meta = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)

            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(clean_meta)

        embeddings = self.create_embeddings(documents)

        # Upsert into ChromaDB
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        return len(ids)

    def ingest_documents(self, pdf_dir: Optional[str] = None) -> int:
        """
        Full ingestion pipeline:
        PDF -> Text extraction -> Cleaning -> Chunking -> Metadata -> Embeddings -> ChromaDB
        """
        if pdf_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pdf_dir = os.path.join(base_dir, "data", "pdf")

        if not os.path.exists(pdf_dir):
            raise FileNotFoundError(f"PDF directory does not exist: {pdf_dir}")

        docs = self.loader.load_directory(pdf_dir)
        if not docs:
            print(f"Warning: No PDF documents found in {pdf_dir}")
            return 0

        all_chunks = []
        for doc in docs:
            chunks = self.chunker.chunk_document(doc, crop="paddy")
            all_chunks.extend(chunks)

        count = self.store_documents(all_chunks)
        print(f"Ingested {count} chunks into collection '{self.COLLECTION_NAME}'")
        return count

    def search(self, query: str, where_filter: Optional[Dict[str, Any]] = None, n_results: int = 5) -> Dict[str, Any]:
        """Performs semantic similarity search with optional metadata filtering."""
        query_vec = self.embedding_service.embed_query(query)
        kwargs = {
            "query_embeddings": [query_vec],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_filter:
            kwargs["where"] = where_filter

        try:
            return self.collection.query(**kwargs)
        except Exception as e:
            # If where filter failed (e.g. no match for filter), fallback without filter
            print(f"Query with filter failed ({e}), falling back to unconstrained query")
            kwargs.pop("where", None)
            return self.collection.query(**kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the vector store."""
        return {
            "collection_name": self.COLLECTION_NAME,
            "document_count": self.collection.count(),
            "persist_dir": self.persist_dir
        }
