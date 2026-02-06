"""
Document processing and vector store management.
"""

import hashlib
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

console = Console()

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.pdf', '.docx', '.doc', '.pptx', '.ppt',
    '.xlsx', '.xls', '.csv',
    '.html', '.htm', '.xml',
    '.txt', '.md', '.rst',
    '.eml', '.msg',
    '.rtf', '.odt', '.epub',
    '.png', '.jpg', '.jpeg', '.tiff', '.bmp',
    '.json',
}


def get_file_hash(filepath: Path) -> str:
    """Generate MD5 hash for file deduplication."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_documents(directory: Path) -> list[Path]:
    """Recursively find all supported documents in a directory."""
    documents = []
    for ext in SUPPORTED_EXTENSIONS:
        documents.extend(directory.rglob(f"*{ext}"))
        documents.extend(directory.rglob(f"*{ext.upper()}"))
    return sorted(set(documents))


def process_document(
    filepath: Path,
    strategy: str = "auto",
) -> list:
    """
    Parse a single document with Unstructured.
    
    Args:
        filepath: Path to the document
        strategy: Parsing strategy ('auto', 'fast', 'hi_res')
    
    Returns:
        List of document elements
    """
    try:
        elements = partition(
            filename=str(filepath),
            strategy=strategy,
            include_metadata=True,
        )
        
        # Add source file to metadata
        for el in elements:
            el.metadata.filename = filepath.name
            el.metadata.file_path = str(filepath)
        
        return elements
    except Exception as e:
        console.print(f"[red]Failed to parse {filepath.name}: {e}[/red]")
        return []


def chunk_elements(
    elements: list,
    max_chars: int = 1000,
    combine_under: int = 200,
) -> list:
    """
    Chunk document elements for optimal retrieval.
    
    Args:
        elements: List of document elements from Unstructured
        max_chars: Maximum characters per chunk
        combine_under: Combine elements smaller than this
    
    Returns:
        List of chunked elements
    """
    if not elements:
        return []
    
    chunks = chunk_by_title(
        elements,
        max_characters=max_chars,
        new_after_n_chars=int(max_chars * 0.8),
        combine_text_under_n_chars=combine_under,
        multipage_sections=True,
    )
    return chunks


class DocumentProcessor:
    """
    Main document processing and vector store class.
    
    Example:
        processor = DocumentProcessor(output_dir="./vectorstore")
        processor.process_directory("./documents")
        results = processor.query("What is the refund policy?")
    """
    
    def __init__(
        self,
        output_dir: str | Path = "./vectorstore",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
    ):
        """
        Initialize the document processor.
        
        Args:
            output_dir: Directory to store the vector database
            embedding_model: Sentence-transformers model name
            chunk_size: Maximum characters per chunk
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.chunk_size = chunk_size
        
        # Initialize embedding model
        console.print(f"[blue]Loading embedding model: {embedding_model}[/blue]")
        self.embedder = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB with persistent storage
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.output_dir / "chroma"),
            settings=Settings(anonymized_telemetry=False),
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Track processed files to avoid reprocessing
        self.processed_hashes: set = set()
        self._load_processed_hashes()
    
    def _load_processed_hashes(self):
        """Load previously processed file hashes from disk."""
        hash_file = self.output_dir / "processed_hashes.txt"
        if hash_file.exists():
            self.processed_hashes = set(hash_file.read_text().splitlines())
    
    def _save_processed_hash(self, file_hash: str):
        """Save a processed file hash to disk."""
        self.processed_hashes.add(file_hash)
        hash_file = self.output_dir / "processed_hashes.txt"
        with open(hash_file, 'a') as f:
            f.write(f"{file_hash}\n")
    
    def is_processed(self, filepath: Path) -> bool:
        """Check if a file was already processed."""
        return get_file_hash(filepath) in self.processed_hashes
    
    def process_directory(
        self,
        directory: str | Path,
        force: bool = False,
        strategy: str = "auto",
    ) -> int:
        """
        Process all documents in a directory.
        
        Args:
            directory: Path to directory containing documents
            force: If True, reprocess all files even if cached
            strategy: Unstructured parsing strategy
        
        Returns:
            Number of documents processed
        """
        directory = Path(directory)
        
        if not directory.exists():
            console.print(f"[red]Directory not found: {directory}[/red]")
            return 0
        
        # Find documents
        documents = find_documents(directory)
        console.print(f"[green]Found {len(documents)} documents[/green]")
        
        if not documents:
            return 0
        
        # Filter already processed
        if not force:
            to_process = [d for d in documents if not self.is_processed(d)]
            skipped = len(documents) - len(to_process)
            if skipped:
                console.print(f"[yellow]Skipping {skipped} already processed files[/yellow]")
            documents = to_process
        
        if not documents:
            console.print("[green]All documents already processed![/green]")
            return 0
        
        # Process with progress bar
        all_chunks = []
        processed_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing documents...", total=len(documents))
            
            for doc_path in documents:
                progress.update(task, description=f"Processing {doc_path.name[:40]}...")
                
                # Parse document
                elements = process_document(doc_path, strategy=strategy)
                
                if elements:
                    # Chunk for retrieval
                    chunks = chunk_elements(elements, self.chunk_size)
                    
                    # Prepare for storage
                    file_hash = get_file_hash(doc_path)
                    for i, chunk in enumerate(chunks):
                        all_chunks.append({
                            'id': f"{file_hash}_{i}",
                            'text': chunk.text,
                            'metadata': {
                                'source': str(doc_path),
                                'filename': doc_path.name,
                                'chunk_index': i,
                            }
                        })
                    
                    # Mark as processed
                    self._save_processed_hash(file_hash)
                    processed_count += 1
                
                progress.advance(task)
        
        if not all_chunks:
            console.print("[yellow]No content extracted from documents[/yellow]")
            return processed_count
        
        # Generate embeddings
        console.print(f"[blue]Generating embeddings for {len(all_chunks)} chunks...[/blue]")
        
        texts = [c['text'] for c in all_chunks]
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        
        # Store in ChromaDB
        console.print("[blue]Storing in vector database...[/blue]")
        
        self.collection.add(
            ids=[c['id'] for c in all_chunks],
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=[c['metadata'] for c in all_chunks],
        )
        
        console.print(f"[green]✓ Stored {len(all_chunks)} chunks from {processed_count} documents[/green]")
        console.print(f"[green]✓ Vector store: {self.output_dir / 'chroma'}[/green]")
        
        return processed_count
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
    ) -> dict:
        """
        Query the vector store.
        
        Args:
            query_text: The search query
            n_results: Number of results to return
        
        Returns:
            Dictionary with 'documents', 'metadatas', and 'distances'
        """
        query_embedding = self.embedder.encode([query_text])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        return results
    
    def stats(self) -> dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with index statistics
        """
        count = self.collection.count()
        return {
            'documents_indexed': len(self.processed_hashes),
            'total_chunks': count,
            'storage_path': str(self.output_dir / 'chroma'),
        }
    
    def print_stats(self):
        """Print statistics to console."""
        stats = self.stats()
        console.print(f"\n[bold]Vector Store Stats[/bold]")
        console.print(f"  Documents indexed: {stats['documents_indexed']}")
        console.print(f"  Total chunks: {stats['total_chunks']}")
        console.print(f"  Location: {stats['storage_path']}")
