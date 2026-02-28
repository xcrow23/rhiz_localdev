#!/usr/bin/env python3
"""
Initialize Qdrant collection for skill fingerprints.

Creates rhiz_skills collection with vector configuration matching
all-MiniLM-L6-v2 embeddings (384-dim, COSINE distance).
"""

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance


def create_skills_collection(
    host: str = "localhost",
    port: int = 6333,
    collection_name: str = "rhiz_skills"
):
    """
    Create Qdrant collection for skill fingerprints.

    Args:
        host: Qdrant server host
        port: Qdrant server port
        collection_name: Name for the skills collection

    Returns:
        True if created successfully, False if already exists
    """
    client = QdrantClient(host=host, port=port)

    # Check if collection already exists
    collections = client.get_collections().collections
    existing_names = [col.name for col in collections]

    if collection_name in existing_names:
        print(f"[INFO] Collection '{collection_name}' already exists")

        # Get collection info
        info = client.get_collection(collection_name)
        print(f"  Points: {info.points_count}")
        print(f"  Vector size: {info.config.params.vectors.size}")
        print(f"  Distance: {info.config.params.vectors.distance}")
        return False

    # Create new collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,  # all-MiniLM-L6-v2 embedding dimension
            distance=Distance.COSINE
        )
    )

    print(f"[OK] Created '{collection_name}' collection")
    print(f"  Vector size: 384 (all-MiniLM-L6-v2)")
    print(f"  Distance: COSINE")
    print(f"  Status: Ready for skill fingerprints")

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize Qdrant collection for skill fingerprints"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Qdrant server host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6333,
        help="Qdrant server port (default: 6333)"
    )
    parser.add_argument(
        "--collection",
        default="rhiz_skills",
        help="Collection name (default: rhiz_skills)"
    )

    args = parser.parse_args()

    try:
        create_skills_collection(
            host=args.host,
            port=args.port,
            collection_name=args.collection
        )
    except Exception as e:
        print(f"[ERROR] Failed to create collection: {e}")
        exit(1)
