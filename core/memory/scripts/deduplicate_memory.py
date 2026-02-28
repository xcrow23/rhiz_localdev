"""
Memory Deduplication for Rhiz Vector Database

Identifies and optionally removes duplicate memory points in Qdrant.
Duplicates detected by:
- Identical content hashes (exact duplicates)
- High vector similarity (>0.99 cosine similarity)
- Same checkpoint_id with same section

Created: 2026-01-19
Purpose: Fix duplicate entries breaking semantic search (Session Start showed 2x same checkpoint)
"""

import hashlib
import yaml
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

try:
    from embeddings import EmbeddingGenerator
except ImportError:
    # Handle import if run from different context
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from embeddings import EmbeddingGenerator


class MemoryDeduplicator:
    """Identifies and removes duplicate memory points."""

    def __init__(self,
                 qdrant_host: str = "localhost",
                 qdrant_port: int = 6333,
                 collection_name: str = "rhiz_memories"):
        """
        Initialize deduplicator.

        Args:
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            collection_name: Name of collection to deduplicate
        """
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = collection_name

    def _content_hash(self, content: any) -> str:
        """Generate hash of content for exact duplicate detection."""
        # Convert content to stable string representation
        if isinstance(content, dict):
            content_str = yaml.dump(content, sort_keys=True)
        else:
            content_str = str(content)

        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

    def find_exact_duplicates(self) -> Dict[str, List[str]]:
        """
        Find exact content duplicates by hash.

        Returns:
            Dict mapping content hash to list of point IDs with that content
        """
        print("[DEDUP] Scanning for exact content duplicates...")

        # Scroll through all points
        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=1000,  # Adjust if collection >1000 points
            with_payload=True,
            with_vectors=False
        )

        # Group by content hash
        hash_groups = defaultdict(list)
        for point in points:
            content = point.payload.get("content", "")
            content_hash = self._content_hash(content)
            hash_groups[content_hash].append(str(point.id))

        # Filter to only groups with duplicates
        duplicates = {h: ids for h, ids in hash_groups.items() if len(ids) > 1}

        print(f"[DEDUP] Found {len(duplicates)} groups with exact duplicates")
        print(f"[DEDUP] Total duplicate points: {sum(len(ids) - 1 for ids in duplicates.values())}")

        return duplicates

    def find_checkpoint_duplicates(self) -> Dict[str, List[str]]:
        """
        Find duplicate checkpoints (same checkpoint_id + section).

        Returns:
            Dict mapping (checkpoint_id, section) to list of point IDs
        """
        print("[DEDUP] Scanning for duplicate checkpoint entries...")

        # Scroll through all points
        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )

        # Group by (checkpoint_id, section)
        checkpoint_groups = defaultdict(list)
        for point in points:
            checkpoint_id = point.payload.get("checkpoint_id", "unknown")
            section = point.payload.get("section", "unknown")
            key = (checkpoint_id, section)
            checkpoint_groups[key].append(str(point.id))

        # Filter to only groups with duplicates
        duplicates = {k: ids for k, ids in checkpoint_groups.items() if len(ids) > 1}

        print(f"[DEDUP] Found {len(duplicates)} checkpoint+section combinations with duplicates")
        print(f"[DEDUP] Total duplicate points: {sum(len(ids) - 1 for ids in duplicates.values())}")

        return duplicates

    def find_similar_duplicates(self, similarity_threshold: float = 0.99) -> List[Tuple[str, str, float]]:
        """
        Find near-duplicates by vector similarity.

        Args:
            similarity_threshold: Cosine similarity threshold (0-1)

        Returns:
            List of (point_id_1, point_id_2, similarity_score) tuples
        """
        print(f"[DEDUP] Scanning for similar duplicates (threshold {similarity_threshold})...")

        # Get all points with vectors
        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=1000,
            with_payload=True,
            with_vectors=True
        )

        print(f"[DEDUP] Comparing {len(points)} points...")

        duplicates = []
        for i, point_a in enumerate(points):
            if i % 50 == 0:
                print(f"[DEDUP] Progress: {i}/{len(points)} points checked")

            # Query for similar points
            similar = self.client.query_points(
                collection_name=self.collection_name,
                query=point_a.vector,
                limit=5,  # Only check top 5 most similar
                score_threshold=similarity_threshold
            ).points

            # Check for duplicates (excluding self)
            for sim_point in similar:
                if str(sim_point.id) != str(point_a.id):
                    # Check if this pair already recorded (avoid duplicates)
                    pair = tuple(sorted([str(point_a.id), str(sim_point.id)]))
                    if not any(tuple(sorted([d[0], d[1]])) == pair for d in duplicates):
                        duplicates.append((
                            str(point_a.id),
                            str(sim_point.id),
                            sim_point.score
                        ))

        print(f"[DEDUP] Found {len(duplicates)} similar duplicate pairs")
        return duplicates

    def analyze_duplicates(self, dry_run: bool = True) -> Dict:
        """
        Run complete duplicate analysis.

        Args:
            dry_run: If True, only report duplicates without deleting

        Returns:
            Summary report with duplicate counts
        """
        report = {
            "dry_run": dry_run,
            "timestamp": str(Path(__file__).parent),
            "collection": self.collection_name
        }

        # Find exact duplicates
        exact_dups = self.find_exact_duplicates()
        report["exact_duplicates"] = {
            "groups": len(exact_dups),
            "total_points": sum(len(ids) - 1 for ids in exact_dups.values()),
            "examples": list(exact_dups.items())[:3]
        }

        # Find checkpoint duplicates
        checkpoint_dups = self.find_checkpoint_duplicates()
        report["checkpoint_duplicates"] = {
            "groups": len(checkpoint_dups),
            "total_points": sum(len(ids) - 1 for ids in checkpoint_dups.values()),
            "examples": [(f"{k[0]}:{k[1]}", ids) for k, ids in list(checkpoint_dups.items())[:3]]
        }

        # Calculate total
        total_exact = sum(len(ids) - 1 for ids in exact_dups.values())
        total_checkpoint = sum(len(ids) - 1 for ids in checkpoint_dups.values())

        report["summary"] = {
            "total_duplicate_points": total_exact + total_checkpoint,
            "action": "DRY RUN - No points deleted" if dry_run else "DELETED duplicates"
        }

        return report

    def remove_exact_duplicates(self, keep_oldest: bool = True) -> int:
        """
        Remove exact content duplicates.

        Args:
            keep_oldest: If True, keeps oldest point in each group (by ID)

        Returns:
            Number of points deleted
        """
        duplicates = self.find_exact_duplicates()

        deleted_count = 0
        for content_hash, point_ids in duplicates.items():
            # Sort IDs (oldest first if numeric IDs)
            sorted_ids = sorted(point_ids, key=lambda x: int(x) if x.isdigit() else x)

            # Keep first (oldest), delete rest
            ids_to_delete = sorted_ids[1:] if keep_oldest else sorted_ids[:-1]

            print(f"[DEDUP] Deleting {len(ids_to_delete)} duplicates of point {sorted_ids[0]}")

            for point_id in ids_to_delete:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=[point_id]
                )
                deleted_count += 1

        print(f"[DEDUP] Deleted {deleted_count} exact duplicate points")
        return deleted_count

    def remove_checkpoint_duplicates(self, keep_oldest: bool = True) -> int:
        """
        Remove duplicate checkpoint entries.

        Args:
            keep_oldest: If True, keeps oldest point in each (checkpoint_id, section) group

        Returns:
            Number of points deleted
        """
        duplicates = self.find_checkpoint_duplicates()

        deleted_count = 0
        for (checkpoint_id, section), point_ids in duplicates.items():
            # Sort IDs (oldest first)
            sorted_ids = sorted(point_ids, key=lambda x: int(x) if x.isdigit() else x)

            # Keep first, delete rest
            ids_to_delete = sorted_ids[1:] if keep_oldest else sorted_ids[:-1]

            print(f"[DEDUP] Deleting {len(ids_to_delete)} duplicates of {checkpoint_id}:{section}")

            for point_id in ids_to_delete:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=[point_id]
                )
                deleted_count += 1

        print(f"[DEDUP] Deleted {deleted_count} checkpoint duplicate points")
        return deleted_count

    def format_report(self, report: Dict) -> str:
        """Format analysis report as readable text."""
        lines = []
        lines.append("=" * 80)
        lines.append("MEMORY DEDUPLICATION REPORT")
        lines.append("=" * 80)

        lines.append(f"\nCollection: {report['collection']}")
        lines.append(f"Mode: {'DRY RUN' if report['dry_run'] else 'LIVE DELETE'}")

        # Exact duplicates
        exact = report["exact_duplicates"]
        lines.append(f"\n## Exact Content Duplicates")
        lines.append(f"Groups: {exact['groups']}")
        lines.append(f"Total Points: {exact['total_points']}")
        if exact["examples"]:
            lines.append(f"\nExamples:")
            for content_hash, ids in exact["examples"]:
                lines.append(f"  Hash {content_hash[:16]}...: {len(ids)} copies")

        # Checkpoint duplicates
        checkpoint = report["checkpoint_duplicates"]
        lines.append(f"\n## Checkpoint+Section Duplicates")
        lines.append(f"Groups: {checkpoint['groups']}")
        lines.append(f"Total Points: {checkpoint['total_points']}")
        if checkpoint["examples"]:
            lines.append(f"\nExamples:")
            for key, ids in checkpoint["examples"]:
                lines.append(f"  {key}: {len(ids)} copies")

        # Summary
        summary = report["summary"]
        lines.append(f"\n## Summary")
        lines.append(f"Total Duplicate Points: {summary['total_duplicate_points']}")
        lines.append(f"Action: {summary['action']}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


def deduplicate_collection(
    collection_name: str = "rhiz_memories",
    dry_run: bool = True,
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333
):
    """
    Convenience function to deduplicate a collection.

    Args:
        collection_name: Collection to deduplicate
        dry_run: If True, only analyze without deleting
        qdrant_host: Qdrant server host
        qdrant_port: Qdrant server port
    """
    dedup = MemoryDeduplicator(qdrant_host, qdrant_port, collection_name)

    if dry_run:
        # Analyze only
        report = dedup.analyze_duplicates(dry_run=True)
        print(dedup.format_report(report))
        return report
    else:
        # Analyze + delete
        print("[DEDUP] Running in LIVE mode - duplicates will be deleted")
        print("[DEDUP] Press Ctrl+C within 5 seconds to cancel...")
        import time
        time.sleep(5)

        report_before = dedup.analyze_duplicates(dry_run=True)
        print(dedup.format_report(report_before))

        print("\n[DEDUP] Proceeding with deletion...\n")

        # Delete exact duplicates
        exact_deleted = dedup.remove_exact_duplicates(keep_oldest=True)

        # Delete checkpoint duplicates
        checkpoint_deleted = dedup.remove_checkpoint_duplicates(keep_oldest=True)

        print(f"\n[DEDUP] COMPLETE:")
        print(f"  Exact duplicates deleted: {exact_deleted}")
        print(f"  Checkpoint duplicates deleted: {checkpoint_deleted}")
        print(f"  Total deleted: {exact_deleted + checkpoint_deleted}")

        return {
            "deleted": {
                "exact": exact_deleted,
                "checkpoint": checkpoint_deleted,
                "total": exact_deleted + checkpoint_deleted
            }
        }


if __name__ == "__main__":
    import sys

    # Parse command line
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    auto_confirm = "--yes" in sys.argv or "-y" in sys.argv
    collection = "rhiz_memories"

    if "--collection" in sys.argv:
        idx = sys.argv.index("--collection")
        if idx + 1 < len(sys.argv):
            collection = sys.argv[idx + 1]

    print("=" * 80)
    print("RHIZ MEMORY DEDUPLICATOR")
    print("=" * 80)
    print(f"\nCollection: {collection}")
    print(f"Mode: {'DRY RUN (analysis only)' if dry_run else 'LIVE (will delete duplicates)'}")
    print("")

    if not dry_run:
        if auto_confirm:
            print("[WARN] WARNING: Auto-confirmed deletion of duplicate points!")
        else:
            print("[WARN] WARNING: This will permanently delete duplicate points!")
            confirm = input("Type 'DELETE' to confirm: ")
            if confirm != "DELETE":
                print("Cancelled.")
                sys.exit(0)

    deduplicate_collection(collection_name=collection, dry_run=dry_run)
