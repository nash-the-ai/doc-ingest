"""
doc-ingest: Point at a directory of documents. Get a RAG-ready vector store.
"""

from .cli import main
from .processor import DocumentProcessor

__version__ = "0.1.0"
__all__ = ["DocumentProcessor", "main"]
