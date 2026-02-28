"""
Qdrant Backup and Restore Utility

Provides backup and restore capabilities for Qdrant collections
containing SIL trade outcomes, strategy performance, and decision logs.

Features:
- Full collection export to JSON
- Point-by-point restore from backup
- Backup verification
- Retention policy management
- Scheduled backup support

Usage:
    # Backup all collections
    python qdrant_backup.py backup --output-dir ./backups

    # Restore from backup
    python qdrant_backup.py restore --backup-file ./backups/backup_2026-01-03.json

    # List backups
    python qdrant_backup.py list --backup-dir ./backups

    # Verify backup integrity
    python qdrant_backup.py verify --backup-file ./backups/backup_2026-01-03.json

    # Clean old backups
    python qdrant_backup.py cleanup --backup-dir ./backups --retention-days 90
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path to import SIL modules
sys.path.append(str(Path(__file__).parent.parent))

from memory.qdrant_client import QdrantMemoryClient
from memory.qdrant_schema import QdrantCollections


class QdrantBackup:
    """Handles Qdrant backup and restore operations."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None
    ):
        """
        Initialize backup handler.

        Args:
            host: Qdrant host
            port: Qdrant port
            api_key: Optional API key
        """
        self.client = QdrantMemoryClient(host=host, port=port, api_key=api_key)

    def backup_all_collections(self, output_dir: Path) -> Path:
        """
        Backup all SIL collections to a single JSON file.

        Args:
            output_dir: Directory to save backup file

        Returns:
            Path to backup file
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = output_dir / f"sil_backup_{timestamp}.json"

        print(f"[Backup] Starting backup to {backup_file}")

        backup_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "collections": {}
        }

        # Backup each collection
        collections = [
            QdrantCollections.TRADE_OUTCOMES,
            QdrantCollections.STRATEGY_PERFORMANCE,
            QdrantCollections.DECISION_LOG
        ]

        for collection_name in collections:
            try:
                print(f"[Backup] Backing up {collection_name}...")
                points = self._export_collection(collection_name)
                backup_data["collections"][collection_name] = points
                print(f"[Backup] ✓ {collection_name}: {len(points)} points")
            except Exception as e:
                print(f"[Backup] ✗ {collection_name}: Error - {e}")
                backup_data["collections"][collection_name] = {
                    "error": str(e),
                    "points": []
                }

        # Save to file
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

        # Get file size
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        print(f"[Backup] Complete! Backup saved: {backup_file} ({size_mb:.2f} MB)")

        return backup_file

    def _export_collection(self, collection_name: str) -> List[Dict]:
        """
        Export all points from a collection.

        Args:
            collection_name: Name of collection to export

        Returns:
            List of point dictionaries
        """
        points = []
        offset = None
        batch_size = 100

        while True:
            # Scroll through collection
            result, next_offset = self.client.client.scroll(
                collection_name=collection_name,
                limit=batch_size,
                offset=offset,
                with_vectors=True,
                with_payload=True
            )

            if not result:
                break

            # Convert points to dictable format
            for point in result:
                points.append({
                    "id": str(point.id),
                    "vector": point.vector.tolist() if hasattr(point.vector, 'tolist') else list(point.vector),
                    "payload": point.payload
                })

            # Check if there are more points
            if next_offset is None:
                break

            offset = next_offset

        return points

    def restore_from_backup(self, backup_file: Path, overwrite: bool = False):
        """
        Restore collections from backup file.

        Args:
            backup_file: Path to backup JSON file
            overwrite: If True, delete existing collections before restore
        """
        backup_file = Path(backup_file)

        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        print(f"[Restore] Loading backup from {backup_file}")

        with open(backup_file, 'r') as f:
            backup_data = json.load(f)

        backup_time = backup_data.get("timestamp", "unknown")
        print(f"[Restore] Backup timestamp: {backup_time}")

        # Restore each collection
        for collection_name, points in backup_data["collections"].items():
            if isinstance(points, dict) and "error" in points:
                print(f"[Restore] ✗ Skipping {collection_name} (backup had error)")
                continue

            try:
                print(f"[Restore] Restoring {collection_name}...")
                self._import_collection(collection_name, points, overwrite=overwrite)
                print(f"[Restore] ✓ {collection_name}: {len(points)} points restored")
            except Exception as e:
                print(f"[Restore] ✗ {collection_name}: Error - {e}")

        print("[Restore] Complete!")

    def _import_collection(
        self,
        collection_name: str,
        points: List[Dict],
        overwrite: bool = False
    ):
        """
        Import points into a collection.

        Args:
            collection_name: Name of collection
            points: List of point dictionaries
            overwrite: If True, delete collection first
        """
        import numpy as np
        from qdrant_client.models import PointStruct

        if overwrite:
            try:
                self.client.client.delete_collection(collection_name)
                print(f"[Restore] Deleted existing collection: {collection_name}")
            except Exception:
                pass  # Collection may not exist

            # Recreate collection (will be done by initialization if needed)
            # For now, assume collection exists or will be created

        # Batch upsert points
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]

            point_structs = [
                PointStruct(
                    id=p["id"],
                    vector=np.array(p["vector"], dtype=np.float32),
                    payload=p["payload"]
                )
                for p in batch
            ]

            self.client.client.upsert(
                collection_name=collection_name,
                points=point_structs
            )

    def verify_backup(self, backup_file: Path) -> Dict:
        """
        Verify backup file integrity.

        Args:
            backup_file: Path to backup file

        Returns:
            Verification report
        """
        backup_file = Path(backup_file)

        if not backup_file.exists():
            return {"status": "error", "message": f"File not found: {backup_file}"}

        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"Invalid JSON: {e}"}

        # Verify structure
        if "timestamp" not in backup_data:
            return {"status": "error", "message": "Missing timestamp field"}

        if "collections" not in backup_data:
            return {"status": "error", "message": "Missing collections field"}

        # Count points
        total_points = 0
        collection_stats = {}

        for collection_name, points in backup_data["collections"].items():
            if isinstance(points, dict) and "error" in points:
                collection_stats[collection_name] = {"status": "error", "error": points["error"]}
            else:
                collection_stats[collection_name] = {
                    "status": "ok",
                    "points": len(points)
                }
                total_points += len(points)

        return {
            "status": "ok",
            "backup_timestamp": backup_data["timestamp"],
            "total_points": total_points,
            "collections": collection_stats,
            "file_size_mb": backup_file.stat().st_size / (1024 * 1024)
        }

    def list_backups(self, backup_dir: Path) -> List[Dict]:
        """
        List all backup files in directory.

        Args:
            backup_dir: Directory containing backups

        Returns:
            List of backup info dicts
        """
        backup_dir = Path(backup_dir)

        if not backup_dir.exists():
            return []

        backups = []
        for backup_file in sorted(backup_dir.glob("sil_backup_*.json"), reverse=True):
            try:
                stat = backup_file.stat()
                backups.append({
                    "file": str(backup_file),
                    "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size_mb": stat.st_size / (1024 * 1024)
                })
            except Exception as e:
                print(f"[List] Warning: Could not read {backup_file.name}: {e}")

        return backups

    def cleanup_old_backups(self, backup_dir: Path, retention_days: int = 90):
        """
        Delete backups older than retention period.

        Args:
            backup_dir: Directory containing backups
            retention_days: Keep backups newer than this many days
        """
        backup_dir = Path(backup_dir)

        if not backup_dir.exists():
            print(f"[Cleanup] Backup directory not found: {backup_dir}")
            return

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        deleted_count = 0

        for backup_file in backup_dir.glob("sil_backup_*.json"):
            try:
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)

                if file_mtime < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    print(f"[Cleanup] Deleted: {backup_file.name}")

            except Exception as e:
                print(f"[Cleanup] Warning: Could not delete {backup_file.name}: {e}")

        print(f"[Cleanup] Deleted {deleted_count} old backups (retention: {retention_days} days)")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Qdrant backup and restore utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create backup")
    backup_parser.add_argument("--output-dir", default="./backups", help="Output directory")
    backup_parser.add_argument("--host", default="localhost", help="Qdrant host")
    backup_parser.add_argument("--port", type=int, default=6333, help="Qdrant port")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("--backup-file", required=True, help="Backup file to restore")
    restore_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing collections")
    restore_parser.add_argument("--host", default="localhost", help="Qdrant host")
    restore_parser.add_argument("--port", type=int, default=6333, help="Qdrant port")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify backup integrity")
    verify_parser.add_argument("--backup-file", required=True, help="Backup file to verify")

    # List command
    list_parser = subparsers.add_parser("list", help="List backups")
    list_parser.add_argument("--backup-dir", default="./backups", help="Backup directory")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Delete old backups")
    cleanup_parser.add_argument("--backup-dir", default="./backups", help="Backup directory")
    cleanup_parser.add_argument("--retention-days", type=int, default=90, help="Retention period (days)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get Qdrant connection from environment if available
    host = os.getenv("QDRANT_HOST", args.host if hasattr(args, 'host') else "localhost")
    port = int(os.getenv("QDRANT_PORT", args.port if hasattr(args, 'port') else 6333))
    api_key = os.getenv("QDRANT_API_KEY")

    # Execute command
    if args.command == "backup":
        backup = QdrantBackup(host=host, port=port, api_key=api_key)
        backup.backup_all_collections(Path(args.output_dir))

    elif args.command == "restore":
        backup = QdrantBackup(host=host, port=port, api_key=api_key)
        backup.restore_from_backup(Path(args.backup_file), overwrite=args.overwrite)

    elif args.command == "verify":
        backup = QdrantBackup()
        report = backup.verify_backup(Path(args.backup_file))
        print(json.dumps(report, indent=2))

    elif args.command == "list":
        backup = QdrantBackup()
        backups = backup.list_backups(Path(args.backup_dir))
        for b in backups:
            print(f"{b['timestamp']}: {b['file']} ({b['size_mb']:.2f} MB)")

    elif args.command == "cleanup":
        backup = QdrantBackup()
        backup.cleanup_old_backups(Path(args.backup_dir), args.retention_days)


if __name__ == "__main__":
    main()
