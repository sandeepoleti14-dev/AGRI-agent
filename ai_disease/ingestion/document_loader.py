"""
Document loader module for agricultural documents (PDFs and text files).
Supports PyMuPDF (fitz) and PyPDF with automatic fallback.
"""

import os
from typing import List, Dict, Any
from .text_cleaner import TextCleaner


class DocumentLoader:
    """Loads documents from PDF and text files, returning raw page/document records."""

    def __init__(self):
        self.cleaner = TextCleaner()

    def load_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text and metadata from a PDF file.
        Returns a list of page dicts: [{'page': 1, 'text': '...', 'source': '...'}]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        pages_data = []
        filename = os.path.basename(file_path)

        # Attempt PyMuPDF first
        try:
            import pymupdf
            doc = pymupdf.open(file_path)
            for page_idx, page in enumerate(doc):
                raw_text = page.get_text()
                cleaned_text = self.cleaner.clean(raw_text)
                if cleaned_text:
                    pages_data.append({
                        "page": page_idx + 1,
                        "text": cleaned_text,
                        "source": filename,
                        "file_path": file_path
                    })
            doc.close()
            return pages_data
        except ImportError:
            pass

        # Fallback to pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                raw_text = page.extract_text() or ""
                cleaned_text = self.cleaner.clean(raw_text)
                if cleaned_text:
                    pages_data.append({
                        "page": page_idx + 1,
                        "text": cleaned_text,
                        "source": filename,
                        "file_path": file_path
                    })
            return pages_data
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF {file_path}: {e}")

    def load_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        """Loads all supported PDF documents from a directory."""
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        all_docs = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    full_path = os.path.join(root, file)
                    try:
                        pages = self.load_pdf(full_path)
                        all_docs.extend(pages)
                    except Exception as err:
                        print(f"Warning: Failed loading {file}: {err}")
        return all_docs
