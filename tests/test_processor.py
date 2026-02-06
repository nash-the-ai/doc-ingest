"""Tests for the document processor."""

import tempfile
from pathlib import Path

import pytest

from doc_ingest.processor import (
    find_documents,
    get_file_hash,
    SUPPORTED_EXTENSIONS,
)


def test_supported_extensions():
    """Test that we support common document types."""
    assert '.pdf' in SUPPORTED_EXTENSIONS
    assert '.docx' in SUPPORTED_EXTENSIONS
    assert '.txt' in SUPPORTED_EXTENSIONS
    assert '.html' in SUPPORTED_EXTENSIONS


def test_get_file_hash():
    """Test file hashing for deduplication."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content")
        f.flush()
        
        hash1 = get_file_hash(Path(f.name))
        hash2 = get_file_hash(Path(f.name))
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hex length


def test_find_documents():
    """Test document discovery."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "doc.txt").write_text("hello")
        (tmpdir / "doc.pdf").write_text("fake pdf")
        (tmpdir / "subdir").mkdir()
        (tmpdir / "subdir" / "nested.md").write_text("# Markdown")
        (tmpdir / "ignore.xyz").write_text("unknown type")
        
        docs = find_documents(tmpdir)
        
        assert len(docs) == 3
        names = [d.name for d in docs]
        assert "doc.txt" in names
        assert "doc.pdf" in names
        assert "nested.md" in names
        assert "ignore.xyz" not in names


def test_find_documents_empty_dir():
    """Test with empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs = find_documents(Path(tmpdir))
        assert docs == []
