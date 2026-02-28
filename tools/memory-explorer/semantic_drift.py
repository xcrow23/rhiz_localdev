#!/usr/bin/env python3
"""
Semantic Drift Analyzer
Analyzes embedding distance between consecutive sessions to identify conceptual shifts.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add paths for imports
RHIZ_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(RHIZ_ROOT / "core" / "memory" / "scripts"))

try:
    from embeddings import EmbeddingGenerator
    from qdrant_client import QdrantClient
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    import numpy as np
except ImportError as e:
    print(f"Error: Required dependencies not available: {e}", file=sys.stderr)
    print("This tool requires: sentence-transformers, qdrant-client, numpy", file=sys.stderr)
    sys.exit(1)


class SemanticDriftAnalyzer:
    """Analyze embedding distance between consecutive sessions"""

    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333, collection_name: str = "rhiz_memories"):
        try:
            self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
            self.collection_name = collection_name
            self.embedder = None  # Lazy initialization

            # Verify collection exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            if collection_name not in collection_names:
                raise ValueError(f"Collection '{collection_name}' not found. Available: {collection_names}")

        except Exception as e:
            print(f"Error connecting to Qdrant: {e}", file=sys.stderr)
            raise

    def _get_embedder(self) -> EmbeddingGenerator:
        """Lazy initialization of embedding generator"""
        if self.embedder is None:
            self.embedder = EmbeddingGenerator()
        return self.embedder

    def compute_session_drift(self, section: str = "mental_model") -> List[Dict]:
        """
        Compute cosine distance between consecutive session embeddings.

        Args:
            section: Which checkpoint section to analyze (mental_model, session_arc, etc.)

        Returns:
            List of drift measurements between consecutive sessions
        """
        # Query all points from specified section, sorted by date
        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="section",
                        match=MatchValue(value=section)
                    )
                ]
            ),
            limit=100,
            with_vectors=True,
            with_payload=True
        )

        if len(results) < 2:
            print(f"Warning: Found only {len(results)} points for section '{section}'. Need at least 2 for drift analysis.", file=sys.stderr)
            return []

        # Sort by session date
        points = sorted(results, key=lambda p: p.payload.get('session_date', ''))

        # Compute drift between consecutive sessions
        drift_timeline = []
        for i in range(1, len(points)):
            prev_vector = np.array(points[i-1].vector)
            curr_vector = np.array(points[i].vector)

            # Cosine similarity (1 - distance)
            similarity = np.dot(prev_vector, curr_vector) / (np.linalg.norm(prev_vector) * np.linalg.norm(curr_vector))
            distance = 1 - similarity

            drift_timeline.append({
                'from_session': points[i-1].payload.get('checkpoint_id', 'unknown'),
                'to_session': points[i].payload.get('checkpoint_id', 'unknown'),
                'from_date': points[i-1].payload.get('session_date', 'unknown'),
                'to_date': points[i].payload.get('session_date', 'unknown'),
                'semantic_distance': float(distance),
                'similarity': float(similarity),
                'section': section
            })

        return drift_timeline

    def identify_high_drift_sessions(self, threshold: float = 0.3, section: str = "mental_model") -> List[Dict]:
        """
        Find sessions with unusually high semantic drift.

        Args:
            threshold: Distance threshold above which drift is considered "high"
            section: Which checkpoint section to analyze

        Returns:
            List of high-drift sessions, sorted by distance (descending)
        """
        drift = self.compute_session_drift(section=section)
        high_drift = [d for d in drift if d['semantic_distance'] > threshold]
        return sorted(high_drift, key=lambda x: -x['semantic_distance'])

    def compute_drift_statistics(self, section: str = "mental_model") -> Dict:
        """Compute summary statistics for semantic drift"""
        drift = self.compute_session_drift(section=section)

        if not drift:
            return {
                'section': section,
                'total_transitions': 0,
                'mean_distance': 0.0,
                'std_distance': 0.0,
                'min_distance': 0.0,
                'max_distance': 0.0
            }

        distances = [d['semantic_distance'] for d in drift]

        return {
            'section': section,
            'total_transitions': len(drift),
            'mean_distance': float(np.mean(distances)),
            'std_distance': float(np.std(distances)),
            'min_distance': float(np.min(distances)),
            'max_distance': float(np.max(distances)),
            'median_distance': float(np.median(distances))
        }

    def visualize_drift(self, section: str = "mental_model", max_bar_length: int = 50) -> str:
        """ASCII chart of semantic drift over time"""
        drift = self.compute_session_drift(section=section)

        if not drift:
            return f"No drift data available for section: {section}"

        chart = []
        chart.append(f"SEMANTIC DRIFT TIMELINE ({section.replace('_', ' ').title()})")
        chart.append("-" * 60)
        chart.append("")

        for entry in drift:
            distance = entry['semantic_distance']
            bar_length = int(distance * max_bar_length)
            bar = "#" * bar_length

            session_display = entry['to_session'][:20].ljust(20)
            date_display = entry['to_date'][:12].ljust(12)

            chart.append(f"{date_display} {session_display} | {bar} ({distance:.3f})")

        chart.append("")
        chart.append(f"Note: Higher bars = larger conceptual shifts between sessions")
        chart.append(f"      Distance range: {min(d['semantic_distance'] for d in drift):.3f} - {max(d['semantic_distance'] for d in drift):.3f}")

        return "\n".join(chart)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze semantic drift across sessions")
    parser.add_argument(
        "--section",
        default="mental_model",
        help="Checkpoint section to analyze (default: mental_model)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.3,
        help="Drift threshold for identifying high-drift sessions (default: 0.3)"
    )
    parser.add_argument(
        "--command",
        choices=["visualize", "stats", "high-drift"],
        default="visualize",
        help="Command to execute (default: visualize)"
    )

    args = parser.parse_args()

    try:
        analyzer = SemanticDriftAnalyzer()

        if args.command == "visualize":
            print(analyzer.visualize_drift(section=args.section))

        elif args.command == "stats":
            import json
            stats = analyzer.compute_drift_statistics(section=args.section)
            print(json.dumps(stats, indent=2))

        elif args.command == "high-drift":
            import json
            high_drift = analyzer.identify_high_drift_sessions(
                threshold=args.threshold,
                section=args.section
            )
            print(json.dumps(high_drift, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
