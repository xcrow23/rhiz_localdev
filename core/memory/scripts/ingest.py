"""
Checkpoint Ingestion for Rhiz Memory System
Reads YAML checkpoints and ingests them into Qdrant vector database.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm
import uuid

from embeddings import EmbeddingGenerator


def extract_session_date(checkpoint: dict) -> str:
    """Extract date with fallback to created timestamp."""
    if "session_date" in checkpoint:
        return checkpoint["session_date"]
    if "created" in checkpoint:
        try:
            created_dt = datetime.fromisoformat(checkpoint["created"])
            return created_dt.date().isoformat()
        except (ValueError, AttributeError):
            pass
    return "unknown"


def extract_phase(checkpoint: dict) -> str:
    """
    Extract phase from multiple possible locations.

    Handles both string and dict formats:
    - String: "Wave 2: Trust Calibration"
    - Dict: {"current": "Wave 2", "previous": "Wave 1"}
    """
    # Try relational_state.phase_assessment
    if "relational_state" in checkpoint:
        rs = checkpoint["relational_state"]
        if isinstance(rs, dict) and "phase_assessment" in rs:
            phase = rs["phase_assessment"]
            # Handle dict format
            if isinstance(phase, dict):
                return str(phase.get("current", "unknown"))
            return str(phase) if phase else "unknown"

    # Try direct phase_assessment key
    if "phase_assessment" in checkpoint:
        phase = checkpoint["phase_assessment"]
        # Handle dict format: {current: "Wave 2", previous: "Wave 1"}
        if isinstance(phase, dict):
            return str(phase.get("current", "unknown"))
        return str(phase) if phase else "unknown"

    # Try alternatives_rejected.phase_mismatch
    if "alternatives_rejected" in checkpoint:
        alt = checkpoint["alternatives_rejected"]
        if isinstance(alt, dict) and "phase_mismatch" in alt:
            phase = alt["phase_mismatch"]
            # Handle dict format
            if isinstance(phase, dict):
                return str(phase.get("expected", "unknown"))
            return str(phase) if phase else "unknown"

    return "unknown"


def infer_domains_from_content(checkpoint: dict) -> List[str]:
    """Infer domains from session_arc, mental_model, decisions_made."""
    domains = []

    # Combine searchable text
    text_fields = [
        checkpoint.get("session_arc", ""),
        str(checkpoint.get("mental_model", "")),
        str(checkpoint.get("decisions_made", "")),
        checkpoint.get("session_topic", "")
    ]
    combined_text = " ".join(text_fields).lower()

    # Domain keywords
    if any(kw in combined_text for kw in ["trading", "kraken", "fathom", "hummingbot", "portfolio"]):
        domains.append("trading")

    if any(kw in combined_text for kw in ["qdrant", "docker", "cloudflare", "vps", "deployment"]):
        domains.append("infrastructure")

    if any(kw in combined_text for kw in ["checkpoint", "memory", "embedding", "session_start"]):
        domains.append("memory")

    if any(kw in combined_text for kw in ["blog", "writing", "publish", "content"]):
        domains.append("blogging")

    if any(kw in combined_text for kw in ["music", "audio", "midi"]):
        domains.append("music")

    if any(kw in combined_text for kw in ["haist", "symbiosis", "relational", "partnership"]):
        domains.append("research")

    return list(set(domains))  # Deduplicate


class CheckpointIngestor:
    """
    Ingests session checkpoints into Qdrant vector database.
    Creates collections for different memory layers.
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "rhiz_memories",
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize the checkpoint ingestor.

        Args:
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            collection_name: Name of the Qdrant collection
            max_retries: Connection retry attempts (default: 3)
            retry_delay: Seconds between retries (default: 2)
        """
        import time

        print(f"Connecting to Qdrant at {qdrant_host}:{qdrant_port}...")

        for attempt in range(1, max_retries + 1):
            try:
                self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
                # Verify connection with health check
                self.client.get_collections()
                print(f"[OK] Connected to Qdrant successfully")
                break
            except Exception as e:
                if attempt < max_retries:
                    print(f"  Connection attempt {attempt} failed: {e}")
                    print(f"  Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError(
                        f"Failed to connect to Qdrant after {max_retries} attempts.\n"
                        f"Error: {e}\n"
                        f"Verify Qdrant is running: docker ps | grep qdrant\n"
                        f"Start Qdrant: docker start qdrant"
                    )

        self.collection_name = collection_name
        self.embedder = EmbeddingGenerator()

        # Initialize collection if it doesn't exist
        self._ensure_collection()

    def _ensure_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            print(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedder.get_dimension(),
                    distance=Distance.COSINE
                )
            )
            print(f"Collection '{self.collection_name}' created successfully!")
        else:
            print(f"Collection '{self.collection_name}' already exists.")

    def load_checkpoint(self, checkpoint_path: Path) -> Optional[Dict]:
        """
        Load a checkpoint YAML file.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            Parsed checkpoint dictionary or None if error
        """
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data
        except Exception as e:
            print(f"Error loading {checkpoint_path}: {e}")
            return None

    def ingest_checkpoint(self, checkpoint_path: Path) -> bool:
        """
        Ingest a single checkpoint into Qdrant.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            True if successful, False otherwise
        """
        # Load checkpoint
        checkpoint = self.load_checkpoint(checkpoint_path)
        if not checkpoint:
            return False

        print(f"\nIngesting: {checkpoint_path.name}")

        # Unwrap checkpoint if using schema v1.0.0 format
        # New format: {checkpoint: {session_arc: ...}}
        # Old format: {session_arc: ...}
        if "checkpoint" in checkpoint and isinstance(checkpoint["checkpoint"], dict):
            checkpoint = checkpoint["checkpoint"]

        # Generate embeddings
        embeddings = self.embedder.embed_checkpoint(checkpoint)

        # Extract frontmatter for hybrid search (backward compatible)
        frontmatter = checkpoint.get("frontmatter", {})

        # Prepare base metadata
        metadata = {
            "source_file": checkpoint_path.name,
            "checkpoint_id": checkpoint.get("session_id", "unknown"),  # Fixed: use session_id
            "session_date": extract_session_date(checkpoint),  # Fixed: smart extraction
            "session_type": checkpoint.get("session_type", "unknown"),
            "phase": extract_phase(checkpoint),  # Fixed: multi-path extraction
            "ingested_at": datetime.now().isoformat()
        }

        # Add frontmatter fields for keyword filtering (if present)
        if frontmatter and frontmatter.get("domains"):
            # Use explicit domains from frontmatter
            metadata["domains"] = frontmatter.get("domains", [])
            metadata["keywords"] = frontmatter.get("keywords", [])

            # Session classification
            session_type_fm = frontmatter.get("session_type", {})
            if session_type_fm:
                metadata["session_type_primary"] = session_type_fm.get("primary", "unknown")
                metadata["session_type_secondary"] = session_type_fm.get("secondary", [])

            # Technical stack
            tech_stack = frontmatter.get("technical_stack", {})
            if tech_stack:
                metadata["languages"] = tech_stack.get("languages", [])
                metadata["frameworks"] = tech_stack.get("frameworks", [])
                metadata["services"] = tech_stack.get("services", [])
                metadata["tools"] = tech_stack.get("tools", [])

            # Pattern and skill references
            metadata["patterns_used"] = [
                p.get("pattern_name", "") if isinstance(p, dict) else p
                for p in frontmatter.get("patterns_used", [])
            ]
            metadata["skills_executed"] = [
                s.get("skill_name", "") if isinstance(s, dict) else s
                for s in frontmatter.get("skills_executed", [])
            ]

            # Problem solving context
            metadata["blockers_resolved"] = [
                b.get("type", "") if isinstance(b, dict) else b
                for b in frontmatter.get("blockers_resolved", [])
            ]
            metadata["decision_types"] = frontmatter.get("decision_types", [])

            # Discovery and learning
            metadata["discoveries"] = frontmatter.get("discoveries", [])

            # Quality metadata
            completeness = frontmatter.get("completeness", {})
            if completeness:
                metadata["completeness_status"] = completeness.get("status", "unknown")

            notable = frontmatter.get("notable", {})
            if notable:
                metadata["is_notable"] = notable.get("is_notable", False)
                metadata["notable_reason"] = notable.get("reason", "")
        else:
            # Infer domains from content when frontmatter missing
            metadata["domains"] = infer_domains_from_content(checkpoint)
            metadata["keywords"] = []
            metadata["patterns_used"] = []
            metadata["decision_types"] = []

        # Create points for each embedded section
        points = []

        # Main combined embedding (for general semantic search)
        if "combined" in embeddings:
            point_id = str(uuid.uuid4())
            points.append(PointStruct(
                id=point_id,
                vector=embeddings["combined"].tolist(),
                payload={
                    **metadata,
                    "section": "combined",
                    "content": {
                        "session_arc": checkpoint.get("session_arc", ""),
                        "mental_model": checkpoint.get("working_memory", {}).get("mental_model", ""),
                        "resume_prompt": checkpoint.get("suggested_resume_prompt", "")
                    }
                }
            ))

        # Session arc embedding
        if "session_arc" in embeddings:
            point_id = str(uuid.uuid4())
            points.append(PointStruct(
                id=point_id,
                vector=embeddings["session_arc"].tolist(),
                payload={
                    **metadata,
                    "section": "session_arc",
                    "content": checkpoint.get("session_arc", "")
                }
            ))

        # Mental model embedding
        if "mental_model" in embeddings:
            point_id = str(uuid.uuid4())
            points.append(PointStruct(
                id=point_id,
                vector=embeddings["mental_model"].tolist(),
                payload={
                    **metadata,
                    "section": "mental_model",
                    "content": checkpoint.get("working_memory", {}).get("mental_model", "")
                }
            ))

        # Resume prompt embedding
        if "resume_prompt" in embeddings:
            point_id = str(uuid.uuid4())
            points.append(PointStruct(
                id=point_id,
                vector=embeddings["resume_prompt"].tolist(),
                payload={
                    **metadata,
                    "section": "resume_prompt",
                    "content": checkpoint.get("suggested_resume_prompt", "")
                }
            ))

        # Decisions (if multiple, create separate points)
        if "decisions" in embeddings:
            decisions = checkpoint.get("decisions_made", [])
            if isinstance(decisions, list):
                for idx, decision_embedding in enumerate(embeddings["decisions"]):
                    point_id = str(uuid.uuid4())
                    decision_data = decisions[idx] if idx < len(decisions) else {}
                    points.append(PointStruct(
                        id=point_id,
                        vector=decision_embedding.tolist(),
                        payload={
                            **metadata,
                            "section": "decision",
                            "decision_index": idx,
                            "content": decision_data
                        }
                    ))

        # Upload to Qdrant
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"[OK] Ingested {len(points)} memory points from {checkpoint_path.name}")
            return True
        else:
            print(f"[SKIP] No embeddings generated for {checkpoint_path.name}")
            return False

    def ingest_directory(self, checkpoint_dir: Path) -> Dict[str, int]:
        """
        Ingest all checkpoints in a directory.

        Args:
            checkpoint_dir: Path to directory containing checkpoints

        Returns:
            Dictionary with ingestion statistics
        """
        checkpoint_files = list(checkpoint_dir.glob("*.yaml")) + list(checkpoint_dir.glob("*.yml"))

        if not checkpoint_files:
            print(f"No checkpoint files found in {checkpoint_dir}")
            return {"total": 0, "success": 0, "failed": 0}

        print(f"\nFound {len(checkpoint_files)} checkpoint files")
        print("=" * 60)

        stats = {"total": len(checkpoint_files), "success": 0, "failed": 0}

        for checkpoint_path in tqdm(checkpoint_files, desc="Ingesting checkpoints"):
            if self.ingest_checkpoint(checkpoint_path):
                stats["success"] += 1
            else:
                stats["failed"] += 1

        print("\n" + "=" * 60)
        print(f"Ingestion complete: {stats['success']}/{stats['total']} successful")
        if stats["failed"] > 0:
            print(f"[WARNING] {stats['failed']} files failed to ingest")

        return stats

    def get_collection_info(self) -> Dict:
        """Get information about the current collection."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {}


def ingest_checkpoints(checkpoint_dir: str, qdrant_host: str = "localhost", qdrant_port: int = 6333):
    """
    Convenience function to ingest all checkpoints.

    Args:
        checkpoint_dir: Path to checkpoint directory
        qdrant_host: Qdrant server host
        qdrant_port: Qdrant server port
    """
    ingestor = CheckpointIngestor(qdrant_host=qdrant_host, qdrant_port=qdrant_port)
    checkpoint_path = Path(checkpoint_dir)

    if not checkpoint_path.exists():
        print(f"Error: Directory not found: {checkpoint_dir}")
        return

    stats = ingestor.ingest_directory(checkpoint_path)

    # Show collection info
    print("\nCollection Info:")
    info = ingestor.get_collection_info()
    for key, value in info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    import sys

    # Default checkpoint directory
    default_dir = Path(__file__).parent.parent / "checkpoints"

    if len(sys.argv) > 1:
        checkpoint_dir = sys.argv[1]
    else:
        checkpoint_dir = str(default_dir)

    print(f"Rhiz Memory System - Checkpoint Ingestion")
    print(f"Checkpoint directory: {checkpoint_dir}")
    print("")

    ingest_checkpoints(checkpoint_dir)
