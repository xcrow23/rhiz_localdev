"""
Mathematical Pattern Analysis for Strudel Patterns
Extracts mathematical features from pattern code for vectorization.

This is a proof-of-concept exploring machine-native music representations.
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import Counter


class PatternMath:
    """
    Extract mathematical features from Strudel pattern code.

    Features:
    - Density series (events over time)
    - Pitch statistics (if melodic content)
    - Transformation profile
    - Periodicity analysis
    """

    # Common sample names (percussion)
    PERCUSSION = {'bd', 'cp', 'sn', 'hh', 'oh', 'ch', 'rim', 'clap', 'tom', 'shaker'}

    # Transformation categories
    TRANSFORM_CATEGORIES = {
        'dynamics': ['gain', 'velocity', 'accent'],
        'space': ['room', 'delay', 'pan', 'reverb'],
        'time': ['fast', 'slow', 'every', 'sometimes', 'rarely', 'struct'],
        'pitch': ['transpose', 'add', 'note'],
        'filter': ['lpf', 'hpf', 'cutoff', 'resonance'],
        'distortion': ['crush', 'shape', 'drive']
    }

    def __init__(self):
        self.note_to_midi = self._build_note_map()

    def _build_note_map(self) -> Dict[str, int]:
        """Build note name to MIDI number mapping."""
        notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
        note_map = {}
        for octave in range(0, 9):
            for i, note in enumerate(notes):
                midi = 12 + (octave * 12) + i
                note_map[f"{note}{octave}"] = midi
                # Also handle flats
                if '#' not in note and i > 0:
                    flat = notes[i-1].replace('#', '') + 'b'
                    note_map[f"{flat}{octave}"] = midi - 1
        return note_map

    def extract_density(self, pattern_code: str, resolution: int = 16) -> np.array:
        """
        Extract rhythmic density series from pattern.

        Analyzes sample patterns like s("bd ~ cp ~") to determine
        events per time slice.

        Args:
            pattern_code: Strudel pattern code
            resolution: Number of time slices per cycle

        Returns:
            numpy array of event counts per slice
        """
        density = np.zeros(resolution)

        # Find sample patterns: s("...")
        sample_patterns = re.findall(r's\(["\']([^"\']+)["\']\)', pattern_code)

        for pattern in sample_patterns:
            # Parse the mini-notation
            density += self._parse_mini_notation(pattern, resolution)

        return density

    def _parse_mini_notation(self, notation: str, resolution: int) -> np.array:
        """
        Parse Strudel mini-notation into density array.

        Handles:
        - "bd ~ cp ~" -> events at positions 0, 2
        - "hh*4" -> 4 events spread across cycle
        - "bd [cp cp]" -> nested patterns
        """
        density = np.zeros(resolution)

        # Split by comma (parallel patterns)
        parallel = notation.split(',')

        for part in parallel:
            part = part.strip()
            if not part:
                continue

            # Handle multiplication: hh*4
            mult_match = re.match(r'(\w+)\*(\d+)', part)
            if mult_match:
                count = int(mult_match.group(2))
                positions = np.linspace(0, resolution - 1, count, dtype=int)
                for pos in positions:
                    density[pos] += 1
                continue

            # Handle space-separated (sequential)
            tokens = part.split()
            if len(tokens) > 0:
                step = resolution // len(tokens)
                for i, token in enumerate(tokens):
                    if token != '~':  # ~ is rest
                        # Handle brackets [x x] as subdivisions
                        if '[' in token:
                            sub_count = token.count(' ') + 1 - token.count('~')
                            density[i * step] += sub_count
                        else:
                            density[i * step] += 1

        return density

    def extract_pitches(self, pattern_code: str) -> List[int]:
        """
        Extract MIDI pitch values from note patterns.

        Args:
            pattern_code: Strudel pattern code

        Returns:
            List of MIDI pitch values
        """
        pitches = []

        # Find note patterns: note("...")
        note_patterns = re.findall(r'note\(["\']([^"\']+)["\']\)', pattern_code)

        for pattern in note_patterns:
            # Extract individual notes
            notes = re.findall(r'([a-g]#?b?\d)', pattern.lower())
            for note in notes:
                if note in self.note_to_midi:
                    pitches.append(self.note_to_midi[note])

        return pitches

    def extract_transforms(self, pattern_code: str) -> Dict[str, List[str]]:
        """
        Extract transformation chain from pattern.

        Returns dict of {category: [transforms]}
        """
        transforms = {cat: [] for cat in self.TRANSFORM_CATEGORIES}

        # Find all method calls: .method(...)
        method_calls = re.findall(r'\.(\w+)\([^)]*\)', pattern_code)

        for method in method_calls:
            for category, methods in self.TRANSFORM_CATEGORIES.items():
                if method.lower() in methods:
                    transforms[category].append(method)

        return transforms

    def compute_features(self, pattern_code: str) -> Dict[str, float]:
        """
        Compute full mathematical feature set from pattern.

        Returns:
            Dictionary of named features
        """
        features = {}

        # Density features
        density = self.extract_density(pattern_code)
        features['density_mean'] = float(np.mean(density))
        features['density_std'] = float(np.std(density))
        features['density_max'] = float(np.max(density))
        features['sparseness'] = float(np.sum(density == 0) / len(density))

        # Pitch features
        pitches = self.extract_pitches(pattern_code)
        if pitches:
            features['pitch_mean'] = float(np.mean(pitches))
            features['pitch_std'] = float(np.std(pitches))
            features['pitch_range'] = float(max(pitches) - min(pitches))
            features['unique_pitches'] = len(set(pitches))
        else:
            features['pitch_mean'] = 0.0
            features['pitch_std'] = 0.0
            features['pitch_range'] = 0.0
            features['unique_pitches'] = 0

        # Transformation features
        transforms = self.extract_transforms(pattern_code)
        features['transform_depth'] = sum(len(v) for v in transforms.values())
        features['has_space'] = 1.0 if transforms['space'] else 0.0
        features['has_time_mod'] = 1.0 if transforms['time'] else 0.0
        features['has_filter'] = 1.0 if transforms['filter'] else 0.0

        # Periodicity via autocorrelation
        if np.any(density):
            autocorr = np.correlate(density, density, mode='full')
            autocorr = autocorr[len(autocorr)//2:]  # positive lags only
            # Find peaks (excluding lag 0)
            if len(autocorr) > 1:
                peaks = np.where(np.diff(np.sign(np.diff(autocorr))) < 0)[0] + 1
                if len(peaks) > 0:
                    features['dominant_period'] = float(peaks[0])
                else:
                    features['dominant_period'] = 0.0
            else:
                features['dominant_period'] = 0.0
        else:
            features['dominant_period'] = 0.0

        return features

    def to_vector(self, pattern_code: str) -> np.array:
        """
        Convert pattern to fixed-size feature vector.

        Returns:
            numpy array of ~16 features
        """
        features = self.compute_features(pattern_code)

        # Fixed order for consistent vectorization
        feature_order = [
            'density_mean', 'density_std', 'density_max', 'sparseness',
            'pitch_mean', 'pitch_std', 'pitch_range', 'unique_pitches',
            'transform_depth', 'has_space', 'has_time_mod', 'has_filter',
            'dominant_period'
        ]

        return np.array([features.get(f, 0.0) for f in feature_order])


def analyze_pattern(pattern_code: str) -> Dict:
    """
    Convenience function to analyze a pattern.

    Args:
        pattern_code: Strudel pattern code

    Returns:
        Dictionary with features and analysis
    """
    analyzer = PatternMath()
    features = analyzer.compute_features(pattern_code)
    vector = analyzer.to_vector(pattern_code)

    return {
        'features': features,
        'vector': vector.tolist(),
        'density_series': analyzer.extract_density(pattern_code).tolist(),
        'pitches': analyzer.extract_pitches(pattern_code),
        'transforms': analyzer.extract_transforms(pattern_code)
    }


if __name__ == "__main__":
    # Test with folk-hiphop pattern
    test_pattern = '''
    setcpm(88)
    stack(
      s("bd ~ ~ ~, ~ ~ cp ~, ~ hh ~ hh").swing(0.12).room(0.4).gain(0.7),
      note("e1 ~ ~ e1, ~ e1 ~ ~").s("sine").lpf(200).gain(0.65),
      note("e3 g3 b3").s("sawtooth").attack(1.5).release(3).lpf(2000).room(0.6).gain(0.25),
      note("b4 ~ e5 ~, ~ ~ g4 ~").s("triangle").delay(0.35).room(0.5).gain(0.2)
    ).gain(0.75)
    '''

    print("=" * 60)
    print("MATHEMATICAL PATTERN ANALYSIS")
    print("=" * 60)
    print(f"\nPattern (folk-hiphop organic-minimal):\n{test_pattern[:100]}...")

    result = analyze_pattern(test_pattern)

    print("\n--- Features ---")
    for name, value in result['features'].items():
        print(f"  {name}: {value:.3f}" if isinstance(value, float) else f"  {name}: {value}")

    print("\n--- Density Series (16 slices) ---")
    print(f"  {result['density_series']}")

    print("\n--- Pitches (MIDI) ---")
    print(f"  {result['pitches']}")

    print("\n--- Transforms ---")
    for cat, transforms in result['transforms'].items():
        if transforms:
            print(f"  {cat}: {transforms}")

    print("\n--- Feature Vector (13 dims) ---")
    print(f"  {result['vector']}")

    print("\nAnalysis complete!")
