#!/usr/bin/env python3
"""
One-time script to clean up dyad.md formatting issues.
Removes excessive blank lines from YAML sections.
"""

import re
from pathlib import Path

def clean_dyad_md(dyad_path: Path):
    """Remove excessive blank lines from YAML sections"""
    content = dyad_path.read_text(encoding='utf-8')

    # Pattern to match YAML sections with excessive whitespace
    # Captures: (## SECTION\n```yaml) + whitespace + (actual content) + (```)
    def clean_yaml_section(match):
        header = match.group(1)  # ## SECTION\n```yaml
        yaml_content = match.group(2).strip()  # Actual YAML (stripped)
        closing = match.group(3)  # ```

        # Reconstruct with single newline before and after content
        return f"{header}\n{yaml_content}\n{closing}"

    # Apply to all YAML sections
    pattern = r'(##\s+\w+\s*\n```yaml)\s*(.*?)\s*(```)'
    cleaned_content = re.sub(pattern, clean_yaml_section, content, flags=re.DOTALL)

    # Write back
    dyad_path.write_text(cleaned_content, encoding='utf-8')
    print(f"[OK] Cleaned {dyad_path}")

    # Count how many blank lines were removed
    original_lines = len(content.split('\n'))
    cleaned_lines = len(cleaned_content.split('\n'))
    print(f"  Removed {original_lines - cleaned_lines} blank lines")
    print(f"  Original: {original_lines} lines → Cleaned: {cleaned_lines} lines")

if __name__ == "__main__":
    import os
    rhiz_root = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent))
    dyad_path = rhiz_root / "core" / "daemon" / "dyad.md"

    if not dyad_path.exists():
        print(f"Error: dyad.md not found at {dyad_path}")
        exit(1)

    # Backup first
    backup_path = dyad_path.with_suffix('.md.backup')
    backup_path.write_text(dyad_path.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"[OK] Backup created: {backup_path}")

    clean_dyad_md(dyad_path)
