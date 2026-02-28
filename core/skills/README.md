# Rhiz Skills Registry

## Overview

Skills are compiled expertise patterns that enable fast activation without context payload. This directory contains skill definitions that capture:

- **Recognition patterns** - When to activate the skill
- **Core knowledge** - Domain-specific facts and heuristics
- **Execution primitives** - Code patterns and tool invocations
- **Decision heuristics** - How to choose between approaches
- **Common patterns** - Recurring usage examples
- **Failure modes** - Known gotchas and recovery strategies

## Philosophy

Skills implement the **compiled expertise** principle from Skill Compression Research:

1. **Recognition**: Fast pattern matching to identify skill relevance
2. **Retrieval**: Load skill representation based on triggers
3. **Composition**: Combine primitives into executable sequences
4. **Execution**: Run with dynamic adaptation

The goal is **pattern recognition, not context payload**. A well-defined skill should activate from keywords and context patterns, not require reading full documentation.

## Skill Format

Skills use YAML format with structured sections:

```yaml
skill:
  name: "skill_name"
  version: "1.0.0"
  domain: "category"

  triggers:
    keywords: [...]
    context_patterns: [...]
    user_questions: [...]

  knowledge:
    # Domain-specific facts

  primitives:
    - name: "primitive_name"
      code_pattern: |
        # Executable code template

  decision_tree:
    - condition: "when to use"
      action: "what to do"

  usage_patterns:
    # Common recurring patterns

  gotchas:
    # Known failure modes
```

## Available Skills

### memory_search (v1.0.0)
**Domain:** infrastructure
**Purpose:** Hybrid semantic + keyword search expertise for Rhiz memory system

**Key Capabilities:**
- Pure semantic search (vector similarity)
- Hybrid search (semantic + keyword filtering)
- Domain/pattern/keyword filtering
- Score threshold tuning (all-MiniLM-L6-v2)

**MCP Integration:**
- `checkpoint_search` - Pure semantic search
- `hybrid_search_checkpoints` - Hybrid search with filters
- `memory_context` - Auto-context retrieval

**Documentation:** `docs/architecture/memory_hybrid_search.md`

**Activation Triggers:**
- Keywords: "search memories", "find checkpoints", "previous sessions"
- Questions: "When did we work on [domain]?", "Show sessions about [topic]"
- Context: Need to recall previous work or find related sessions

**Common Patterns:**
```yaml
# Find sessions by domain
hybrid_search(query="deployment", domains=["infrastructure"])

# Multi-filter precision
hybrid_search(
  query="architecture",
  domains=["trading"],
  decision_types=["architectural"],
  is_notable=True
)
```

## Skill Development Workflow

### Creating New Skills

1. **Identify Expertise Domain**
   - What area of Rhiz does this expertise cover?
   - Is it infrastructure, trading, patterns, or research?

2. **Extract from Session Work**
   - Skill definitions should emerge from real sessions
   - Look for recurring patterns and decision heuristics
   - Document failure modes encountered

3. **Define Recognition Patterns**
   - What keywords trigger this skill?
   - What questions does it answer?
   - What context patterns indicate relevance?

4. **Encode Primitives**
   - Extract code patterns as templates
   - Identify composition patterns
   - Document tool/MCP integrations

5. **Test Activation**
   - Does skill trigger on relevant queries?
   - Are primitives executable as-is?
   - Do decision heuristics guide correctly?

### Updating Existing Skills

1. **Version Increment**
   - Patch (x.x.1): Bug fixes, clarifications
   - Minor (x.1.0): New primitives, patterns
   - Major (1.0.0): Breaking changes, new recognition logic

2. **Changelog**
   - Document what changed and why
   - Reference session where changes emerged

3. **Backward Compatibility**
   - Preserve existing primitives
   - Add new patterns, don't replace
   - Mark deprecated approaches

## MCP Integration

Skills should integrate with MCP servers for executable primitives:

```yaml
primitives:
  - name: "mcp_tool_call"
    mcp_call: "tool_name"
    code_pattern: |
      result = mcp_client.call_tool(
          "tool_name",
          param1="value1"
      )
```

**MCP Server Tool Descriptions:**
- Reference skill in tool description
- Include skill-based usage hints
- Cross-link to skill documentation

Example:
```python
Tool(
    name="hybrid_search_checkpoints",
    description="... See skill: memory_search for usage patterns.",
    ...
)
```

## Cross-System Upskilling

Skills enable knowledge propagation across:

1. **Session-to-Session** - Load skill at session start
2. **Human-to-AI** - Captain references skills in requests
3. **AI-to-AI** - Future model training on skill patterns
4. **MCP-to-Skill** - MCP tools reference skills
5. **Skill-to-Skill** - Skills compose via `combines_with`

**Example Flow:**
```
Session work → Skill definition → MCP tool description →
Auto-activation in future sessions → Refined in practice →
Skill update → Training data for future models
```

## Skill Composition

Skills can reference other skills via `combines_with`:

```yaml
combines_with:
  - skill: "checkpoint_writing"
    synergy: "Write checkpoints with frontmatter for better retrieval"

  - skill: "session_handshake"
    synergy: "Use memory_context for session startup"
```

This creates a **skill graph** enabling higher-order patterns.

## Future: Skill Compression

From Skill Compression Research, future skill system will:

1. **Semantic Skill Routing** - Embed skill descriptions, retrieve by similarity
2. **Dynamic Weight Adaptation** - Skills tune based on usage success
3. **Hierarchical Composition** - Complex skills from primitive combinations
4. **Auto-Skill Discovery** - Extract skills from session patterns automatically

## Contributing

When creating skills from session work:

1. Create skill YAML in `core/skills/registry/[skill_name].yaml`
2. Update this README with skill summary
3. Reference skill in relevant MCP tool descriptions
4. Add skill to checkpoint frontmatter `skills_executed` if used
5. Document in session checkpoint for future reference

---

**Last Updated:** 2026-01-31
**Skills Count:** 6
**Status:** Hibernation (observation mode)
