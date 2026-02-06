#!/usr/bin/env python3
"""
Example: Building a simple RAG Q&A system with doc-ingest.

This example shows how to:
1. Process documents into a vector store
2. Query the store
3. Use retrieved context with an LLM (OpenAI example)

Usage:
    # First, set your OpenAI API key
    export OPENAI_API_KEY="your-key"
    
    # Then run
    python rag_example.py
"""

import os
from pathlib import Path

# Check for OpenAI key (optional - only needed for LLM part)
HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))

from doc_ingest import DocumentProcessor


def main():
    # Path to sample documents
    docs_dir = Path(__file__).parent / "sample-docs"
    output_dir = Path(__file__).parent / "vectorstore"
    
    print("=" * 60)
    print("doc-ingest RAG Example")
    print("=" * 60)
    
    # 1. Process documents
    print("\n[1] Processing documents...")
    processor = DocumentProcessor(
        output_dir=output_dir,
        chunk_size=500,  # Smaller chunks for this demo
    )
    processor.process_directory(docs_dir)
    
    # 2. Query the vector store
    print("\n[2] Querying the vector store...")
    
    questions = [
        "What is the vacation policy?",
        "How do I get a refund?",
        "What integrations are available?",
    ]
    
    for question in questions:
        print(f"\n📝 Question: {question}")
        print("-" * 40)
        
        results = processor.query(question, n_results=2)
        
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            score = 1 - dist
            print(f"\n  Result {i+1} (score: {score:.3f}, source: {meta['filename']})")
            print(f"  {doc[:200]}...")
    
    # 3. Full RAG with LLM (if OpenAI available)
    if HAS_OPENAI:
        print("\n" + "=" * 60)
        print("[3] Full RAG with OpenAI")
        print("=" * 60)
        
        import openai
        client = openai.OpenAI()
        
        def ask(question: str) -> str:
            """Full RAG: retrieve context and generate answer."""
            # Retrieve
            results = processor.query(question, n_results=3)
            context = "\n\n---\n\n".join(results['documents'][0])
            
            # Generate
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Answer questions based on the provided context. "
                            "Be concise. If the answer isn't in the context, say so."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}"
                    }
                ],
                max_tokens=200,
            )
            return response.choices[0].message.content
        
        question = "How many vacation days do I get and can I carry them over?"
        print(f"\n📝 Question: {question}")
        print("-" * 40)
        answer = ask(question)
        print(f"\n🤖 Answer: {answer}")
    
    else:
        print("\n" + "=" * 60)
        print("💡 Tip: Set OPENAI_API_KEY to see the full RAG example with LLM generation")
        print("=" * 60)
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
