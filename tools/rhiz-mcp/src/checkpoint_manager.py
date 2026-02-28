"""
Checkpoint Manager

Handles loading and saving session checkpoints for dyad continuity.

QUALITY ENFORCEMENT (2026-01-19):
- Validates checkpoints against schema before write
- Warns on quality < 0.5 but allows write (non-blocking)
- Prevents quality degradation (Dec 0.73 → Jan 0.14)
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Get checkpoint directory
RHIZ_ROOT = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent.parent))
CHECKPOINT_DIR = RHIZ_ROOT / "core" / "memory" / "checkpoints"

# Import validation (handle both installed and local dev)
try:
    # Try relative import from tools/rhiz-mcp context
    from ..core.memory.scripts.validate_checkpoint import CheckpointValidator
except ImportError:
    # Fall back to absolute import if core/memory is in path
    try:
        sys.path.insert(0, str(RHIZ_ROOT))
        from core.memory.scripts.validate_checkpoint import CheckpointValidator
    except ImportError:
        # Validation not available - warn but continue
        CheckpointValidator = None
        print("[WARNING] CheckpointValidator not available - quality checks disabled",
              file=sys.stderr)


class CheckpointManager:
    """Manager for session checkpoint files."""

    def __init__(self, checkpoint_dir: Optional[Path] = None):
        self.checkpoint_dir = checkpoint_dir or CHECKPOINT_DIR
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def list_checkpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent checkpoints, most recent first"""
        checkpoints = []

        # Find all YAML checkpoint files
        for file_path in self.checkpoint_dir.glob("session_*.yaml"):
            try:
                stat = file_path.stat()
                checkpoints.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size_kb": round(stat.st_size / 1024, 2)
                })
            except Exception as e:
                # Skip files that can't be read
                continue

        # Sort by modified time, most recent first
        checkpoints.sort(key=lambda x: x["modified"], reverse=True)

        return checkpoints[:limit]

    def load_checkpoint(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a checkpoint by filename, or load the most recent if no filename provided

        Args:
            filename: Optional filename to load. If None, loads most recent.

        Returns:
            Checkpoint data as dict
        """
        if filename:
            checkpoint_path = self.checkpoint_dir / filename
            if not checkpoint_path.exists():
                raise FileNotFoundError(f"Checkpoint not found: {filename}")
        else:
            # Load most recent
            checkpoints = self.list_checkpoints(limit=1)
            if not checkpoints:
                raise FileNotFoundError("No checkpoints available")
            checkpoint_path = Path(checkpoints[0]["path"])

        # Load and parse YAML
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse YAML (handle both single document and multi-document)
        try:
            data = yaml.safe_load(content)
            return {
                "filename": checkpoint_path.name,
                "loaded_at": datetime.now().isoformat(),
                "data": data
            }
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in checkpoint: {e}")

    def write_checkpoint(self, checkpoint_data: Dict[str, Any],
                        description: Optional[str] = None,
                        validate: bool = True) -> Tuple[str, Optional[Dict]]:
        """
        Write a new checkpoint file with quality validation

        Args:
            checkpoint_data: The checkpoint data to write
            description: Optional description for filename
            validate: Whether to validate quality (default: True)

        Returns:
            Tuple of (filename, validation_report)
            - filename: Name of written checkpoint file
            - validation_report: Validation results (None if validation disabled)

        Note:
            Validation warnings do NOT block write. Checkpoints with quality < 0.5
            are written but logged as requiring improvement.
        """
        # Generate filename
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y%m%d")

        if description:
            # Clean description for filename
            clean_desc = description.lower().replace(" ", "_")
            clean_desc = "".join(c for c in clean_desc if c.isalnum() or c == "_")
            filename = f"session_{date_str}_{clean_desc}.yaml"
        else:
            time_str = timestamp.strftime("%H%M%S")
            filename = f"session_{date_str}_{time_str}.yaml"

        checkpoint_path = self.checkpoint_dir / filename

        # Ensure checkpoint_data has required structure
        if "checkpoint" not in checkpoint_data:
            # Wrap data in checkpoint structure
            checkpoint_data = {
                "checkpoint": {
                    "schema_version": "1.0.0",
                    "created": timestamp.isoformat(),
                    "session_id": filename.replace(".yaml", ""),
                    **checkpoint_data
                }
            }
        else:
            # Add schema_version if not present
            if "schema_version" not in checkpoint_data["checkpoint"]:
                checkpoint_data["checkpoint"]["schema_version"] = "1.0.0"
            # Add created if not present
            if "created" not in checkpoint_data["checkpoint"]:
                checkpoint_data["checkpoint"]["created"] = timestamp.isoformat()

        # Validate checkpoint quality before writing
        validation_report = None
        if validate and CheckpointValidator is not None:
            try:
                validator = CheckpointValidator()
                validation_report = validator.validate_and_report(checkpoint_data)

                # Log validation results
                quality = validation_report["quality_score"]
                level = validation_report["quality_level"]

                if quality < 0.5:
                    print(f"[CHECKPOINT] ⚠️  QUALITY WARNING: {filename}",
                          file=sys.stderr)
                    print(f"[CHECKPOINT]    Quality: {quality:.3f} ({level})",
                          file=sys.stderr)
                    print(f"[CHECKPOINT]    This checkpoint may impact session continuity",
                          file=sys.stderr)
                    if validation_report["errors"]:
                        print(f"[CHECKPOINT]    Errors: {len(validation_report['errors'])}",
                              file=sys.stderr)
                        for error in validation_report["errors"][:3]:  # Show first 3
                            print(f"[CHECKPOINT]      - {error}", file=sys.stderr)
                elif quality >= 0.8:
                    print(f"[CHECKPOINT] ✅ Quality: {quality:.3f} ({level}) - {filename}",
                          file=sys.stderr)
                else:
                    print(f"[CHECKPOINT] ✓ Quality: {quality:.3f} ({level}) - {filename}",
                          file=sys.stderr)

            except Exception as e:
                print(f"[CHECKPOINT] Validation error (continuing): {e}",
                      file=sys.stderr)

        # Write YAML with header comment
        header = f"""# Rhiz Session Checkpoint
# Created: {timestamp.isoformat()}
# File: {filename}
# Schema: v1.0.0
"""
        if validation_report:
            header += f"# Quality: {validation_report['quality_score']:.3f} ({validation_report['quality_level']})\n"
        header += "\n"

        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            f.write(header)
            yaml.dump(checkpoint_data, f,
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False)

        return filename, validation_report

    def get_resume_context(self, filename: Optional[str] = None) -> str:
        """
        Get resume context from a checkpoint for session handshake

        Args:
            filename: Optional checkpoint to load. If None, uses most recent.

        Returns:
            Formatted resume context string
        """
        checkpoint = self.load_checkpoint(filename)
        data = checkpoint["data"]

        # Extract key fields for resume context
        cp = data.get("checkpoint", {})

        session_arc = cp.get("session_arc", "No session arc available")
        next_actions = cp.get("next_immediate", [])
        in_progress = cp.get("in_progress", [])
        learning = cp.get("learning", [])

        # Format resume context
        context = f"""## Session Resume Context

**Last Session**: {checkpoint['filename']}
**Created**: {cp.get('created', 'unknown')}

### Session Arc
{session_arc}

### Next Immediate Actions
"""
        if next_actions:
            for action in next_actions:
                context += f"- {action}\n"
        else:
            context += "- None specified\n"

        context += "\n### In Progress\n"
        if in_progress:
            for item in in_progress:
                context += f"- {item}\n"
        else:
            context += "- Nothing in progress\n"

        context += "\n### Key Learning\n"
        if learning:
            for item in learning:
                context += f"- {item}\n"
        else:
            context += "- No learning captured\n"

        suggested_resume = cp.get("suggested_resume_prompt", "")
        if suggested_resume:
            context += f"\n### Suggested Resume Prompt\n{suggested_resume}\n"

        return context
