"""
Rhiz Skill Router - Recognition & Retrieval Engine
Implements the first two layers of the skill system:
1. Recognition: Pattern matching to identify relevant skills
2. Retrieval: Loading skill representations and primitives

Design Philosophy:
- Skills activate through pattern recognition, not explicit calls
- Semantic similarity over keyword matching
- Confidence-based ranking
- Compiled expertise emerges from pattern recognition across sessions
"""

import yaml
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys

# Add memory scripts to path for embedding model
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "memory" / "scripts"))
from embeddings import EmbeddingGenerator

class SkillRouter:
    """
    Routes requests to appropriate skills based on semantic pattern matching.
    """

    def __init__(
        self,
        skills_registry_path: Optional[str] = None,
        primitives_path: Optional[str] = None,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize the skill router.

        Args:
            skills_registry_path: Path to skills registry directory
            primitives_path: Path to primitives directory
            confidence_threshold: Minimum confidence for skill activation (0-1)
        """
        # Set default paths relative to this file
        if skills_registry_path is None:
            skills_registry_path = Path(__file__).parent.parent / "registry"
        if primitives_path is None:
            primitives_path = Path(__file__).parent.parent / "primitives"

        self.skills_registry_path = Path(skills_registry_path)
        self.primitives_path = Path(primitives_path)
        self.confidence_threshold = confidence_threshold

        # Initialize embedding model for semantic matching
        print("Initializing skill router embedding model...")
        self.embedder = EmbeddingGenerator()

        # Load skills and primitives
        self.skills = {}
        self.primitives = {}
        self.skill_embeddings = {}

        self._load_skills()
        self._load_primitives()

        print(f"[OK] Skill router initialized: {len(self.skills)} skills, {len(self.primitives)} primitives")

    def _load_skills(self):
        """Load all skill definitions from registry and domain skills."""
        # Load from core registry
        skill_files = []

        if self.skills_registry_path.exists():
            skill_files.extend(list(self.skills_registry_path.glob("**/*.yaml")))

        # Also load from domain skills directories
        project_root = Path(__file__).parent.parent.parent.parent
        domains_path = project_root / "domains"

        if domains_path.exists():
            skill_files.extend(list(domains_path.glob("**/skills/**/*.yaml")))

        for skill_file in skill_files:
            # Skip template file
            if "template" in skill_file.stem:
                continue

            try:
                with open(skill_file, 'r') as f:
                    skill_data = yaml.safe_load(f)

                if not skill_data or 'skill' not in skill_data:
                    continue

                skill_name = skill_data['skill']['name']
                self.skills[skill_name] = skill_data

                # Pre-compute embeddings for trigger patterns
                if 'recognition' in skill_data and 'trigger_patterns' in skill_data['recognition']:
                    patterns = skill_data['recognition']['trigger_patterns']
                    pattern_texts = [p['pattern'] for p in patterns if isinstance(p, dict)]

                    if pattern_texts:
                        # Embed all patterns for this skill
                        embeddings = self.embedder.embed(pattern_texts)
                        self.skill_embeddings[skill_name] = {
                            'patterns': pattern_texts,
                            'embeddings': embeddings,
                            'confidences': [p.get('confidence', 0.8) for p in patterns]
                        }

            except Exception as e:
                print(f"Warning: Failed to load skill {skill_file}: {e}")

    def _load_primitives(self):
        """Load all primitive definitions."""
        if not self.primitives_path.exists():
            print(f"Warning: Primitives path not found at {self.primitives_path}")
            return

        primitive_files = list(self.primitives_path.glob("*.yaml"))

        for prim_file in primitive_files:
            try:
                with open(prim_file, 'r') as f:
                    prim_data = yaml.safe_load(f)

                if not prim_data or 'primitive' not in prim_data:
                    continue

                prim_name = prim_data['primitive']['name']
                self.primitives[prim_name] = prim_data

            except Exception as e:
                print(f"Warning: Failed to load primitive {prim_file}: {e}")

    def recognize(self, request: str, top_k: int = 3) -> List[Dict]:
        """
        Recognize which skills match the given request.

        Args:
            request: Natural language request or task description
            top_k: Number of top skills to return

        Returns:
            List of matched skills with confidence scores, sorted by confidence
        """
        if not self.skills:
            return []

        # Embed the request
        request_embedding = self.embedder.embed(request)

        matches = []

        for skill_name, skill_data in self.skill_embeddings.items():
            # Compute similarity with each trigger pattern
            for i, pattern_embedding in enumerate(skill_data['embeddings']):
                # Cosine similarity
                similarity = self._cosine_similarity(request_embedding, pattern_embedding)

                # Adjust by pattern confidence
                adjusted_confidence = similarity * skill_data['confidences'][i]

                if adjusted_confidence >= self.confidence_threshold:
                    matches.append({
                        'skill_name': skill_name,
                        'skill_data': self.skills[skill_name],
                        'confidence': adjusted_confidence,
                        'matched_pattern': skill_data['patterns'][i],
                        'pattern_similarity': similarity
                    })

        # Sort by confidence and return top_k
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches[:top_k]

    def retrieve(self, skill_name: str) -> Optional[Dict]:
        """
        Retrieve a skill definition by name.

        Args:
            skill_name: Name of the skill to retrieve

        Returns:
            Skill definition dict or None if not found
        """
        skill_data = self.skills.get(skill_name)

        if not skill_data:
            return None

        # Enrich with primitive definitions
        if 'composition' in skill_data and 'primitives' in skill_data['composition']:
            enriched_primitives = []

            for prim_ref in skill_data['composition']['primitives']:
                prim_name = prim_ref.get('name')
                if prim_name in self.primitives:
                    enriched_primitives.append({
                        'reference': prim_ref,
                        'definition': self.primitives[prim_name]
                    })
                else:
                    enriched_primitives.append({
                        'reference': prim_ref,
                        'definition': None,
                        'error': 'Primitive not found'
                    })

            skill_data['enriched_primitives'] = enriched_primitives

        return skill_data

    def match(self, request: str) -> Optional[Dict]:
        """
        Convenience method: recognize and retrieve best matching skill.

        Args:
            request: Natural language request

        Returns:
            Best matching skill with full definition, or None
        """
        matches = self.recognize(request, top_k=1)

        if not matches:
            return None

        best_match = matches[0]
        skill_name = best_match['skill_name']

        # Retrieve full definition with primitives
        skill_data = self.retrieve(skill_name)

        return {
            'match': best_match,
            'skill': skill_data
        }

    @staticmethod
    def _cosine_similarity(vec1, vec2):
        """Compute cosine similarity between two vectors."""
        import numpy as np
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        return dot_product / (norm_a * norm_b)

    def list_skills(self) -> List[str]:
        """Return list of all available skill names."""
        return list(self.skills.keys())

    def list_primitives(self) -> List[str]:
        """Return list of all available primitive names."""
        return list(self.primitives.keys())

    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """
        Get basic info about a skill without full retrieval.

        Returns:
            Dict with name, description, domain, tags
        """
        skill = self.skills.get(skill_name)
        if not skill or 'skill' not in skill:
            return None

        skill_def = skill['skill']

        return {
            'name': skill_def.get('name'),
            'version': skill_def.get('version'),
            'domain': skill_def.get('domain'),
            'description': skill_def.get('description'),
            'tags': skill_def.get('taxonomy', {}).get('tags', [])
        }


def create_router(confidence_threshold: float = 0.6) -> SkillRouter:
    """Convenience function to create a router with default paths."""
    return SkillRouter(confidence_threshold=confidence_threshold)


if __name__ == "__main__":
    # Test the skill router
    print("=" * 60)
    print("RHIZ SKILL ROUTER TEST")
    print("=" * 60)

    router = create_router()

    print(f"\nAvailable skills: {router.list_skills()}")
    print(f"Available primitives: {router.list_primitives()}")

    # Test recognition
    test_requests = [
        "Check if exchange is connected",
        "What's the current BTC price?",
        "Analyze my portfolio performance"
    ]

    for request in test_requests:
        print(f"\n--- Testing: '{request}' ---")
        matches = router.recognize(request, top_k=2)

        if matches:
            for i, match in enumerate(matches, 1):
                print(f"{i}. {match['skill_name']} (confidence: {match['confidence']:.3f})")
                print(f"   Matched: '{match['matched_pattern']}'")
        else:
            print("  No skills matched")

    print("\n" + "=" * 60)
