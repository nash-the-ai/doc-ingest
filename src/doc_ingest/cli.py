"""
Command-line interface for doc-ingest.
"""

from typing import Optional

import click
from rich.console import Console

from .processor import DocumentProcessor

console = Console()


@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option(
    '--output', '-o',
    default='./vectorstore',
    help='Output directory for vector store',
    type=click.Path(),
)
@click.option(
    '--chunk-size', '-c',
    default=1000,
    help='Maximum chunk size in characters',
    type=int,
)
@click.option(
    '--model', '-m',
    default='all-MiniLM-L6-v2',
    help='Sentence-transformers embedding model',
)
@click.option(
    '--query', '-q',
    default=None,
    help='Query the index after processing',
)
@click.option(
    '--n-results', '-n',
    default=5,
    help='Number of results to return for queries',
    type=int,
)
@click.option(
    '--force', '-f',
    is_flag=True,
    help='Reprocess all files (ignore cache)',
)
@click.option(
    '--strategy',
    default='auto',
    type=click.Choice(['auto', 'fast', 'hi_res']),
    help='Document parsing strategy',
)
@click.option(
    '--stats', '-s',
    is_flag=True,
    help='Show index statistics',
)
def main(
    directory: str,
    output: str,
    chunk_size: int,
    model: str,
    query: Optional[str],
    n_results: int,
    force: bool,
    strategy: str,
    stats: bool,
):
    """
    Process a directory of documents into a RAG-ready vector store.

    \b
    Examples:
        doc-ingest ./documents
        doc-ingest ./documents --output ./my-index
        doc-ingest ./documents --query "What is the refund policy?"
        doc-ingest ./documents --force --chunk-size 1500
    """
    console.print("\n[bold]doc-ingest[/bold] - Document Ingestion Pipeline\n")

    # Initialize processor
    processor = DocumentProcessor(
        output_dir=output,
        embedding_model=model,
        chunk_size=chunk_size,
    )

    # Process directory
    processor.process_directory(
        directory,
        force=force,
        strategy=strategy,
    )

    # Show stats if requested
    if stats:
        processor.print_stats()

    # Run query if provided
    if query:
        console.print(f"\n[bold]Query:[/bold] {query}\n")
        results = processor.query(query, n_results=n_results)

        if not results['documents'][0]:
            console.print("[yellow]No results found[/yellow]")
            return

        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            score = 1 - dist  # Convert distance to similarity
            console.print(f"[cyan]Result {i+1}[/cyan] (score: {score:.3f})")
            console.print(f"  Source: {meta['filename']}")
            console.print(f"  {doc[:300]}{'...' if len(doc) > 300 else ''}\n")


if __name__ == '__main__':
    main()
