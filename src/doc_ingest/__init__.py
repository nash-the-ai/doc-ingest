"""
doc-ingest: Point at a directory of documents. Get a RAG-ready vector store.
"""

from .processor import DocumentProcessor
from .cli import main

__version__ = "0.1.0"
__all__ = ["DocumentProcessor", "main"]
