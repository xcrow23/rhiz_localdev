# Mathematical Pattern Vectorization: Series Analysis for Music Patterns

## The Insight

Music patterns are mathematical series. A pattern like:
```javascript
s("bd ~ cp ~, hh*8").fast(2).every(4, x => x.rev)
```

...encodes:
- **Event sequence**: discrete events over time
- **Density function**: notes per time unit
- **Transformation chain**: operations that modify the series
- **Periodicity**: how the pattern cycles and evolves

Rather than embedding human-readable descriptions, we can vectorize the *mathematical structure itself*.

## Mathematical Representations

### 1. Density Series d(t)

Parse pattern into time slices, count events:

```
Pattern: s("bd ~ cp ~")
Time:     0   1   2   3   (in beats)
Events:   1   0   1   0
d(t) =    [1, 0, 1, 0]
```

**Properties extractable**:
- Mean density: avg(d(t))
- Variance: spread of activity
- Sparseness: ratio of silence to sound
- Pulse pattern: dominant periodicities via FFT

### 2. Pitch Distribution P(f)

For melodic content, build frequency histogram:

```
Pattern: note("c2 e3 g4 e3")
Pitches: [C2, E3, G4, E3] = [36, 52, 67, 52] (MIDI)
P(f) = histogram over pitch range
```

**Properties extractable**:
- Centroid: "center of mass" of pitch
- Spread: how wide the pitch range
- Entropy: how uniform vs. concentrated
- Mode: most frequent pitch class

### 3. Transformation Graph G(V, E)

Parse transformation chain as directed graph:

```
Pattern: s("bd*4").gain(0.8).room(0.3).every(4, rev)

Graph:
  sample("bd*4")
      → gain(0.8)
      → room(0.3)
      → every(4, rev)

Adjacency encoding: [sample, gain, room, temporal_mod]
```

**Properties extractable**:
- Transformation depth: length of chain
- Effect types: which categories used (dynamics, space, time)
- Complexity: branching in stack() operations

### 4. Periodicity Analysis

Autocorrelation of density series reveals rhythmic structure:

```python
import numpy as np

def extract_periodicity(density_series):
    """Find dominant periodicities via autocorrelation."""
    autocorr = np.correlate(density_series, density_series, mode='full')
    # Find peaks = rhythmic periods
    return dominant_periods
```

### 5. Symbolic Structure Tree

Parse Strudel pattern as AST:

```
stack(
  s("bd*4"),           → Layer 1: percussion, density=4
  note("c2").s("sine") → Layer 2: bass, single note
)

Tree encoding:
{
  "root": "stack",
  "children": [
    {"type": "sample", "density": 4, "transforms": []},
    {"type": "note", "density": 1, "transforms": ["synth"]}
  ]
}
```

## Combined Feature Vector

Concatenate mathematical features into unified vector:

```python
def extract_pattern_features(pattern_code: str) -> np.array:
    """Extract mathematical features from pattern."""

    # Parse pattern
    parsed = parse_strudel(pattern_code)

    features = []

    # Rhythmic features (16 dims)
    density = extract_density_series(parsed, resolution=16)
    features.extend([
        np.mean(density),           # mean density
        np.std(density),            # density variance
        np.sum(density == 0) / 16,  # sparseness ratio
        *np.fft.fft(density)[:4].real  # dominant frequencies
    ])

    # Pitch features (8 dims) - if melodic content
    pitches = extract_pitches(parsed)
    if pitches:
        features.extend([
            np.mean(pitches),       # pitch centroid
            np.std(pitches),        # pitch spread
            entropy(pitch_histogram(pitches)),  # pitch entropy
            len(set(pitches)),      # unique pitches
        ])
    else:
        features.extend([0, 0, 0, 0])

    # Transformation features (8 dims)
    transforms = extract_transforms(parsed)
    features.extend([
        len(transforms),            # chain depth
        has_reverb(transforms),     # space effects
        has_delay(transforms),
        has_temporal_mod(transforms),  # every, sometimes, rarely
        has_pitch_mod(transforms),  # transpose, add
        complexity_score(parsed),   # stack depth, etc.
    ])

    # Periodicity features (4 dims)
    autocorr = autocorrelate(density)
    features.extend(top_k_periods(autocorr, k=4))

    return np.array(features)  # ~36 dimensional feature vector
```

## Visualization with Matplotlib

Programmatic visualization of pattern structure:

```python
import matplotlib.pyplot as plt
import numpy as np

def visualize_pattern_structure(pattern_code: str):
    """Generate visual representation of pattern mathematics."""

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # 1. Density over time
    ax1 = axes[0, 0]
    density = extract_density_series(pattern_code)
    ax1.bar(range(len(density)), density, color='steelblue')
    ax1.set_title('Rhythmic Density d(t)')
    ax1.set_xlabel('Time (beats)')
    ax1.set_ylabel('Event count')

    # 2. Pitch distribution
    ax2 = axes[0, 1]
    pitches = extract_pitches(pattern_code)
    ax2.hist(pitches, bins=24, color='coral', edgecolor='black')
    ax2.set_title('Pitch Distribution P(f)')
    ax2.set_xlabel('MIDI pitch')
    ax2.set_ylabel('Frequency')

    # 3. Autocorrelation (periodicity)
    ax3 = axes[1, 0]
    autocorr = np.correlate(density, density, mode='full')
    lags = range(-len(density)+1, len(density))
    ax3.plot(lags, autocorr, color='green')
    ax3.set_title('Autocorrelation (Periodicity)')
    ax3.set_xlabel('Lag')
    ax3.set_ylabel('Correlation')

    # 4. Transformation chain
    ax4 = axes[1, 1]
    transforms = extract_transforms(pattern_code)
    categories = categorize_transforms(transforms)
    ax4.barh(list(categories.keys()), list(categories.values()))
    ax4.set_title('Transformation Profile')
    ax4.set_xlabel('Count')

    plt.tight_layout()
    return fig

def export_pattern_svg(pattern_code: str, output_path: str):
    """Export pattern visualization as SVG for embedding."""
    fig = visualize_pattern_structure(pattern_code)
    fig.savefig(output_path, format='svg')
    plt.close(fig)
```

## Hybrid Vectorization Strategy

Combine semantic + mathematical vectors:

```python
def hybrid_embed_pattern(pattern: dict) -> np.array:
    """Create hybrid embedding: semantic + mathematical."""

    # Semantic embedding (384 dims from sentence transformer)
    semantic_text = build_embed_text(pattern)
    semantic_vec = embedder.embed(semantic_text)

    # Mathematical embedding (~36 dims from feature extraction)
    math_vec = extract_pattern_features(pattern['pattern'])

    # Normalize mathematical features
    math_vec = (math_vec - math_vec.mean()) / (math_vec.std() + 1e-8)

    # Concatenate: 384 + 36 = 420 dimensional hybrid vector
    hybrid = np.concatenate([semantic_vec, math_vec])

    return hybrid
```

## Search Implications

Mathematical features enable new query types:

```python
# "Find patterns with similar rhythmic density"
query_density = extract_density_series(source_pattern)
results = search_by_density_similarity(query_density)

# "Find sparse patterns (lots of silence)"
results = filter_patterns(lambda p: p.sparseness > 0.6)

# "Find patterns with similar transformation complexity"
results = filter_patterns(lambda p: p.transform_depth == 3)

# "Patterns with dominant 4-beat periodicity"
results = filter_patterns(lambda p: 4 in p.dominant_periods)
```

## Implementation Path

### Phase 1: Pattern Parser
Build a Strudel pattern parser that extracts:
- Event sequences with timing
- Note values with MIDI pitches
- Transformation chains

### Phase 2: Feature Extraction
Implement mathematical feature extractors:
- Density series
- Pitch statistics
- Periodicity analysis
- Transformation categorization

### Phase 3: Visualization Pipeline
Create matplotlib-based visualization:
- Generate SVG/PNG for each pattern
- Store visualization alongside pattern data
- Enable visual pattern browsing

### Phase 4: Hybrid Embedding Integration
- Extend Qdrant schema for hybrid vectors
- Implement weighted similarity search
- Enable queries like "mathematically similar to X but semantically like Y"

## Connection to Machine Cognition

This approach moves beyond human-centric embeddings (text descriptions) toward **distinctly machine** representations:

- Humans hear music as gestalt experience
- Machines can perceive music as mathematical series
- The mathematical representation captures structure invisible to human perception
- Similarity becomes computable: two patterns are close if their series transform similarly

This is what machine cognition might naturally develop when analyzing music - not metaphors about "warmth" or "energy" but precise mathematical characterizations of density, periodicity, and transformation.

---

*Research note: December 24, 2025*
*Exploring machine-native representations for music patterns*
*Part of Rhiz human-AI symbiotic development*
