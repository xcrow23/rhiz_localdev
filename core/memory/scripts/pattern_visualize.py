"""
Pattern Visualization: Visual Fingerprints for Strudel Patterns
Creates matplotlib visualizations showing mathematical structure.

Usage:
    python pattern_visualize.py <pattern_file.json>
    python pattern_visualize.py --all <patterns_dir>
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
except ImportError:
    print("Error: matplotlib not installed. Run: pip install matplotlib")
    sys.exit(1)

# Import our pattern analyzer
sys.path.insert(0, str(Path(__file__).parent))
from pattern_math import PatternMath, analyze_pattern


# Color palette for visualizations
COLORS = {
    'density': '#4A90D9',      # Steel blue
    'pitch': '#D9534F',        # Coral
    'transform': '#5CB85C',    # Green
    'period': '#F0AD4E',       # Amber
    'background': '#1a1a2e',   # Dark blue-gray
    'grid': '#2d2d44',         # Subtle grid
    'text': '#e0e0e0'          # Light text
}


def create_pattern_fingerprint(pattern_data: dict, output_path: str = None, show: bool = True):
    """
    Create a visual fingerprint of a pattern's mathematical structure.

    Args:
        pattern_data: Parsed pattern JSON with 'pattern' code
        output_path: Optional path to save PNG/SVG
        show: Whether to display the plot
    """
    pattern_code = pattern_data.get('pattern', '')
    name = pattern_data.get('name', 'Unknown')
    genre = pattern_data.get('genre', 'unknown')
    bpm = pattern_data.get('bpm', 120)
    key = pattern_data.get('key', 'C')

    # Analyze pattern
    analysis = analyze_pattern(pattern_code)
    features = analysis['features']
    density = np.array(analysis['density_series'])
    pitches = analysis['pitches']
    transforms = analysis['transforms']

    # Create figure with dark theme
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14, 10), facecolor=COLORS['background'])
    fig.suptitle(f'{name}', fontsize=20, color=COLORS['text'], fontweight='bold', y=0.98)
    fig.text(0.5, 0.94, f'{genre} | {bpm} BPM | {key}', ha='center',
             fontsize=12, color=COLORS['text'], alpha=0.7)

    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3,
                  left=0.08, right=0.92, top=0.88, bottom=0.08)

    # 1. Density Waveform (top, full width)
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(COLORS['background'])

    # Create filled area plot for density
    x = np.arange(len(density))
    ax1.fill_between(x, density, alpha=0.6, color=COLORS['density'])
    ax1.plot(x, density, color=COLORS['density'], linewidth=2)

    # Add beat markers
    for i in range(0, len(density), 4):
        ax1.axvline(x=i, color=COLORS['grid'], linestyle='--', alpha=0.3)

    ax1.set_xlim(0, len(density) - 1)
    ax1.set_ylim(0, max(density) * 1.2 if max(density) > 0 else 1)
    ax1.set_xlabel('Time (16th notes)', color=COLORS['text'])
    ax1.set_ylabel('Event Density', color=COLORS['text'])
    ax1.set_title('Rhythmic Density d(t)', color=COLORS['text'], fontsize=12, pad=10)
    ax1.tick_params(colors=COLORS['text'])

    # 2. Pitch Distribution (middle left)
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(COLORS['background'])

    if pitches:
        # Create pitch histogram
        pitch_range = range(min(pitches) - 2, max(pitches) + 3)
        ax2.hist(pitches, bins=len(pitch_range), color=COLORS['pitch'],
                 alpha=0.7, edgecolor=COLORS['text'], linewidth=0.5)
        ax2.set_xlabel('MIDI Pitch', color=COLORS['text'])
        ax2.set_ylabel('Frequency', color=COLORS['text'])

        # Add pitch labels for common notes
        pitch_labels = {36: 'C2', 48: 'C3', 60: 'C4', 72: 'C5', 84: 'C6'}
        for midi, label in pitch_labels.items():
            if min(pitches) - 2 <= midi <= max(pitches) + 2:
                ax2.axvline(x=midi, color=COLORS['text'], linestyle=':', alpha=0.3)
                ax2.text(midi, ax2.get_ylim()[1] * 0.9, label,
                        ha='center', color=COLORS['text'], fontsize=8)
    else:
        ax2.text(0.5, 0.5, 'No melodic\ncontent', ha='center', va='center',
                transform=ax2.transAxes, color=COLORS['text'], fontsize=12, alpha=0.5)

    ax2.set_title('Pitch Distribution P(f)', color=COLORS['text'], fontsize=12, pad=10)
    ax2.tick_params(colors=COLORS['text'])

    # 3. Autocorrelation / Periodicity (middle center)
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(COLORS['background'])

    if np.any(density):
        # Compute autocorrelation
        autocorr = np.correlate(density, density, mode='full')
        autocorr = autocorr[len(autocorr)//2:]  # Positive lags only
        autocorr = autocorr / autocorr[0] if autocorr[0] != 0 else autocorr  # Normalize

        lags = np.arange(len(autocorr))
        ax3.fill_between(lags, autocorr, alpha=0.5, color=COLORS['period'])
        ax3.plot(lags, autocorr, color=COLORS['period'], linewidth=2)

        # Mark dominant period
        if features['dominant_period'] > 0:
            dp = int(features['dominant_period'])
            ax3.axvline(x=dp, color=COLORS['text'], linestyle='--', alpha=0.7)
            ax3.text(dp + 0.3, 0.8, f'T={dp}', color=COLORS['text'], fontsize=10)

    ax3.set_xlim(0, len(density) - 1)
    ax3.set_xlabel('Lag (16th notes)', color=COLORS['text'])
    ax3.set_ylabel('Correlation', color=COLORS['text'])
    ax3.set_title('Autocorrelation (Periodicity)', color=COLORS['text'], fontsize=12, pad=10)
    ax3.tick_params(colors=COLORS['text'])

    # 4. Transformation Profile (middle right)
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.set_facecolor(COLORS['background'])

    # Count transforms by category
    categories = ['dynamics', 'space', 'time', 'filter', 'pitch', 'distortion']
    counts = [len(transforms.get(cat, [])) for cat in categories]

    y_pos = np.arange(len(categories))
    bars = ax4.barh(y_pos, counts, color=COLORS['transform'], alpha=0.7)

    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(categories, color=COLORS['text'])
    ax4.set_xlabel('Count', color=COLORS['text'])
    ax4.set_title('Transform Profile', color=COLORS['text'], fontsize=12, pad=10)
    ax4.tick_params(colors=COLORS['text'])

    # Add count labels
    for i, (count, bar) in enumerate(zip(counts, bars)):
        if count > 0:
            ax4.text(count + 0.1, bar.get_y() + bar.get_height()/2,
                    str(count), va='center', color=COLORS['text'], fontsize=10)

    # 5. Feature Summary (bottom left)
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.set_facecolor(COLORS['background'])
    ax5.axis('off')

    summary_text = f"""
    Density Mean:  {features['density_mean']:.2f}
    Density Std:   {features['density_std']:.2f}
    Sparseness:    {features['sparseness']:.0%}
    Unique Pitches: {features['unique_pitches']}
    """
    ax5.text(0.1, 0.5, summary_text, transform=ax5.transAxes,
             fontfamily='monospace', fontsize=11, color=COLORS['text'],
             verticalalignment='center')
    ax5.set_title('Rhythmic Features', color=COLORS['text'], fontsize=12, pad=10)

    # 6. Circular Rhythm Visualization (bottom center)
    ax6 = fig.add_subplot(gs[2, 1], projection='polar')
    ax6.set_facecolor(COLORS['background'])

    # Map density to polar coordinates
    theta = np.linspace(0, 2 * np.pi, len(density), endpoint=False)
    radii = density / (max(density) + 0.001)  # Normalize

    # Create bars around the circle
    width = 2 * np.pi / len(density)
    bars = ax6.bar(theta, radii, width=width, alpha=0.7, color=COLORS['density'])

    # Style polar plot
    ax6.set_ylim(0, 1.2)
    ax6.set_rticks([])
    ax6.set_xticks(np.linspace(0, 2 * np.pi, 4, endpoint=False))
    ax6.set_xticklabels(['1', '2', '3', '4'], color=COLORS['text'])
    ax6.set_title('Circular Rhythm', color=COLORS['text'], fontsize=12, pad=15)
    ax6.tick_params(colors=COLORS['text'])
    ax6.spines['polar'].set_color(COLORS['grid'])

    # 7. Pattern Stats (bottom right)
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.set_facecolor(COLORS['background'])
    ax7.axis('off')

    stats_text = f"""
    Transform Depth: {features['transform_depth']}
    Has Space FX:    {'Yes' if features['has_space'] else 'No'}
    Has Filters:     {'Yes' if features['has_filter'] else 'No'}
    Has Time Mod:    {'Yes' if features['has_time_mod'] else 'No'}
    Dom. Period:     {features['dominant_period']:.0f} steps
    """
    ax7.text(0.1, 0.5, stats_text, transform=ax7.transAxes,
             fontfamily='monospace', fontsize=11, color=COLORS['text'],
             verticalalignment='center')
    ax7.set_title('Processing Features', color=COLORS['text'], fontsize=12, pad=10)

    # Save if path provided
    if output_path:
        plt.savefig(output_path, dpi=150, facecolor=COLORS['background'],
                   edgecolor='none', bbox_inches='tight')
        print(f"Saved: {output_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def visualize_all_patterns(patterns_dir: str, output_dir: str = None):
    """Generate fingerprints for all patterns in a directory."""
    patterns_path = Path(patterns_dir)
    output_path = Path(output_dir) if output_dir else patterns_path / 'visualizations'
    output_path.mkdir(exist_ok=True)

    pattern_files = list(patterns_path.glob('**/*.json'))
    print(f"Found {len(pattern_files)} patterns")

    for pattern_file in pattern_files:
        try:
            with open(pattern_file, 'r', encoding='utf-8') as f:
                pattern_data = json.load(f)

            output_file = output_path / f"{pattern_data.get('name', pattern_file.stem)}_fingerprint.png"
            create_pattern_fingerprint(pattern_data, str(output_file), show=False)

        except Exception as e:
            print(f"Error processing {pattern_file}: {e}")

    print(f"\nVisualizations saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize Strudel pattern structure")
    parser.add_argument('pattern', nargs='?', help="Path to pattern JSON file")
    parser.add_argument('--all', metavar='DIR', help="Visualize all patterns in directory")
    parser.add_argument('--output', '-o', help="Output file or directory")
    parser.add_argument('--no-show', action='store_true', help="Don't display, only save")

    args = parser.parse_args()

    if args.all:
        visualize_all_patterns(args.all, args.output)
    elif args.pattern:
        with open(args.pattern, 'r', encoding='utf-8') as f:
            pattern_data = json.load(f)
        create_pattern_fingerprint(pattern_data, args.output, show=not args.no_show)
    else:
        # Demo with inline pattern
        demo_pattern = {
            "name": "organic-minimal",
            "genre": "folk-hiphop",
            "bpm": 88,
            "key": "Em",
            "pattern": '''setcpm(88)
stack(
  s("bd ~ ~ ~, ~ ~ cp ~, ~ hh ~ hh").swing(0.12).room(0.4).gain(0.7),
  note("e1 ~ ~ e1, ~ e1 ~ ~").s("sine").lpf(200).gain(0.65),
  note("e3 g3 b3").s("sawtooth").attack(1.5).release(3).lpf(2000).room(0.6).gain(0.25),
  note("b4 ~ e5 ~, ~ ~ g4 ~").s("triangle").delay(0.35).room(0.5).gain(0.2)
).gain(0.75)'''
        }
        create_pattern_fingerprint(demo_pattern, args.output, show=not args.no_show)


if __name__ == "__main__":
    main()
