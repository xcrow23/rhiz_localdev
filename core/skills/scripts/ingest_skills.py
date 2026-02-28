#!/usr/bin/env python3
"""
Ingest skill fingerprints into Qdrant for semantic routing.

Loads skill definitions from skill_fingerprints.yaml and creates
multi-component embeddings combining description, utterances, and tools.
"""

import yaml
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer


def validate_skill_schema(skill: dict, skill_index: int) -> None:
    """
    Validate skill has required fields for fingerprint creation.

    Args:
        skill: Skill definition dict
        skill_index: Position in skills list (for error messages)

    Raises:
        ValueError: If skill is missing required fields or has invalid types
    """
    required_fields = ["name", "description", "category", "utterances"]
    missing = [field for field in required_fields if field not in skill]

    if missing:
        raise ValueError(
            f"Skill #{skill_index} ({skill.get('name', 'UNKNOWN')}) "
            f"missing required fields: {missing}"
        )

    # Type validation
    if not isinstance(skill["utterances"], list):
        raise ValueError(
            f"Skill #{skill_index} ({skill['name']}): "
            f"'utterances' must be a list, got {type(skill['utterances']).__name__}"
        )

    if "tools" in skill and not isinstance(skill["tools"], list):
        raise ValueError(
            f"Skill #{skill_index} ({skill['name']}): "
            f"'tools' must be a list, got {type(skill['tools']).__name__}"
        )

    # Naming convention check
    if "/" not in skill["name"]:
        print(
            f"  [WARNING] Skill #{skill_index} ({skill['name']}) "
            f"should follow 'domain/name' convention"
        )


def create_skill_fingerprint(skill: dict, encoder: SentenceTransformer) -> list:
    """
    Create multi-component embedding for skill.

    Combines skill description, utterances, category, and tools into
    a single vector representation for semantic matching.

    Args:
        skill: Skill definition dict with validated schema
        encoder: SentenceTransformer model

    Returns:
        384-dim embedding vector

    Raises:
        KeyError: If required fields missing (should be caught by validate_skill_schema first)
    """
    components = [
        skill["description"],
        " ".join(skill["utterances"]),
        skill["category"],
        " ".join(skill.get("tools", []))
    ]
    combined = " [SEP] ".join(components)
    return encoder.encode(combined).tolist()


def ingest_all_skills(
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333,
    collection_name: str = "rhiz_skills"
):
    """
    Ingest all skill fingerprints from registry into Qdrant.

    Args:
        qdrant_host: Qdrant server host
        qdrant_port: Qdrant server port
        collection_name: Name of skills collection

    Returns:
        Number of skills ingested
    """
    # Load skills registry
    skills_file = Path(__file__).parent.parent / "registry" / "skill_fingerprints.yaml"
    print(f"Loading skills from: {skills_file}")

    with open(skills_file) as f:
        data = yaml.safe_load(f)

    skills = data.get("skills", [])
    print(f"Found {len(skills)} skill definitions")

    # Initialize Qdrant and encoder
    client = QdrantClient(host=qdrant_host, port=qdrant_port)
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"[OK] Loaded encoder: all-MiniLM-L6-v2")

    # Validate and create skill embeddings
    points = []
    for idx, skill in enumerate(skills):
        # Validate skill schema before processing
        validate_skill_schema(skill, idx + 1)

        embedding = create_skill_fingerprint(skill, encoder)

        point = PointStruct(
            id=idx + 1,
            vector=embedding,
            payload={
                "name": skill["name"],
                "description": skill["description"],
                "category": skill["category"],
                "utterances": skill["utterances"],
                "tools": skill.get("tools", []),
                "dependencies": skill.get("dependencies", []),
                "domain": skill.get("domain", "general"),
                "priority": skill.get("priority", "medium")
            }
        )
        points.append(point)
        print(f"  [{idx+1}] {skill['name']} - {len(skill['utterances'])} utterances")

    # Upsert to Qdrant
    client.upsert(collection_name=collection_name, points=points)
    print(f"\n[OK] Ingested {len(points)} skills to '{collection_name}' collection")

    return len(points)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingest skill fingerprints into Qdrant for semantic routing"
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
        count = ingest_all_skills(
            qdrant_host=args.host,
            qdrant_port=args.port,
            collection_name=args.collection
        )
        print(f"\n[OK] Successfully ingested {count} skills")
    except FileNotFoundError as e:
        print(f"[ERROR] Skill registry file not found: {e}")
        print(f"Verify RHIZ_ROOT is set correctly or run from repo root")
        exit(1)
    except yaml.YAMLError as e:
        print(f"[ERROR] Invalid YAML in skill_fingerprints.yaml: {e}")
        if hasattr(e, 'problem_mark'):
            print(f"Check syntax at line {e.problem_mark.line}")
        exit(1)
    except ValueError as e:
        print(f"[ERROR] Skill validation failed: {e}")
        print(f"Fix skill definitions in skill_fingerprints.yaml")
        exit(1)
    except Exception as e:
        error_str = str(e).lower()
        if "connection" in error_str or "qdrant" in error_str:
            print(f"[ERROR] Cannot connect to Qdrant: {e}")
            print(f"Verify Qdrant is running:")
            print(f"  docker ps | grep qdrant")
            print(f"  curl http://{args.host}:{args.port}/collections")
            exit(1)
        else:
            print(f"[ERROR] Unexpected error during ingestion: {e}")
            import traceback
            traceback.print_exc()
            exit(1)
