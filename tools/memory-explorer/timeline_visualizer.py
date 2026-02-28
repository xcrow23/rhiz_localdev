"""
Timeline Visualizer
ASCII-based timeline visualization for pattern trends.
"""

from typing import Dict, List, Any


class TimelineVisualizer:
    """ASCII-based timeline visualization for pattern trends"""

    def visualize_decision_confidence(self, timeline_data: List[Dict]) -> str:
        """Show decision confidence over time as ASCII chart"""
        chart = []
        chart.append("DECISION CONFIDENCE TIMELINE")
        chart.append("-" * 60)
        chart.append("")

        for entry in timeline_data:
            session = entry['session']
            counts = entry['confidence_counts']
            total = counts['high'] + counts['medium'] + counts['low']

            if total == 0:
                continue

            # Bar chart representation using ASCII blocks
            bar_high = "#" * counts['high']
            bar_med = "=" * counts['medium']
            bar_low = "." * counts['low']

            # Truncate session name for display
            session_display = session[:20].ljust(20)

            chart.append(f"{session_display} | {bar_high}{bar_med}{bar_low} ({total})")

        chart.append("")
        chart.append("Legend: # = High confidence, = = Medium, . = Low")

        return "\n".join(chart)

    def visualize_domain_activity(self, timeline_data: List[Dict]) -> str:
        """Show domain activity heatmap over time"""
        chart = []
        chart.append("DOMAIN ACTIVITY HEATMAP")
        chart.append("-" * 60)
        chart.append("")

        for entry in timeline_data:
            session = entry['session']
            domains = entry['domains']

            # Domain indicators
            trading_mark = "T" if "trading" in domains else "-"
            memory_mark = "M" if "memory" in domains else "-"
            skills_mark = "S" if "skills" in domains else "-"

            # Truncate session name for display
            session_display = session[:20].ljust(20)

            chart.append(f"{session_display} | [{trading_mark}] [{memory_mark}] [{skills_mark}]")

        chart.append("")
        chart.append("Legend: [T]rading [M]emory [S]kills")

        return "\n".join(chart)

    def visualize_phase_timeline(self, transitions: List[Dict]) -> str:
        """Show phase transitions over time"""
        chart = []
        chart.append("PHASE TRANSITION TIMELINE")
        chart.append("-" * 60)
        chart.append("")

        for trans in transitions:
            date = trans['date']
            from_phase = trans['from_phase']
            to_phase = trans['to_phase']

            # Ensure ASCII-safe output
            from_phase = from_phase.encode('ascii', 'replace').decode('ascii') if from_phase else "(initial)"
            to_phase = to_phase.encode('ascii', 'replace').decode('ascii') if to_phase else "unknown"

            arrow = f"{from_phase:30} -> {to_phase}"
            chart.append(f"{date:12} | {arrow}")

            # Show context preview (ASCII-safe)
            if trans.get('context'):
                context = trans['context'].replace('\n', ' ')
                # Replace non-ASCII characters with '?'
                context = context.encode('ascii', 'replace').decode('ascii')
                chart.append(f"             Context: {context}")
                chart.append("")

        return "\n".join(chart)

    def visualize_gotchas_timeline(self, gotchas_data: Dict) -> str:
        """Show learning outcomes over time"""
        chart = []
        chart.append("LEARNING OUTCOMES TIMELINE")
        chart.append("-" * 60)
        chart.append("")

        gotchas = gotchas_data['gotchas']

        # Group by date
        by_date = {}
        for gotcha in gotchas:
            date = gotcha['date']
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(gotcha)

        # Sort by date and display
        for date in sorted(by_date.keys()):
            chart.append(f"{date}:")
            for gotcha in by_date[date]:
                # Truncate gotcha text
                gotcha_text = gotcha['gotcha']
                if isinstance(gotcha_text, str):
                    # Ensure ASCII-safe output
                    gotcha_text = gotcha_text.encode('ascii', 'replace').decode('ascii')
                    if len(gotcha_text) > 70:
                        gotcha_text = gotcha_text[:70] + "..."
                chart.append(f"  - {gotcha_text}")
            chart.append("")

        return "\n".join(chart)


if __name__ == "__main__":
    import os
    from pathlib import Path
    from pattern_extractor import PatternExtractor

    # Default to checkpoints directory
    rhiz_root = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent))
    checkpoints_dir = rhiz_root / "core" / "memory" / "checkpoints"

    extractor = PatternExtractor(checkpoints_dir)
    visualizer = TimelineVisualizer()

    print("=" * 60)
    print("RHIZ MEMORY PATTERN VISUALIZATIONS")
    print("=" * 60)
    print()

    # Decision confidence timeline
    conf_data = extractor.extract_decision_confidence()
    print(visualizer.visualize_decision_confidence(conf_data['timeline']))
    print()
    print()

    # Domain activity
    domains = extractor.extract_domain_activity()
    print(visualizer.visualize_domain_activity(domains['timeline']))
    print()
    print()

    # Phase transitions
    transitions = extractor.extract_phase_transitions()
    print(visualizer.visualize_phase_timeline(transitions))
    print()
    print()

    # Gotchas
    gotchas = extractor.extract_gotchas()
    print(visualizer.visualize_gotchas_timeline(gotchas))
