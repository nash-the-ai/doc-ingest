# doc-ingest

Point at a directory of documents. Get a RAG-ready vector store.

```bash
doc-ingest ./my-documents --query "What is the vacation policy?"
```

## What It Does

1. **Scans** your directory recursively for documents (PDFs, Word, HTML, images, etc.)
2. **Parses** each file using [Unstructured](https://github.com/Unstructured-IO/unstructured)
3. **Chunks** content intelligently for retrieval
4. **Embeds** chunks using sentence-transformers
5. **Stores** everything in a local ChromaDB vector store
6. **Queries** with semantic search

No cloud services required. Everything runs locally.

## Installation

### 1. Install the package

```bash
pip install -e .
```

### 2. Install system dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils tesseract-ocr libmagic-dev
```

**macOS:**
```bash
brew install poppler tesseract libmagic
```

**Optional (for more file types):**
```bash
# MS Office .doc files
sudo apt-get install libreoffice

# EPUBs, RTFs
sudo apt-get install pandoc
```

## Usage

### Process a directory

```bash
# Basic usage - processes ./documents, stores in ./vectorstore
doc-ingest ./documents

# Custom output location
doc-ingest ./documents --output ./my-index

# Larger chunks (default is 1000 chars)
doc-ingest ./documents --chunk-size 1500
```

### Query your documents

```bash
# Process and query
doc-ingest ./documents --query "What are the payment terms?"

# Query an existing index (no reprocessing)
doc-ingest ./documents --query "refund policy"
```

### Options

```
Usage: doc-ingest [OPTIONS] DIRECTORY

Options:
  -o, --output PATH      Output directory for vector store [default: ./vectorstore]
  -c, --chunk-size INT   Maximum chunk size in characters [default: 1000]
  -m, --model TEXT       Sentence-transformers model [default: all-MiniLM-L6-v2]
  -q, --query TEXT       Query the index after processing
  -n, --n-results INT    Number of results to return [default: 5]
  -f, --force            Reprocess all files (ignore cache)
  -s, --stats            Show index statistics
  --help                 Show this message and exit
```

## Supported File Types

| Type | Extensions |
|------|------------|
| PDF | `.pdf` |
| Word | `.docx`, `.doc` |
| PowerPoint | `.pptx`, `.ppt` |
| Excel | `.xlsx`, `.xls`, `.csv` |
| Web | `.html`, `.htm`, `.xml` |
| Text | `.txt`, `.md`, `.rst` |
| Email | `.eml`, `.msg` |
| Images (OCR) | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp` |
| Other | `.rtf`, `.odt`, `.epub`, `.json` |

## Examples

### Build a knowledge base from your docs folder

```bash
doc-ingest ~/Documents/work --output ~/.local/share/work-kb
```

### Search your research papers

```bash
doc-ingest ./papers --query "transformer attention mechanism"
```

### Process with better (but slower) embeddings

```bash
doc-ingest ./documents --model all-mpnet-base-v2
```

### Force reprocess everything

```bash
doc-ingest ./documents --force
```

## How It Works

```
┌─────────────────┐
│  Your Documents │
│  (PDF, DOCX...) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Unstructured  │  ← Extracts text, preserves structure
│     Parser      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Chunking     │  ← Splits into retrieval-sized pieces
│  (by title/size)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Embeddings    │  ← Converts text to vectors
│ (sent-transf.)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    ChromaDB     │  ← Stores vectors for fast retrieval
│  Vector Store   │
└─────────────────┘
```

## Using the Index Programmatically

```python
from doc_ingest import DocumentProcessor

# Load existing index
processor = DocumentProcessor(output_dir="./vectorstore")

# Query
results = processor.query("What is the cancellation policy?", n_results=5)

for doc, metadata, distance in zip(
    results['documents'][0],
    results['metadatas'][0], 
    results['distances'][0]
):
    print(f"Score: {1-distance:.3f}")
    print(f"Source: {metadata['filename']}")
    print(f"Content: {doc[:200]}...")
    print()
```

## Adding RAG with an LLM

```python
import openai
from doc_ingest import DocumentProcessor

processor = DocumentProcessor(output_dir="./vectorstore")

def ask(question: str) -> str:
    # Retrieve relevant chunks
    results = processor.query(question, n_results=5)
    context = "\n\n---\n\n".join(results['documents'][0])
    
    # Generate answer
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer based on the context. If unsure, say so."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content

print(ask("What are the key findings?"))
```

## Performance Tips

- **Fast processing**: Use `--strategy fast` for simple documents
- **Better OCR**: Install `tesseract-lang` for non-English documents
- **Faster embeddings**: Default model is fast; use `all-mpnet-base-v2` for better quality
- **Large directories**: Files are processed incrementally; re-running skips already processed files

## Troubleshooting

**"No module named 'magic'"**
```bash
pip install python-magic-bin  # Windows
pip install python-magic      # Linux/Mac (also install libmagic)
```

**PDF parsing fails**
```bash
# Make sure poppler is installed
pdftoppm -v  # Should show version
```

**OCR not working**
```bash
tesseract --version  # Should show version
```

## License

MIT

## Credits

Built on top of:
- [Unstructured](https://github.com/Unstructured-IO/unstructured) - Document parsing
- [ChromaDB](https://github.com/chroma-core/chroma) - Vector store
- [Sentence-Transformers](https://www.sbert.net/) - Embeddings
