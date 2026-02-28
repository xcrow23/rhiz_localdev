#!/usr/bin/env python3
"""
Rhiz Memory Browser
Interactive CLI for exploring Qdrant vector memories.
"""

import argparse
import json
import sys
from urllib.request import urlopen, Request
from urllib.parse import urlencode


QDRANT_URL = "http://localhost:6333"
COLLECTION = "rhiz_memories"


def make_request(endpoint, method="GET", data=None):
    """Make HTTP request to Qdrant."""
    url = f"{QDRANT_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if data:
        data = json.dumps(data).encode('utf-8')

    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def get_collection_info():
    """Get collection statistics."""
    result = make_request(f"/collections/{COLLECTION}")
    if result and result.get("status") == "ok":
        info = result["result"]
        return {
            "points_count": info.get("points_count", 0),
            "indexed_vectors": info.get("indexed_vectors_count", 0),
            "vector_size": info.get("config", {}).get("params", {}).get("vectors", {}).get("size", 0),
            "distance": info.get("config", {}).get("params", {}).get("vectors", {}).get("distance", "unknown")
        }
    return None


def list_memories(limit=10, offset=None, filter_type=None):
    """List memories with optional filtering."""
    scroll_data = {
        "limit": limit,
        "with_payload": True,
        "with_vector": False
    }

    if offset:
        scroll_data["offset"] = offset

    if filter_type:
        scroll_data["filter"] = {
            "must": [
                {"key": "type", "match": {"value": filter_type}}
            ]
        }

    result = make_request(f"/collections/{COLLECTION}/points/scroll", method="POST", data=scroll_data)

    if result and result.get("status") == "ok":
        points = result["result"]["points"]
        next_offset = result["result"].get("next_page_offset")

        return points, next_offset

    return [], None


def search_memories(query, limit=5):
    """Semantic search in memories."""
    # Qdrant search by text (uses FastEmbed if configured)
    search_data = {
        "query_text": query,
        "limit": limit,
        "with_payload": True,
        "with_vector": False
    }

    result = make_request(f"/collections/{COLLECTION}/points/query", method="POST", data=search_data)

    if result and result.get("status") == "ok":
        return result["result"].get("points", [])

    return []


def get_memory_by_id(point_id):
    """Get specific memory by ID."""
    result = make_request(f"/collections/{COLLECTION}/points/{point_id}")

    if result and result.get("status") == "ok":
        return result["result"]

    return None


def print_memory_summary(point):
    """Print concise memory summary."""
    payload = point.get("payload", {})
    point_id = point.get("id")

    mem_type = payload.get("type", "unknown")
    name = payload.get("name", "unnamed")
    description = payload.get("description", "")[:80]

    print(f"  [{point_id}] {mem_type}: {name}")
    print(f"    {description}...")
    print()


def print_memory_detail(point):
    """Print full memory details."""
    payload = point.get("payload", {})
    point_id = point.get("id")

    print("=" * 80)
    print(f"Memory ID: {point_id}")
    print("=" * 80)

    for key, value in payload.items():
        if key == "pattern_code" and len(str(value)) > 200:
            print(f"{key}: {str(value)[:200]}... (truncated)")
        else:
            print(f"{key}: {value}")

    print("=" * 80)
    print()


def export_memories(output_file, filter_type=None):
    """Export all memories to JSON file."""
    all_points = []
    offset = None

    while True:
        points, next_offset = list_memories(limit=100, offset=offset, filter_type=filter_type)

        if not points:
            break

        all_points.extend(points)

        if not next_offset:
            break

        offset = next_offset

    with open(output_file, 'w') as f:
        json.dump(all_points, f, indent=2)

    print(f"Exported {len(all_points)} memories to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Rhiz Memory Browser - Explore Qdrant memories")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Info command
    subparsers.add_parser("info", help="Show collection info")

    # List command
    list_parser = subparsers.add_parser("list", help="List memories")
    list_parser.add_argument("-n", "--limit", type=int, default=10, help="Number to show")
    list_parser.add_argument("-t", "--type", help="Filter by type")
    list_parser.add_argument("-d", "--detailed", action="store_true", help="Show full details")

    # Search command
    search_parser = subparsers.add_parser("search", help="Semantic search")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-n", "--limit", type=int, default=5, help="Number of results")
    search_parser.add_argument("-d", "--detailed", action="store_true", help="Show full details")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get memory by ID")
    get_parser.add_argument("id", type=int, help="Memory ID")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export memories to JSON")
    export_parser.add_argument("output", help="Output file path")
    export_parser.add_argument("-t", "--type", help="Filter by type")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == "info":
        info = get_collection_info()
        if info:
            print("\nRhiz Memory Collection Info")
            print("=" * 40)
            print(f"Total memories: {info['points_count']}")
            print(f"Indexed vectors: {info['indexed_vectors']}")
            print(f"Vector size: {info['vector_size']}")
            print(f"Distance metric: {info['distance']}")
            print("=" * 40)
            print()

    elif args.command == "list":
        print(f"\nListing memories (limit: {args.limit})")
        if args.type:
            print(f"Filter: type={args.type}")
        print()

        points, next_offset = list_memories(limit=args.limit, filter_type=args.type)

        if not points:
            print("No memories found.")
            return

        for point in points:
            if args.detailed:
                print_memory_detail(point)
            else:
                print_memory_summary(point)

        if next_offset:
            print(f"More results available. Next offset: {next_offset}")

    elif args.command == "search":
        print(f"\nSearching for: '{args.query}'")
        print()

        points = search_memories(args.query, limit=args.limit)

        if not points:
            print("No matches found.")
            return

        for point in points:
            score = point.get("score", 0)
            print(f"Score: {score:.4f}")

            if args.detailed:
                print_memory_detail(point)
            else:
                print_memory_summary(point)

    elif args.command == "get":
        memory = get_memory_by_id(args.id)

        if not memory:
            print(f"Memory {args.id} not found.")
            return

        print_memory_detail({"id": args.id, "payload": memory})

    elif args.command == "export":
        export_memories(args.output, filter_type=args.type)


if __name__ == "__main__":
    main()
