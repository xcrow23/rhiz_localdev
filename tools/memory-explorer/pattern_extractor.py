"""
Pattern Extractor
Extracts structured patterns from checkpoint YAML files.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any


class PatternExtractor:
    """Extract structured patterns from checkpoint YAML files"""

    def __init__(self, checkpoints_dir: Path):
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoints = self._load_all_checkpoints()

    @staticmethod
    def _safe_ascii(text: str, max_length: int = None) -> str:
        """Ensure text is ASCII-safe for Windows console"""
        if not isinstance(text, str):
            text = str(text)
        text = text.encode('ascii', 'replace').decode('ascii')
        if max_length and len(text) > max_length:
            return text[:max_length] + "..."
        return text

    def _load_all_checkpoints(self) -> List[Dict[str, Any]]:
        """Load all checkpoint YAML files, sorted by date"""
        checkpoints = []

        if not self.checkpoints_dir.exists():
            print(f"Warning: Checkpoints directory not found: {self.checkpoints_dir}")
            return []

        for cp_file in sorted(self.checkpoints_dir.glob("*.yaml")):
            try:
                with open(cp_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        data['_source_file'] = cp_file.name
                        checkpoints.append(data)
            except yaml.YAMLError as e:
                print(f"Warning: Failed to parse {cp_file.name}: {e}")
            except Exception as e:
                print(f"Warning: Error loading {cp_file.name}: {e}")

        print(f"Loaded {len(checkpoints)} checkpoints from {self.checkpoints_dir}")
        return checkpoints

    def extract_decision_confidence(self) -> Dict[str, Any]:
        """Count decisions by confidence level over time"""
        timeline = []

        for cp in self.checkpoints:
            checkpoint_data = cp.get('checkpoint', {})
            decisions = checkpoint_data.get('decisions_made', [])

            counts = {'high': 0, 'medium': 0, 'low': 0}
            for decision in decisions:
                confidence = decision.get('confidence', 'medium')
                if confidence in counts:
                    counts[confidence] += 1

            session_id = checkpoint_data.get('session_id', cp.get('_source_file', 'unknown'))
            session_metadata = checkpoint_data.get('session_metadata', {})
            session_date = session_metadata.get('date', 'unknown')

            timeline.append({
                'session': session_id,
                'date': session_date,
                'confidence_counts': counts,
                'total_decisions': sum(counts.values())
            })

        return {'timeline': timeline}

    def extract_phase_transitions(self) -> List[Dict[str, Any]]:
        """Identify when phase markers changed"""
        transitions = []
        prev_phase = None

        for cp in self.checkpoints:
            checkpoint_data = cp.get('checkpoint', {})
            session_metadata = checkpoint_data.get('session_metadata', {})

            current_phase = session_metadata.get('phase')
            session_id = checkpoint_data.get('session_id', cp.get('_source_file'))
            session_date = session_metadata.get('date', 'unknown')

            if current_phase and current_phase != prev_phase:
                session_arc = checkpoint_data.get('session_arc', {})

                # Extract opening context (handle both dict and string formats)
                if isinstance(session_arc, dict):
                    context = session_arc.get('opening', '')
                elif isinstance(session_arc, str):
                    context = session_arc
                else:
                    context = ''

                # Truncate and ensure ASCII-safe
                context = self._safe_ascii(context, max_length=200)

                transitions.append({
                    'session': session_id,
                    'date': session_date,
                    'from_phase': prev_phase if prev_phase else "(initial)",
                    'to_phase': current_phase,
                    'context': context
                })

                prev_phase = current_phase

        return transitions

    def extract_gotchas(self) -> Dict[str, Any]:
        """Collect all gotchas/learning outcomes across sessions"""
        gotchas = []

        for cp in self.checkpoints:
            checkpoint_data = cp.get('checkpoint', {})
            learning = checkpoint_data.get('learning_outcomes', [])

            session_id = checkpoint_data.get('session_id', cp.get('_source_file'))
            session_metadata = checkpoint_data.get('session_metadata', {})
            session_date = session_metadata.get('date', 'unknown')

            for gotcha in learning:
                # Ensure ASCII-safe gotcha text
                gotcha_text = self._safe_ascii(gotcha) if isinstance(gotcha, str) else str(gotcha)
                gotchas.append({
                    'session': session_id,
                    'date': session_date,
                    'gotcha': gotcha_text
                })

        return {'gotchas': gotchas, 'total': len(gotchas)}

    def extract_domain_activity(self) -> Dict[str, Any]:
        """Track which domains were active per session"""
        timeline = []

        for cp in self.checkpoints:
            checkpoint_data = cp.get('checkpoint', {})
            code_locations = checkpoint_data.get('code_locations', {})

            # Check which domain sections exist in checkpoint
            domains_active = []

            # Convert code_locations to string for searching
            code_locs_str = str(code_locations).lower()

            if 'trading' in code_locs_str or 'fathom' in code_locs_str or 'kraken' in code_locs_str:
                domains_active.append('trading')
            if 'memory' in code_locs_str or 'qdrant' in code_locs_str or 'checkpoint' in code_locs_str:
                domains_active.append('memory')
            if 'skill' in code_locs_str:
                domains_active.append('skills')

            session_id = checkpoint_data.get('session_id', cp.get('_source_file'))
            session_metadata = checkpoint_data.get('session_metadata', {})
            session_date = session_metadata.get('date', 'unknown')

            timeline.append({
                'session': session_id,
                'date': session_date,
                'domains': domains_active
            })

        return {'timeline': timeline}

    def generate_summary_report(self) -> str:
        """Generate human-readable pattern summary"""
        report = []
        report.append("=" * 60)
        report.append("MEMORY PATTERN DISCOVERY REPORT")
        report.append("=" * 60)
        report.append(f"Total Sessions Analyzed: {len(self.checkpoints)}")
        report.append("")

        # Decision confidence
        conf_data = self.extract_decision_confidence()
        total_decisions = sum(
            t['total_decisions'] for t in conf_data['timeline']
        )
        report.append(f"Total Decisions Made: {total_decisions}")

        # Confidence distribution
        if total_decisions > 0:
            total_high = sum(t['confidence_counts']['high'] for t in conf_data['timeline'])
            total_medium = sum(t['confidence_counts']['medium'] for t in conf_data['timeline'])
            total_low = sum(t['confidence_counts']['low'] for t in conf_data['timeline'])

            report.append(f"  High Confidence: {total_high} ({total_high/total_decisions*100:.1f}%)")
            report.append(f"  Medium Confidence: {total_medium} ({total_medium/total_decisions*100:.1f}%)")
            report.append(f"  Low Confidence: {total_low} ({total_low/total_decisions*100:.1f}%)")
        else:
            report.append("  (No decisions recorded)")

        report.append("")

        # Phase transitions
        transitions = self.extract_phase_transitions()
        report.append(f"Phase Transitions Detected: {len(transitions)}")
        for trans in transitions:
            report.append(f"  {trans['date']}: {trans['from_phase']} -> {trans['to_phase']}")
        report.append("")

        # Gotchas
        gotchas = self.extract_gotchas()
        report.append(f"Learning Outcomes Captured: {gotchas['total']}")
        report.append("")

        # Domain activity
        domains = self.extract_domain_activity()
        domain_counts = {}
        for session in domains['timeline']:
            for domain in session['domains']:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1

        report.append("Domain Activity Distribution:")
        if domain_counts:
            for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
                report.append(f"  {domain}: {count} sessions")
        else:
            report.append("  (No domain activity detected)")

        return "\n".join(report)


if __name__ == "__main__":
    import os
    from pathlib import Path

    # Default to checkpoints directory
    rhiz_root = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent))
    checkpoints_dir = rhiz_root / "core" / "memory" / "checkpoints"

    extractor = PatternExtractor(checkpoints_dir)
    print(extractor.generate_summary_report())
