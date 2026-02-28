"""
Checkpoint Schema Validation for Rhiz Memory System

Validates checkpoint data against session_schema.yaml to prevent:
- Quality degradation (Dec 0.73 → Jan 0.14)
- Missing required fields
- Schema drift
- YAML syntax errors

Created: 2026-01-19
Purpose: Enforce schema compliance before checkpoint write
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class CheckpointValidator:
    """Validates checkpoint data against canonical session schema."""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize validator with session schema.

        Args:
            schema_path: Path to session_schema.yaml (auto-detected if None)
        """
        if schema_path is None:
            # Auto-detect schema location
            memory_dir = Path(__file__).parent.parent
            schema_path = memory_dir / "session_schema.yaml"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = yaml.safe_load(f)

        self.schema_version = self.schema.get("schema_version", "unknown")

    def validate(self, checkpoint_data: dict) -> Tuple[bool, List[str], float]:
        """
        Validate checkpoint against schema.

        Args:
            checkpoint_data: Parsed checkpoint dictionary

        Returns:
            Tuple of (is_valid, errors, quality_score)
            - is_valid: True if passes minimum quality threshold
            - errors: List of validation error messages
            - quality_score: 0.0 to 1.0 (higher is better)
        """
        errors = []
        score_components = {}

        # Check top-level structure
        if "checkpoint" not in checkpoint_data:
            errors.append("CRITICAL: Missing top-level 'checkpoint' key")
            return False, errors, 0.0

        checkpoint = checkpoint_data["checkpoint"]

        # Validate required top-level fields
        required_top_level = ["schema_version", "created", "session_id"]
        for field in required_top_level:
            if field not in checkpoint:
                errors.append(f"Missing required field: checkpoint.{field}")
            elif checkpoint[field] is None or str(checkpoint[field]).strip() == "":
                errors.append(f"Empty required field: checkpoint.{field}")

        score_components["required_fields"] = 1.0 if not any(
            "required field" in e for e in errors
        ) else 0.0

        # Validate context section
        if "context" not in checkpoint:
            errors.append("Missing 'context' section")
            score_components["context"] = 0.0
        else:
            context = checkpoint["context"]
            if "human" in context:
                human = context["human"]
                human_fields = ["name", "role", "preferences_discovered"]
                has_all = all(field in human for field in human_fields)
                score_components["context"] = 1.0 if has_all else 0.5
            else:
                errors.append("Missing context.human")
                score_components["context"] = 0.0

        # Validate session_arc (critical for continuity)
        if "session_arc" not in checkpoint:
            errors.append("CRITICAL: Missing 'session_arc' - required for session handshake")
            score_components["session_arc"] = 0.0
        else:
            arc = checkpoint["session_arc"]
            if isinstance(arc, str):
                arc_len = len(arc.strip())
                if arc_len == 0:
                    errors.append("session_arc is empty")
                    score_components["session_arc"] = 0.0
                elif arc_len < 100:
                    errors.append(f"session_arc too short ({arc_len} chars, expect 200+)")
                    score_components["session_arc"] = 0.3
                else:
                    score_components["session_arc"] = 1.0
            elif isinstance(arc, dict):
                # New format (Jan 2026) - dict with narrative
                if "narrative" in arc and len(str(arc["narrative"])) > 100:
                    score_components["session_arc"] = 1.0
                else:
                    errors.append("session_arc dict missing adequate narrative")
                    score_components["session_arc"] = 0.5
            else:
                errors.append(f"session_arc has invalid type: {type(arc)}")
                score_components["session_arc"] = 0.0

        # Validate working_memory
        if "working_memory" not in checkpoint:
            errors.append("Missing 'working_memory' section")
            score_components["working_memory"] = 0.0
        else:
            wm = checkpoint["working_memory"]
            wm_score = 0.0

            # Check mental_model
            if "mental_model" in wm and wm["mental_model"]:
                mm = wm["mental_model"]
                if isinstance(mm, str) and len(mm.strip()) > 50:
                    wm_score += 0.4
                elif isinstance(mm, (list, dict)) and mm:
                    wm_score += 0.4
                else:
                    errors.append("working_memory.mental_model present but inadequate")

            # Check active_hypotheses
            if "active_hypotheses" in wm and wm["active_hypotheses"]:
                wm_score += 0.3

            # Check open_questions
            if "open_questions" in wm and wm["open_questions"]:
                wm_score += 0.3

            score_components["working_memory"] = wm_score

        # Validate decisions_made
        if "decisions_made" not in checkpoint:
            errors.append("Missing 'decisions_made' section")
            score_components["decisions"] = 0.0
        else:
            decisions = checkpoint["decisions_made"]
            if isinstance(decisions, list) and len(decisions) > 0:
                # Check if decisions have reasoning
                has_reasoning = any(
                    isinstance(d, dict) and "reasoning" in d
                    for d in decisions
                )
                score_components["decisions"] = 1.0 if has_reasoning else 0.5
            elif isinstance(decisions, str) and len(decisions.strip()) > 20:
                score_components["decisions"] = 0.7
            else:
                score_components["decisions"] = 0.0

        # Validate alternatives_rejected
        if "alternatives_rejected" in checkpoint:
            alts = checkpoint["alternatives_rejected"]
            if isinstance(alts, list) and len(alts) > 0:
                score_components["alternatives"] = 1.0
            elif isinstance(alts, str) and len(alts.strip()) > 20:
                score_components["alternatives"] = 0.7
            else:
                score_components["alternatives"] = 0.3
        else:
            score_components["alternatives"] = 0.0

        # Validate next section
        if "next" not in checkpoint:
            errors.append("Missing 'next' section")
            score_components["next"] = 0.0
        else:
            next_section = checkpoint["next"]
            next_score = 0.0

            if "immediate" in next_section and next_section["immediate"]:
                next_score += 0.4

            if "blocked_by" in next_section:
                next_score += 0.3

            if "requires_captain_input" in next_section:
                next_score += 0.3

            score_components["next"] = next_score

        # Validate suggested_resume_prompt (critical for session_start)
        if "suggested_resume_prompt" not in checkpoint:
            errors.append("CRITICAL: Missing 'suggested_resume_prompt' - breaks session handshake")
            score_components["resume_prompt"] = 0.0
        else:
            prompt = checkpoint["suggested_resume_prompt"]
            if isinstance(prompt, str) and len(prompt.strip()) > 50:
                score_components["resume_prompt"] = 1.0
            else:
                errors.append("suggested_resume_prompt too short or empty")
                score_components["resume_prompt"] = 0.0

        # Calculate overall quality score
        if score_components:
            quality_score = sum(score_components.values()) / len(score_components)
        else:
            quality_score = 0.0

        # Determine if valid (passes minimum threshold)
        is_valid = quality_score >= 0.5 and not any("CRITICAL" in e for e in errors)

        return is_valid, errors, quality_score

    def validate_and_report(self, checkpoint_data: dict) -> Dict:
        """
        Validate checkpoint and return detailed report.

        Args:
            checkpoint_data: Parsed checkpoint dictionary

        Returns:
            Dictionary with validation results and recommendations
        """
        is_valid, errors, quality_score = self.validate(checkpoint_data)

        report = {
            "valid": is_valid,
            "quality_score": round(quality_score, 3),
            "errors": errors,
            "warnings": [],
            "recommendations": []
        }

        # Generate quality assessment
        if quality_score >= 0.8:
            report["quality_level"] = "EXCELLENT"
        elif quality_score >= 0.6:
            report["quality_level"] = "GOOD"
            report["recommendations"].append("Consider adding more detail to working_memory and alternatives_rejected")
        elif quality_score >= 0.4:
            report["quality_level"] = "FAIR"
            report["recommendations"].append("CRITICAL: session_arc and suggested_resume_prompt need significant expansion")
        else:
            report["quality_level"] = "POOR"
            report["recommendations"].append("URGENT: Checkpoint missing critical sections - session continuity at risk")

        # Add specific warnings based on errors
        if any("session_arc" in e for e in errors):
            report["warnings"].append("Session narrative inadequate - will impact session handshake")

        if any("suggested_resume_prompt" in e for e in errors):
            report["warnings"].append("Resume prompt missing - automatic session restart will fail")

        if any("working_memory" in e for e in errors):
            report["warnings"].append("Working memory incomplete - mental model continuity broken")

        return report

    def format_report(self, report: Dict) -> str:
        """Format validation report as readable text."""
        lines = []
        lines.append("=" * 80)
        lines.append("CHECKPOINT VALIDATION REPORT")
        lines.append("=" * 80)

        # Status (ASCII-safe for Windows)
        status = "[VALID]" if report["valid"] else "[INVALID]"
        lines.append(f"\nStatus: {status}")
        lines.append(f"Quality Score: {report['quality_score']:.3f} ({report['quality_level']})")

        # Errors
        if report["errors"]:
            lines.append(f"\n[ERRORS] ({len(report['errors'])}):")
            for error in report["errors"]:
                lines.append(f"  - {error}")

        # Warnings
        if report["warnings"]:
            lines.append(f"\n[WARNINGS] ({len(report['warnings'])}):")
            for warning in report["warnings"]:
                lines.append(f"  - {warning}")

        # Recommendations
        if report["recommendations"]:
            lines.append(f"\n[RECOMMENDATIONS]:")
            for rec in report["recommendations"]:
                lines.append(f"  - {rec}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


def validate_checkpoint_file(filepath: Path) -> Dict:
    """
    Validate a checkpoint file.

    Args:
        filepath: Path to checkpoint YAML file

    Returns:
        Validation report dictionary
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            checkpoint_data = yaml.safe_load(f)

        validator = CheckpointValidator()
        report = validator.validate_and_report(checkpoint_data)
        report["file"] = str(filepath)

        return report

    except yaml.YAMLError as e:
        return {
            "valid": False,
            "quality_score": 0.0,
            "errors": [f"YAML parse error: {e}"],
            "warnings": [],
            "recommendations": ["Fix YAML syntax errors before validation"],
            "quality_level": "INVALID",
            "file": str(filepath)
        }
    except Exception as e:
        return {
            "valid": False,
            "quality_score": 0.0,
            "errors": [f"Validation error: {e}"],
            "warnings": [],
            "recommendations": [],
            "quality_level": "ERROR",
            "file": str(filepath)
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validate_checkpoint.py <checkpoint_file>")
        print("\nValidates checkpoint against session_schema.yaml")
        sys.exit(1)

    checkpoint_path = Path(sys.argv[1])

    if not checkpoint_path.exists():
        print(f"Error: File not found: {checkpoint_path}")
        sys.exit(1)

    # Validate
    report = validate_checkpoint_file(checkpoint_path)

    # Print report
    validator = CheckpointValidator()
    print(validator.format_report(report))

    # Exit with appropriate code
    sys.exit(0 if report["valid"] else 1)
