"""
Rhiz Memory Cloud Sync
Syncs local Qdrant memories to cloud via SSH tunnel.

Usage:
    python sync_cloud.py [--reverse]  # reverse syncs cloud -> local

Requires SSH tunnel: ssh -L 6335:localhost:6333 root@72.62.81.128
Or run with --tunnel to establish automatically.
"""

import argparse
import subprocess
import sys
import time

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
except ImportError:
    print("Error: qdrant-client not installed")
    sys.exit(1)


def establish_tunnel():
    """Establish SSH tunnel to cloud Qdrant."""
    print("Establishing SSH tunnel...")
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-L", "6335:localhost:6333",
         "-f", "-N", "root@72.62.81.128"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("Tunnel established on localhost:6335")
        time.sleep(1)  # Give tunnel time to initialize
        return True
    else:
        print(f"Failed to establish tunnel: {result.stderr}")
        return False


def sync_memories(source: QdrantClient, dest: QdrantClient,
                  source_name: str, dest_name: str):
    """Sync all memories from source to destination."""

    collection = "rhiz_memories"

    # Get counts
    source_info = source.get_collection(collection)
    dest_info = dest.get_collection(collection)

    print(f"\n{source_name}: {source_info.points_count} points")
    print(f"{dest_name}: {dest_info.points_count} points")

    # Scroll through all source points
    print(f"\nFetching from {source_name}...")
    all_points = []
    offset = None

    while True:
        result = source.scroll(
            collection_name=collection,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=True
        )
        points, offset = result
        all_points.extend(points)
        if offset is None:
            break

    print(f"Retrieved {len(all_points)} points")

    if not all_points:
        print("Nothing to sync.")
        return

    # Upsert to destination
    print(f"\nSyncing to {dest_name}...")
    batch_size = 50

    for i in range(0, len(all_points), batch_size):
        batch = all_points[i:i+batch_size]
        dest.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=p.id,
                    vector=p.vector,
                    payload=p.payload
                ) for p in batch
            ]
        )
        print(f"  Synced {min(i+batch_size, len(all_points))}/{len(all_points)}")

    # Verify
    dest_info = dest.get_collection(collection)
    print(f"\n{dest_name} after sync: {dest_info.points_count} points")


def main():
    parser = argparse.ArgumentParser(description="Sync Rhiz memories between local and cloud")
    parser.add_argument("--reverse", action="store_true",
                        help="Sync cloud -> local instead of local -> cloud")
    parser.add_argument("--tunnel", action="store_true",
                        help="Establish SSH tunnel before syncing")
    parser.add_argument("--cloud-port", type=int, default=6335,
                        help="Local port for cloud tunnel (default: 6335)")

    args = parser.parse_args()

    print("=" * 60)
    print("RHIZ MEMORY SYNC")
    print("=" * 60)

    # Establish tunnel if requested
    if args.tunnel:
        if not establish_tunnel():
            sys.exit(1)

    # Connect to both
    try:
        local = QdrantClient(host='localhost', port=6333)
        local.get_collections()  # Test connection
        print("Connected to local Qdrant (port 6333)")
    except Exception as e:
        print(f"Failed to connect to local Qdrant: {e}")
        sys.exit(1)

    try:
        cloud = QdrantClient(host='localhost', port=args.cloud_port)
        cloud.get_collections()  # Test connection
        print(f"Connected to cloud Qdrant (port {args.cloud_port} via tunnel)")
    except Exception as e:
        print(f"Failed to connect to cloud Qdrant: {e}")
        print("\nMake sure SSH tunnel is running:")
        print("  ssh -L 6335:localhost:6333 -f -N root@72.62.81.128")
        sys.exit(1)

    # Sync
    if args.reverse:
        sync_memories(cloud, local, "Cloud", "Local")
    else:
        sync_memories(local, cloud, "Local", "Cloud")

    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
