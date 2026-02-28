#!/usr/bin/env python3
"""
Memory Explorer CLI
Command-line interface for exploring patterns across session checkpoints.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pattern_extractor import PatternExtractor
from timeline_visualizer import TimelineVisualizer


def main():
    parser = argparse.ArgumentParser(
        description="Rhiz Memory Pattern Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python explorer.py summary              # Generate full pattern report
  python explorer.py timeline confidence  # Show decision confidence timeline
  python explorer.py timeline domains     # Show domain activity heatmap
  python explorer.py phases               # List phase transitions
  python explorer.py gotchas              # List all learning outcomes
  python explorer.py export patterns.json # Export all patterns to JSON
        """
    )

    parser.add_argument(
        "command",
        choices=["summary", "timeline", "phases", "gotchas", "export"],
        help="Command to execute"
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        help="Subcommand for timeline (confidence|domains|phases|gotchas)"
    )
    parser.add_argument(
        "--output",
        help="Output file for export command"
    )
    parser.add_argument(
        "--checkpoints-dir",
        help="Path to checkpoints directory (default: ../../core/memory/checkpoints)",
        default=None
    )

    args = parser.parse_args()

    # Determine checkpoints directory
    if args.checkpoints_dir:
        checkpoints_dir = Path(args.checkpoints_dir)
    else:
        # Default to checkpoints directory
        rhiz_root = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent))
        checkpoints_dir = rhiz_root / "core" / "memory" / "checkpoints"

    if not checkpoints_dir.exists():
        print(f"Error: Checkpoints directory not found: {checkpoints_dir}", file=sys.stderr)
        sys.exit(1)

    # Initialize extractor and visualizer
    extractor = PatternExtractor(checkpoints_dir)
    visualizer = TimelineVisualizer()

    # Execute command
    try:
        if args.command == "summary":
            print(extractor.generate_summary_report())

        elif args.command == "timeline":
            if not args.subcommand:
                print("Error: timeline command requires subcommand (confidence|domains|phases|gotchas)", file=sys.stderr)
                sys.exit(1)

            if args.subcommand == "confidence":
                data = extractor.extract_decision_confidence()
                print(visualizer.visualize_decision_confidence(data['timeline']))

            elif args.subcommand == "domains":
                data = extractor.extract_domain_activity()
                print(visualizer.visualize_domain_activity(data['timeline']))

            elif args.subcommand == "phases":
                transitions = extractor.extract_phase_transitions()
                print(visualizer.visualize_phase_timeline(transitions))

            elif args.subcommand == "gotchas":
                gotchas = extractor.extract_gotchas()
                print(visualizer.visualize_gotchas_timeline(gotchas))

            else:
                print(f"Error: Unknown timeline subcommand: {args.subcommand}", file=sys.stderr)
                print("Valid subcommands: confidence, domains, phases, gotchas", file=sys.stderr)
                sys.exit(1)

        elif args.command == "phases":
            transitions = extractor.extract_phase_transitions()
            print(json.dumps(transitions, indent=2))

        elif args.command == "gotchas":
            gotchas = extractor.extract_gotchas()
            print(json.dumps(gotchas, indent=2))

        elif args.command == "export":
            output_file = args.output or "patterns.json"

            # Extract all patterns
            patterns = {
                'metadata': {
                    'total_checkpoints': len(extractor.checkpoints),
                    'checkpoints_directory': str(checkpoints_dir),
                    'extraction_timestamp': extractor.checkpoints[-1]['_source_file'] if extractor.checkpoints else 'unknown'
                },
                'decision_confidence': extractor.extract_decision_confidence(),
                'phase_transitions': extractor.extract_phase_transitions(),
                'gotchas': extractor.extract_gotchas(),
                'domain_activity': extractor.extract_domain_activity()
            }

            # Write to file
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(patterns, f, indent=2)

            print(f"Patterns exported to {output_path}")
            print(f"  Total checkpoints: {patterns['metadata']['total_checkpoints']}")
            print(f"  Total decisions: {sum(t['total_decisions'] for t in patterns['decision_confidence']['timeline'])}")
            print(f"  Phase transitions: {len(patterns['phase_transitions'])}")
            print(f"  Learning outcomes: {patterns['gotchas']['total']}")

    except Exception as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
