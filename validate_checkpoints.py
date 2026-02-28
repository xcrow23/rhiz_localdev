"""
Checkpoint Validation Script

Validates all session checkpoints against schema and analyzes quality.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import json

# Constants
CHECKPOINT_DIR = Path("core/memory/checkpoints")
SCHEMA_VERSION = "1.0.0"

# Required top-level fields according to schema
REQUIRED_TOP_LEVEL = ["checkpoint"]
REQUIRED_CHECKPOINT_FIELDS = ["created", "session_id", "session_arc"]

# Important quality fields to check
QUALITY_FIELDS = {
    "checkpoint": ["session_arc", "suggested_resume_prompt"],
    "working_memory": ["mental_model"],
    "decisions": [],
    "progress": ["status"],
    "next": ["immediate"]
}


def validate_checkpoint(file_path: Path) -> Dict[str, Any]:
    """Validate a single checkpoint file."""
    result = {
        "file": file_path.name,
        "valid_yaml": False,
        "schema_compliant": False,
        "has_required_fields": [],
        "missing_fields": [],
        "quality_score": 0.0,
        "quality_notes": [],
        "parse_error": None,
        "schema_version": None,
        "size_kb": round(file_path.stat().st_size / 1024, 2)
    }

    try:
        # Try to parse YAML
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        result["valid_yaml"] = True

        # Check for top-level structure
        if "checkpoint" not in data:
            result["missing_fields"].append("checkpoint (top-level)")
            return result

        result["has_required_fields"].append("checkpoint")
        checkpoint = data["checkpoint"]

        # Check schema version
        result["schema_version"] = checkpoint.get("schema_version", "not specified")

        # Check required checkpoint fields
        for field in REQUIRED_CHECKPOINT_FIELDS:
            if field in checkpoint and checkpoint[field]:
                result["has_required_fields"].append(f"checkpoint.{field}")
            else:
                result["missing_fields"].append(f"checkpoint.{field}")

        # Schema compliance = has all required fields
        result["schema_compliant"] = len(result["missing_fields"]) == 0

        # Quality assessment
        quality_points = 0
        max_points = 0

        # Check session_arc quality (multi-line narrative)
        max_points += 2
        session_arc = checkpoint.get("session_arc", "")
        if session_arc:
            arc_lines = session_arc.strip().split("\n")
            if len(arc_lines) >= 3:
                quality_points += 2
                result["quality_notes"].append("session_arc: comprehensive (3+ lines)")
            elif len(arc_lines) >= 1:
                quality_points += 1
                result["quality_notes"].append("session_arc: present but brief")
        else:
            result["quality_notes"].append("session_arc: missing or empty")

        # Check suggested_resume_prompt
        max_points += 2
        if "next" in data:
            resume_prompt = data["next"].get("suggested_resume_prompt", "")
            if resume_prompt and len(resume_prompt) > 100:
                quality_points += 2
                result["quality_notes"].append("suggested_resume_prompt: rich (100+ chars)")
            elif resume_prompt:
                quality_points += 1
                result["quality_notes"].append("suggested_resume_prompt: present but brief")
        else:
            result["quality_notes"].append("next section missing")

        # Check working_memory
        max_points += 2
        if "working_memory" in data:
            mental_model = data["working_memory"].get("mental_model", "")
            if mental_model and len(mental_model) > 100:
                quality_points += 2
                result["quality_notes"].append("mental_model: comprehensive (100+ chars)")
            elif mental_model:
                quality_points += 1
                result["quality_notes"].append("mental_model: present but brief")
        else:
            result["quality_notes"].append("working_memory section missing")

        # Check decisions with alternatives_rejected
        max_points += 2
        if "decisions" in data and isinstance(data["decisions"], list):
            decisions_with_alts = [d for d in data["decisions"]
                                  if "alternatives_rejected" in d and d["alternatives_rejected"]]
            if decisions_with_alts:
                quality_points += 2
                result["quality_notes"].append(f"decisions: {len(decisions_with_alts)} with alternatives")
            elif data["decisions"]:
                quality_points += 1
                result["quality_notes"].append(f"decisions: {len(data['decisions'])} present")
        else:
            result["quality_notes"].append("decisions section missing or empty")

        # Check progress narrative
        max_points += 1
        if "progress" in data:
            narrative = data["progress"].get("narrative", "")
            if narrative and len(narrative) > 50:
                quality_points += 1
                result["quality_notes"].append("progress.narrative: present")

        # Check artifacts documentation
        max_points += 1
        if "artifacts" in data and isinstance(data["artifacts"], list) and data["artifacts"]:
            quality_points += 1
            result["quality_notes"].append(f"artifacts: {len(data['artifacts'])} documented")

        result["quality_score"] = round(quality_points / max_points, 2) if max_points > 0 else 0.0

    except yaml.YAMLError as e:
        result["parse_error"] = f"YAML parse error: {str(e)}"
    except Exception as e:
        result["parse_error"] = f"Unexpected error: {str(e)}"

    return result


def generate_report(results: List[Dict[str, Any]]) -> str:
    """Generate validation report."""
    total = len(results)
    valid_yaml = sum(1 for r in results if r["valid_yaml"])
    schema_compliant = sum(1 for r in results if r["schema_compliant"])
    avg_quality = sum(r["quality_score"] for r in results) / total if total > 0 else 0

    # Schema version distribution
    schema_versions = {}
    for r in results:
        ver = r["schema_version"]
        schema_versions[ver] = schema_versions.get(ver, 0) + 1

    # Quality distribution
    quality_dist = {
        "excellent (0.8-1.0)": sum(1 for r in results if r["quality_score"] >= 0.8),
        "good (0.6-0.8)": sum(1 for r in results if 0.6 <= r["quality_score"] < 0.8),
        "fair (0.4-0.6)": sum(1 for r in results if 0.4 <= r["quality_score"] < 0.6),
        "poor (<0.4)": sum(1 for r in results if r["quality_score"] < 0.4)
    }

    report = f"""
# CHECKPOINT VALIDATION REPORT
Generated: {datetime.now().isoformat()}

## Summary Statistics
- Total checkpoints: {total}
- Valid YAML: {valid_yaml}/{total} ({100*valid_yaml/total:.1f}%)
- Schema compliant: {schema_compliant}/{total} ({100*schema_compliant/total:.1f}%)
- Average quality score: {avg_quality:.2f}

## Schema Versions
"""
    for ver, count in sorted(schema_versions.items(), key=lambda x: (x[0] is None, str(x[0]) if x[0] else "")):
        report += f"- {ver}: {count} checkpoints\n"

    report += f"\n## Quality Distribution\n"
    for category, count in quality_dist.items():
        report += f"- {category}: {count} checkpoints\n"

    # Parse errors
    parse_errors = [r for r in results if r["parse_error"]]
    if parse_errors:
        report += f"\n## Parse Errors ({len(parse_errors)})\n"
        for r in parse_errors:
            report += f"- {r['file']}: {r['parse_error']}\n"

    # Schema compliance issues
    non_compliant = [r for r in results if not r["schema_compliant"] and r["valid_yaml"]]
    if non_compliant:
        report += f"\n## Schema Compliance Issues ({len(non_compliant)})\n"
        for r in non_compliant:
            report += f"- {r['file']}:\n"
            for field in r["missing_fields"]:
                report += f"  - Missing: {field}\n"

    # Low quality checkpoints
    low_quality = [r for r in results if r["quality_score"] < 0.5 and r["valid_yaml"]]
    if low_quality:
        report += f"\n## Low Quality Checkpoints (<0.5 score, {len(low_quality)} total)\n"
        for r in low_quality[:5]:  # Show first 5
            report += f"- {r['file']} (score: {r['quality_score']}):\n"
            for note in r["quality_notes"]:
                report += f"  - {note}\n"

    # High quality examples
    high_quality = sorted([r for r in results if r["quality_score"] >= 0.8],
                         key=lambda x: x["quality_score"], reverse=True)
    if high_quality:
        report += f"\n## High Quality Examples (>= 0.8 score, {len(high_quality)} total)\n"
        for r in high_quality[:5]:  # Show top 5
            report += f"- {r['file']} (score: {r['quality_score']})\n"

    return report


def main():
    """Main validation function."""
    print("Validating session checkpoints...\n")

    checkpoint_files = sorted(CHECKPOINT_DIR.glob("session_*.yaml"))
    print(f"Found {len(checkpoint_files)} checkpoint files\n")

    results = []
    for checkpoint_file in checkpoint_files:
        print(f"Validating {checkpoint_file.name}...", end=" ")
        result = validate_checkpoint(checkpoint_file)
        results.append(result)

        if result["parse_error"]:
            print(f"[ERROR] PARSE ERROR")
        elif not result["schema_compliant"]:
            print(f"[WARN] SCHEMA ISSUES")
        else:
            quality = result["quality_score"]
            if quality >= 0.8:
                print(f"[OK] Excellent (quality: {quality})")
            elif quality >= 0.6:
                print(f"[OK] Good (quality: {quality})")
            else:
                print(f"[WARN] Fair (quality: {quality})")

    print("\n" + "="*80)
    report = generate_report(results)
    print(report)

    # Save detailed results
    output_file = Path("checkpoint_validation_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")

    # Save report
    report_file = Path("CHECKPOINT_VALIDATION_REPORT.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved to: {report_file}")


if __name__ == "__main__":
    main()
