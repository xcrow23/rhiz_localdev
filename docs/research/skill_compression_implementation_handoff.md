# Appendix: Implementation Handoff for Claude Code (Sonnet 4.5)

## The Bootstrap Problem: Birth Without Memory

When a Claude Code session initializes, the instance arrives *tabula rasa*—no accumulated context, no memory of past corrections, no learned preferences. Yet this fresh instance must somehow:

1. **Recognize what it doesn't know** (epistemic humility)
2. **Trigger appropriate retrieval** without being told what to retrieve
3. **Detect misalignment** between action and outcome
4. **Consolidate corrections** for future instances

This is the first step toward agency: not autonomous action, but **autonomous correction**. A system that can recognize and repair its own errors has crossed a threshold from tool to collaborator.

## The Self-Correcting Dyad Pattern

The daemon-nous architecture provides the conceptual frame. The **daemon** (persistent infrastructure) maintains continuity across sessions; the **nous** (active intelligence) operates within sessions but lacks persistence. Self-correction emerges from their coupling:

```
┌─────────────────────────────────────────────────────────────────┐
│                     SESSION LIFECYCLE                            │
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │  BIRTH   │───▶│  OPERATION   │───▶│   DEATH      │           │
│  │          │    │              │    │              │           │
│  │ Hook:    │    │ Correction   │    │ Hook:        │           │
│  │ Inject   │    │ Loop Active  │    │ Extract &    │           │
│  │ Context  │    │              │    │ Consolidate  │           │
│  └──────────┘    └──────────────┘    └──────────────┘           │
│       ▲                                     │                    │
│       │                                     │                    │
│       │         ┌──────────────┐            │                    │
│       └─────────│   DAEMON     │◀───────────┘                    │
│                 │ (Persistent) │                                 │
│                 │              │                                 │
│                 │ - Qdrant     │                                 │
│                 │ - Checkpoints│                                 │
│                 │ - Corrections│                                 │
│                 └──────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Session Hook Architecture for Sparse Activation

Your existing hooks (`session_start.py`, `session_end.py`) provide the integration points. The enhancement: **semantic-triggered sparse loading** rather than static context injection.


### session_start.py Enhancement

```python
# core/hooks/session_start.py

from semantic_router import SemanticRouter
from semantic_router.index import QdrantIndex
from qdrant_client import QdrantClient
import yaml

class SessionInitializer:
    """
    Sparse activation at session birth.
    
    Instead of loading full context, we:
    1. Embed the initial user message
    2. Retrieve only relevant skill contexts
    3. Load correction history for activated domains
    4. Inject minimal but sufficient context
    """
    
    def __init__(self, qdrant_url="http://localhost:6333"):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.router = self._init_router()
        
    def _init_router(self):
        """Initialize semantic router with skill fingerprints."""
        index = QdrantIndex(
            client=self.qdrant,
            collection_name="skill_fingerprints"
        )
        return SemanticRouter(index=index)
    
    def activate_for_query(self, initial_query: str) -> dict:
        """
        Sparse activation based on initial query.
        Returns minimal context package for CLAUDE.md injection.
        """
        # Route to relevant skill domains
        route_result = self.router(initial_query)
        activated_skills = route_result.name if route_result else ["general"]
        
        # Retrieve correction history for activated domains
        corrections = self._get_domain_corrections(activated_skills)
        
        # Retrieve recent session context (last 3 sessions in domain)
        session_context = self._get_recent_sessions(activated_skills, limit=3)
        
        # Retrieve active learnings (things we've discovered work/don't work)
        learnings = self._get_active_learnings(activated_skills)
        
        return {
            "activated_skills": activated_skills,
            "corrections": corrections,
            "session_context": session_context,
            "learnings": learnings,
            "confidence": route_result.score if route_result else 0.0
        }
    
    def _get_domain_corrections(self, skills: list) -> list:
        """
        Retrieve correction patterns for activated skill domains.
        These are mistakes we've made before and their fixes.
        """
        corrections = []
        for skill in skills:
            results = self.qdrant.search(
                collection_name="corrections",
                query_filter={"skill_domain": skill},
                limit=5
            )
            corrections.extend([r.payload for r in results])
        return corrections
    
    def _get_active_learnings(self, skills: list) -> list:
        """
        Retrieve validated learnings - things confirmed to work.
        Different from corrections: these are positive patterns.
        """
        learnings = []
        for skill in skills:
            results = self.qdrant.search(
                collection_name="learnings",
                query_filter={
                    "skill_domain": skill,
                    "validated": True
                },
                limit=5
            )
            learnings.extend([r.payload for r in results])
        return learnings

def generate_claude_md_injection(activation_context: dict) -> str:
    """
    Generate the sparse context injection for CLAUDE.md.
    
    This is what the fresh instance sees at birth - 
    not everything, but enough to avoid known mistakes
    and leverage confirmed learnings.
    """
    sections = []
    
    # Active skill domains
    sections.append(f"""## Activated Skill Domains
Based on your query, these domains are relevant: {', '.join(activation_context['activated_skills'])}
Confidence: {activation_context['confidence']:.2f}
""")
    
    # Correction patterns (mistakes to avoid)
    if activation_context['corrections']:
        sections.append("## Known Pitfalls (Corrections from Past Sessions)")
        for c in activation_context['corrections'][:3]:  # Top 3 most relevant
            sections.append(f"""
**Pattern**: {c['error_pattern']}
**Correction**: {c['correction']}
**Context**: {c['context']}
""")
    
    # Validated learnings (things that work)
    if activation_context['learnings']:
        sections.append("## Validated Approaches")
        for l in activation_context['learnings'][:3]:
            sections.append(f"""
**Approach**: {l['approach']}
**Why it works**: {l['reasoning']}
**When to use**: {l['trigger_conditions']}
""")
    
    # Session continuity hints
    if activation_context['session_context']:
        sections.append("## Recent Session Context")
        for s in activation_context['session_context']:
            sections.append(f"- {s['summary']} ({s['timestamp']})")
    
    return "\n".join(sections)
```


### The Correction Loop: How the Instance Learns Mid-Session

Self-correction requires **detecting misalignment**. For Claude Code, this means recognizing when:

1. Tool execution fails or returns unexpected results
2. User provides correction or clarification  
3. Verification checks don't pass
4. The model's own confidence drops below threshold

```python
# core/hooks/correction_loop.py

class CorrectionDetector:
    """
    Monitors for correction signals during session.
    
    The key insight: we don't need perfect detection,
    we need reliable detection of HIGH-CONFIDENCE corrections.
    Better to miss some corrections than to record false ones.
    """
    
    CORRECTION_SIGNALS = [
        # Explicit user corrections
        r"no,?\s+(actually|instead|I meant)",
        r"that's (not|wrong|incorrect)",
        r"I (said|meant|wanted)",
        
        # Tool failure patterns
        r"error:|exception:|failed:",
        r"command not found",
        r"permission denied",
        
        # Self-detected issues
        r"I (notice|see|realize) (that |I )?(made|there's) (a |an )?(mistake|error)",
        r"let me (correct|fix|revise)",
    ]
    
    def __init__(self):
        self.correction_buffer = []
        self.context_window = []  # Last N exchanges
        
    def process_exchange(self, user_msg: str, assistant_msg: str, 
                         tool_results: list = None):
        """
        Process each exchange looking for correction signals.
        """
        # Update context window
        self.context_window.append({
            "user": user_msg,
            "assistant": assistant_msg,
            "tools": tool_results
        })
        if len(self.context_window) > 10:
            self.context_window.pop(0)
        
        # Check for correction signals
        correction = self._detect_correction(user_msg, assistant_msg, tool_results)
        if correction:
            self.correction_buffer.append(correction)
            return correction
        return None
    
    def _detect_correction(self, user_msg, assistant_msg, tool_results):
        """
        Detect if this exchange contains a correction.
        Returns structured correction if detected, None otherwise.
        """
        import re
        
        # Check user message for correction patterns
        for pattern in self.CORRECTION_SIGNALS:
            if re.search(pattern, user_msg, re.IGNORECASE):
                return self._extract_correction(
                    trigger="user_correction",
                    context=self.context_window[-3:],
                    current_exchange={"user": user_msg, "assistant": assistant_msg}
                )
        
        # Check tool results for failures
        if tool_results:
            for result in tool_results:
                if result.get("error") or result.get("returncode", 0) != 0:
                    return self._extract_correction(
                        trigger="tool_failure",
                        context=self.context_window[-3:],
                        tool_result=result
                    )
        
        # Check assistant message for self-correction
        for pattern in self.CORRECTION_SIGNALS[-2:]:
            if re.search(pattern, assistant_msg, re.IGNORECASE):
                return self._extract_correction(
                    trigger="self_correction",
                    context=self.context_window[-3:],
                    current_exchange={"user": user_msg, "assistant": assistant_msg}
                )
        
        return None
    
    def _extract_correction(self, trigger: str, context: list, **kwargs) -> dict:
        """
        Structure the correction for storage.
        """
        from datetime import datetime
        return {
            "trigger": trigger,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "details": kwargs,
            "needs_consolidation": True
        }
```
