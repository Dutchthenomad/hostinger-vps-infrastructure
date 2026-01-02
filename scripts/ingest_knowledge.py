#!/usr/bin/env python3
"""
Bulk ingest markdown knowledge into Qdrant.
Requires: pip install sentence-transformers qdrant-client
"""

import os
import hashlib
from pathlib import Path

# Check dependencies
try:
    from sentence_transformers import SentenceTransformer
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install sentence-transformers qdrant-client")
    exit(1)

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
KNOWLEDGE_DIR = "/root/knowledge"
COLLECTIONS = {
    "rugipedia": "rugs_protocol",
    "rl-design": "rl_design",
    "external-docs": "external_docs"
}

print("Loading embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
print("Model loaded, connected to Qdrant")

def chunk_text(text: str, max_chars: int = 1000) -> list:
    """Split text into chunks at paragraph boundaries."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def ingest_folder(folder: str, collection: str):
    """Ingest all markdown files from folder into collection."""
    folder_path = Path(KNOWLEDGE_DIR) / folder
    if not folder_path.exists():
        print(f"Skipping {folder} - not found at {folder_path}")
        return 0

    points = []
    files_processed = 0

    for md_file in folder_path.rglob("*.md"):
        print(f"  Processing: {md_file.name}")
        files_processed += 1

        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"    Error reading {md_file}: {e}")
            continue

        chunks = chunk_text(content)

        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:
                continue

            # Generate embedding
            embedding = model.encode(chunk).tolist()

            # Create unique ID from content hash
            chunk_id = hashlib.md5(f"{md_file}:{i}".encode()).hexdigest()

            points.append(PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "text": chunk,
                    "source": str(md_file.relative_to(KNOWLEDGE_DIR)),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            ))

    # Batch upsert
    if points:
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            client.upsert(collection_name=collection, points=batch)
            print(f"    Inserted batch {i//batch_size + 1} ({len(batch)} points)")

        print(f"  Total: {len(points)} chunks from {files_processed} files")
    else:
        print(f"  No content to ingest from {folder}")

    return len(points)

def main():
    total_points = 0

    for folder, collection in COLLECTIONS.items():
        print(f"\n=== Ingesting {folder} → {collection} ===")
        points = ingest_folder(folder, collection)
        total_points += points

    print("\n=== Collection Stats ===")
    for collection in COLLECTIONS.values():
        try:
            info = client.get_collection(collection)
            print(f"  {collection}: {info.points_count} vectors")
        except Exception as e:
            print(f"  {collection}: Error - {e}")

    print(f"\n=== Total: {total_points} vectors ingested ===")

if __name__ == "__main__":
    main()
