#!/usr/bin/env python3
"""
Rhiz-MCP Startup Verification Script
Checks all dependencies and services are properly configured
"""

import sys
from pathlib import Path

def check_imports():
    """Verify all required Python packages are importable"""
    print("🔍 Checking Python dependencies...")

    try:
        import sentence_transformers
        print("✅ sentence_transformers: OK")
        print(f"   Version: {sentence_transformers.__version__}")
    except ImportError as e:
        print(f"❌ sentence_transformers: MISSING - {e}")
        return False

    try:
        from qdrant_client import QdrantClient
        print("✅ qdrant_client: OK")
    except ImportError as e:
        print(f"❌ qdrant_client: MISSING - {e}")
        return False

    try:
        import yaml
        print("✅ pyyaml: OK")
    except ImportError as e:
        print(f"❌ pyyaml: MISSING - {e}")
        return False

    return True

def check_qdrant_connection():
    """Verify Qdrant is running and accessible"""
    print("\n🔍 Checking Qdrant connection...")

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http import models

        client = QdrantClient(host="localhost", port=6333, timeout=5.0)

        # Test connection
        collections = client.get_collections()
        print(f"✅ Qdrant: Connected")
        print(f"   Endpoint: localhost:6333")
        print(f"   Collections: {len(collections.collections)}")

        # Check for rhiz_memories collection
        collection_names = [c.name for c in collections.collections]
        if "rhiz_memories" in collection_names:
            print(f"✅ Collection 'rhiz_memories': EXISTS")
            info = client.get_collection("rhiz_memories")
            print(f"   Vectors: {info.points_count}")
            print(f"   Vector size: {info.config.params.vectors.size}")
        else:
            print(f"⚠️  Collection 'rhiz_memories': NOT FOUND")
            print(f"   Available: {collection_names}")
            print(f"   Will be auto-created on first checkpoint search")

        return True

    except Exception as e:
        print(f"❌ Qdrant: UNAVAILABLE - {e}")
        print("\n   To start Qdrant:")
        print("   docker-compose up -d qdrant")
        return False

def check_checkpoint_directory():
    """Verify checkpoint directory exists and is accessible"""
    print("\n🔍 Checking checkpoint directory...")

    checkpoint_dir = Path(__file__).parent.parent.parent / "core" / "memory" / "checkpoints"

    if checkpoint_dir.exists():
        yaml_files = list(checkpoint_dir.glob("*.yaml"))
        print(f"✅ Checkpoint directory: {checkpoint_dir}")
        print(f"   Checkpoints found: {len(yaml_files)}")
        if yaml_files:
            latest = max(yaml_files, key=lambda p: p.stat().st_mtime)
            print(f"   Latest: {latest.name}")
    else:
        print(f"⚠️  Checkpoint directory not found: {checkpoint_dir}")
        print(f"   Will be created automatically")

    return True

def test_memory_search():
    """Test the actual memory search functionality"""
    print("\n🔍 Testing memory search system...")

    try:
        from sentence_transformers import SentenceTransformer

        # Load the model (this is what checkpoint_manager does)
        print("   Loading sentence transformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded successfully")

        # Test embedding generation
        test_text = "test query"
        embedding = model.encode(test_text)
        print(f"✅ Embedding generation works (dimension: {len(embedding)})")

        return True

    except Exception as e:
        print(f"❌ Memory search test failed: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("RHIZ-MCP STARTUP VERIFICATION")
    print("=" * 60)

    all_passed = True

    # Run checks
    all_passed &= check_imports()
    all_passed &= check_qdrant_connection()
    all_passed &= check_checkpoint_directory()
    all_passed &= test_memory_search()

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - System ready")
        print("\nYou can now test with:")
        print("  mcp__rhiz-mcp__memory_health_check()")
        print("  mcp__rhiz-mcp__checkpoint_search(query='your search')")
    else:
        print("❌ SOME CHECKS FAILED - See errors above")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
