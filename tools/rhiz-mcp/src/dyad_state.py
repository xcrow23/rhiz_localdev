"""
Dyad State Management

Handles reading and updating the system-managed dyad.md file.
This module provides the core state operations for the Rhiz dyad.
"""

import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Path to dyad state file - use RHIZ_ROOT env var if available
RHIZ_ROOT = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent.parent))
DYAD_STATE_PATH = RHIZ_ROOT / "core" / "daemon" / "dyad.md"

# Valid enum values for state fields
VALID_AVAILABILITY = {"engaged", "available", "away", "unknown"}
VALID_ENERGY = {"high", "medium", "low", "unknown"}
VALID_DOMAIN_STATUS = {"connected", "healthy", "degraded", "disconnected", "unknown"}
VALID_NOTE_CATEGORIES = {"strengths_observed", "friction_points", "evolution_suggestions"}


class DyadState:
    """Manager for dyad.md state document."""

    def __init__(self, state_path: Optional[Path] = None):
        self.state_path = state_path or DYAD_STATE_PATH
        self._state_cache = None
        self._last_load = None

    def load_state(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load current dyad state from dyad.md"""
        if not force_reload and self._state_cache and self._last_load:
            # Cache valid for 1 second to reduce I/O
            if (datetime.now() - self._last_load).total_seconds() < 1:
                return self._state_cache

        if not self.state_path.exists():
            raise FileNotFoundError(f"Dyad state file not found: {self.state_path}")

        content = self.state_path.read_text(encoding='utf-8')
        state = self._parse_dyad_md(content)

        self._state_cache = state
        self._last_load = datetime.now()

        return state

    def _parse_dyad_md(self, content: str) -> Dict[str, Any]:
        """Parse dyad.md markdown/YAML hybrid format"""
        state = {}

        # Extract YAML blocks by section
        sections = [
            'DYAD_STATE', 'CAPTAIN_STATE', 'FIRST_MATE_STATE',
            'SHARED_FOCUS', 'ACTIVE_DOMAINS', 'DYAD_HISTORY',
            'METRICS', 'NOTES'
        ]

        for section in sections:
            pattern = rf'## {section}\s*```yaml\s*(.*?)```'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                yaml_content = match.group(1).strip()
                state[section.lower()] = self._parse_yaml_simple(yaml_content)

        return state

    def _parse_yaml_simple(self, yaml_str: str) -> Dict[str, Any]:
        """Parse YAML using PyYAML library for robust handling"""
        import yaml
        try:
            result = yaml.safe_load(yaml_str)
            return result if result is not None else {}
        except yaml.YAMLError as e:
            # Fallback to empty dict on parse error
            print(f"Warning: YAML parse error: {e}", file=sys.stderr)
            return {}

    def update_captain_state(self, availability: Optional[str] = None,
                           focus: Optional[str] = None,
                           energy: Optional[str] = None,
                           physical_context: Optional[str] = None) -> Dict[str, Any]:
        """Update Captain state fields"""
        # Validate enum values
        if availability and availability not in VALID_AVAILABILITY:
            raise ValueError(f"Invalid availability '{availability}'. Must be one of: {VALID_AVAILABILITY}")
        if energy and energy not in VALID_ENERGY:
            raise ValueError(f"Invalid energy '{energy}'. Must be one of: {VALID_ENERGY}")

        state = self.load_state(force_reload=True)
        captain = state.get('captain_state', {})

        if availability:
            captain['availability'] = availability
        if focus:
            captain['focus'] = focus
        if energy:
            captain['energy'] = energy
        if physical_context:
            captain['physical_context'] = physical_context

        captain['last_active'] = datetime.now().isoformat()

        self._write_section_update('CAPTAIN_STATE', captain)
        return captain

    def update_first_mate_state(self, session_id: Optional[str] = None,
                               context_loaded: Optional[str] = None,
                               capabilities_active: Optional[List[str]] = None) -> Dict[str, Any]:
        """Update First Mate state fields"""
        state = self.load_state(force_reload=True)
        fm = state.get('first_mate_state', {})

        if session_id:
            fm['session_id'] = session_id
        if context_loaded:
            fm['context_loaded'] = context_loaded
        if capabilities_active is not None:
            fm['capabilities_active'] = capabilities_active

        fm['last_active'] = datetime.now().isoformat()

        self._write_section_update('FIRST_MATE_STATE', fm)
        return fm

    def update_shared_focus(self, domain: Optional[str] = None,
                          objective: Optional[str] = None,
                          blockers: Optional[List[str]] = None,
                          next_action: Optional[str] = None) -> Dict[str, Any]:
        """Update shared focus section"""
        state = self.load_state(force_reload=True)
        focus = state.get('shared_focus', {})

        if domain:
            focus['domain'] = domain
        if objective:
            focus['objective'] = objective
        if blockers is not None:
            focus['blockers'] = blockers
        if next_action:
            focus['next_action'] = next_action

        self._write_section_update('SHARED_FOCUS', focus)
        return focus

    def update_active_domain(self, domain: str, status: str, details: Optional[str] = None) -> Dict[str, Any]:
        """Update status of an active domain"""
        # Validate status
        if status not in VALID_DOMAIN_STATUS:
            raise ValueError(f"Invalid domain status '{status}'. Must be one of: {VALID_DOMAIN_STATUS}")

        state = self.load_state(force_reload=True)
        domains = state.get('active_domains', {})

        if domain not in domains:
            domains[domain] = {}

        domains[domain]['status'] = status
        domains[domain]['last_check'] = datetime.now().isoformat()

        if details:
            domains[domain]['details'] = details

        self._write_section_update('ACTIVE_DOMAINS', domains)
        return domains[domain]

    def increment_metric(self, metric_name: str, increment: int = 1) -> int:
        """Increment a metric counter"""
        state = self.load_state(force_reload=True)
        metrics = state.get('metrics', {})

        current = metrics.get(metric_name, 0)
        new_value = current + increment
        metrics[metric_name] = new_value

        self._write_section_update('METRICS', metrics)
        return new_value

    def append_note(self, category: str, note: str):
        """Append a note to strengths_observed, friction_points, or evolution_suggestions"""
        # Validate category
        if category not in VALID_NOTE_CATEGORIES:
            raise ValueError(f"Invalid note category '{category}'. Must be one of: {VALID_NOTE_CATEGORIES}")

        state = self.load_state(force_reload=True)
        notes = state.get('notes', {})

        if category not in notes:
            notes[category] = []

        if note not in notes[category]:
            notes[category].append(note)

        self._write_section_update('NOTES', notes)

    def _write_section_update(self, section: str, data: Dict[str, Any]):
        """Update a specific section in dyad.md using atomic write"""
        # Read current content
        content = self.state_path.read_text(encoding='utf-8')

        # Convert data to YAML format
        yaml_content = self._dict_to_yaml(data)

        # Replace the section (preserving header but cleaning excessive whitespace)
        pattern = rf'(## {section}\s*```yaml)\s*.*?\s*(```)'
        replacement = rf'\1\n{yaml_content}\n\2'
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # Update last sync timestamp
        updated_content = re.sub(
            r'Last Updated: .*',
            f'Last Updated: {datetime.now().isoformat()}Z',
            updated_content
        )

        # Atomic write: write to temp file then rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.state_path.parent,
            prefix='.dyad_',
            suffix='.md.tmp',
            text=True
        )

        try:
            # Write to temp file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk

            # Atomic rename (os.replace works on both Windows and POSIX)
            os.replace(temp_path, self.state_path)

        except Exception as e:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except:
                pass
            raise e

        self._state_cache = None  # Invalidate cache

    def _dict_to_yaml(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Convert dict to simple YAML format"""
        lines = []
        indent_str = '  ' * indent

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{indent_str}{key}:")
                lines.append(self._dict_to_yaml(value, indent + 1))
            elif isinstance(value, list):
                if not value:
                    lines.append(f"{indent_str}{key}: []")
                else:
                    lines.append(f"{indent_str}{key}:")
                    for item in value:
                        lines.append(f"{indent_str}  - {item}")
            elif isinstance(value, bool):
                lines.append(f"{indent_str}{key}: {str(value).lower()}")
            elif value is None:
                lines.append(f"{indent_str}{key}: unknown")
            else:
                lines.append(f"{indent_str}{key}: {value}")

        return '\n'.join(lines)

    def get_full_state(self) -> Dict[str, Any]:
        """Get complete dyad state"""
        return self.load_state(force_reload=True)

    def get_captain_state(self) -> Dict[str, Any]:
        """Get Captain state"""
        state = self.load_state()
        return state.get('captain_state', {})

    def get_shared_focus(self) -> Dict[str, Any]:
        """Get shared focus"""
        state = self.load_state()
        return state.get('shared_focus', {})

    def get_dyad_summary(self) -> str:
        """Get human-readable dyad state summary"""
        state = self.load_state()

        captain = state.get('captain_state', {})
        fm = state.get('first_mate_state', {})
        focus = state.get('shared_focus', {})
        history = state.get('dyad_history', {})

        summary = [
            "## Dyad State Summary",
            "",
            f"**Container**: Rhiz v{state.get('dyad_state', {}).get('version', 'unknown')}",
            f"**Sessions Together**: {history.get('sessions_together', 0)}",
            f"**Trust Calibration**: {history.get('trust_calibration', 'unknown')}",
            "",
            "### Captain",
            f"- Availability: {captain.get('availability', 'unknown')}",
            f"- Focus: {captain.get('focus', 'unknown')}",
            f"- Energy: {captain.get('energy', 'unknown')}",
            "",
            "### First Mate",
            f"- Model: {fm.get('model', 'unknown')}",
            f"- Session: {fm.get('session_id', 'none')}",
            f"- Context: {fm.get('context_loaded', 'none')}",
            "",
            "### Shared Focus",
            f"- Domain: {focus.get('domain', 'none')}",
            f"- Objective: {focus.get('objective', 'none')}",
            f"- Next Action: {focus.get('next_action', 'unknown')}",
        ]

        return '\n'.join(summary)
