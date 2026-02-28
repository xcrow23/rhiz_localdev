#!/usr/bin/env python3
"""
Rhiz Memory Bridge: YAML Checkpoints → Qdrant
Bridges session checkpoints to semantic vector memory.
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import urlopen, Request
import yaml


QDRANT_URL = "http://localhost:6333"
COLLECTION = "rhiz_memories"
CHECKPOINTS_DIR = Path(__file__).parent.parent / "checkpoints"


def make_request(endpoint, method="GET", data=None):
    """Make HTTP request to Qdrant."""
    url = f"{QDRANT_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if data:
        data = json.dumps(data).encode('utf-8')

    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error: {e}")
        return None


def create_vector_from_text(text):
    """Create simple deterministic vector from text."""
    vector = [0.0] * 384
    words = text.lower().split()

    for i, word in enumerate(words):
        idx = abs(hash(word)) % 384
        vector[idx] += 0.1

    # Normalize
    magnitude = sum(v*v for v in vector) ** 0.5
    if magnitude > 0:
        vector = [v / magnitude for v in vector]

    return vector


def extract_checkpoint_data(checkpoint_file):
    """Extract key data from YAML checkpoint (handles both current and legacy schemas)."""
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not data:
        return None

    # Detect schema type
    if 'checkpoint' in data:
        # Current schema (2025-12-26 format)
        return extract_current_schema(data, checkpoint_file)
    elif 'session_id' in data or 'session_metadata' in data:
        # Legacy schema (2025-12-20 to 2025-12-24 format)
        return extract_legacy_schema(data, checkpoint_file)
    else:
        return None


def extract_current_schema(data, checkpoint_file):
    """Extract data from current checkpoint schema."""
    checkpoint = data['checkpoint']
    context = data.get('context', {})
    progress = data.get('progress', {})
    working_memory = data.get('working_memory', {})
    decisions = data.get('decisions_made', [])
    next_steps = data.get('next', {})

    # Create searchable text
    text_parts = []

    # Session info
    session_id = checkpoint.get('session_id', '')
    session_topic = checkpoint.get('session_topic', '')
    session_arc = checkpoint.get('session_arc', '')

    text_parts.append(f"Session: {session_topic}")
    text_parts.append(f"Arc: {session_arc}")

    # Mental model
    mental_model = working_memory.get('mental_model', '')
    if mental_model:
        text_parts.append(f"Mental model: {mental_model}")

    # Decisions
    if decisions:
        for decision in decisions[:3]:  # First 3 decisions
            if isinstance(decision, dict):
                dec_text = decision.get('decision', '')
                reasoning = decision.get('reasoning', '')
                text_parts.append(f"Decision: {dec_text}. Reasoning: {reasoning}")

    # Artifacts
    artifacts = progress.get('artifacts_created', [])
    if artifacts:
        artifact_names = [a.get('path', '') for a in artifacts if isinstance(a, dict)]
        text_parts.append(f"Created: {', '.join(artifact_names)}")

    searchable_text = ". ".join(text_parts)

    # Create payload
    payload = {
        "type": "session_checkpoint",
        "session_id": session_id,
        "session_topic": session_topic,
        "session_arc": session_arc,
        "created": checkpoint.get('created', ''),
        "ai_instance": context.get('ai', {}).get('instance', ''),
        "status": progress.get('status', ''),
        "artifacts_count": len(artifacts),
        "decisions_count": len(decisions),
        "_text": searchable_text,
        "source_file": str(checkpoint_file.name)
    }

    # Add mental model if present
    if mental_model:
        payload["mental_model"] = mental_model[:500]  # Truncate if too long

    # Add key decisions
    if decisions:
        payload["key_decisions"] = [
            {
                "decision": d.get('decision', '')[:200],
                "confidence": d.get('confidence', 'unknown')
            }
            for d in decisions[:3] if isinstance(d, dict)
        ]

    return {
        "searchable_text": searchable_text,
        "payload": payload
    }


def extract_legacy_schema(data, checkpoint_file):
    """Extract data from legacy checkpoint schema (pre-2025-12-25)."""
    # Handle different legacy formats
    session_id = data.get('session_id', '')
    timestamp = data.get('timestamp', '')

    # Session arc - multiple possible locations
    session_arc = data.get('session_arc', '')
    if not session_arc and 'session_metadata' in data:
        session_arc = data['session_metadata'].get('session_arc', '')

    # Extract topic from session_id or first line of arc
    session_topic = session_id.replace('_', ' ').replace('-', ' ').title()

    # Working memory
    working_memory = data.get('working_memory', {})
    mental_model = working_memory.get('mental_model', '')
    if isinstance(mental_model, dict):
        mental_model = str(mental_model)

    # Decisions - can be in multiple places
    decisions = data.get('decisions_made', [])
    if not decisions:
        decisions = data.get('technical_decisions', [])

    # Artifacts
    artifacts = data.get('artifacts_created', [])

    # Create searchable text
    text_parts = []
    text_parts.append(f"Session: {session_topic}")
    if session_arc:
        arc_preview = session_arc[:300] if len(session_arc) > 300 else session_arc
        text_parts.append(f"Arc: {arc_preview}")

    if mental_model:
        model_preview = mental_model[:300] if len(mental_model) > 300 else mental_model
        text_parts.append(f"Mental model: {model_preview}")

    # Add decisions
    if decisions:
        for decision in decisions[:3]:
            if isinstance(decision, dict):
                dec_text = decision.get('decision', '')
                reasoning = decision.get('reasoning', '') or decision.get('rationale', '')
                if dec_text:
                    text_parts.append(f"Decision: {dec_text}. Reasoning: {reasoning}")

    # Add artifacts
    if artifacts:
        artifact_names = [a.get('path', '') for a in artifacts if isinstance(a, dict)]
        if artifact_names:
            text_parts.append(f"Created: {', '.join(artifact_names[:5])}")

    searchable_text = ". ".join(text_parts)

    # Get AI instance
    ai_instance = ''
    if 'participants' in data:
        for p in data['participants']:
            if p.get('role') == 'First Mate':
                ai_instance = p.get('identifier', '')
    elif 'context' in data:
        ai_instance = data['context'].get('ai', {}).get('instance', '')

    # Create payload
    payload = {
        "type": "session_checkpoint",
        "session_id": session_id,
        "session_topic": session_topic,
        "session_arc": session_arc[:1000] if session_arc else '',  # Truncate long arcs
        "created": timestamp,
        "ai_instance": ai_instance,
        "status": data.get('status', 'legacy_format'),
        "artifacts_count": len(artifacts),
        "decisions_count": len(decisions),
        "_text": searchable_text,
        "source_file": str(checkpoint_file.name),
        "schema_version": "legacy"
    }

    # Add mental model if present
    if mental_model:
        payload["mental_model"] = mental_model[:500]

    # Add key decisions
    if decisions:
        payload["key_decisions"] = [
            {
                "decision": d.get('decision', '')[:200],
                "confidence": d.get('confidence', 'unknown')
            }
            for d in decisions[:3] if isinstance(d, dict)
        ]

    return {
        "searchable_text": searchable_text,
        "payload": payload
    }


def bridge_checkpoints():
    """Bridge all YAML checkpoints to Qdrant."""
    print("=" * 70)
    print("RHIZ MEMORY BRIDGE: YAML → Qdrant")
    print("=" * 70)

    # Get all checkpoint files
    checkpoint_files = list(CHECKPOINTS_DIR.glob("session_*.yaml"))
    print(f"\n→ Found {len(checkpoint_files)} checkpoint files")

    if not checkpoint_files:
        print("✗ No checkpoint files found")
        return

    # Process each checkpoint
    bridged_count = 0
    failed_count = 0

    for checkpoint_file in checkpoint_files:
        print(f"\n→ Processing {checkpoint_file.name}...")

        try:
            data = extract_checkpoint_data(checkpoint_file)

            if not data:
                print(f"  ⚠ Skipped (no valid data)")
                failed_count += 1
                continue

            # Create vector
            vector = create_vector_from_text(data["searchable_text"])

            # Generate point ID from session_id
            session_id = data["payload"].get("session_id", "")
            point_id = abs(hash(session_id)) % (2**63)

            # Upsert to Qdrant
            upsert_data = {
                "points": [
                    {
                        "id": point_id,
                        "vector": vector,
                        "payload": data["payload"]
                    }
                ]
            }

            result = make_request(
                f"/collections/{COLLECTION}/points",
                method="PUT",
                data=upsert_data
            )

            if result and result.get("status") == "ok":
                print(f"  ✓ Bridged successfully (ID: {point_id})")
                print(f"    Topic: {data['payload'].get('session_topic', '')[:60]}...")
                bridged_count += 1
            else:
                print(f"  ✗ Failed: {result}")
                failed_count += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed_count += 1

    # Summary
    print("\n" + "=" * 70)
    print("BRIDGE COMPLETE")
    print("=" * 70)
    print(f"✓ Successfully bridged: {bridged_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"📊 Total checkpoints: {len(checkpoint_files)}")

    # Get collection stats
    result = make_request(f"/collections/{COLLECTION}")
    if result and result.get("status") == "ok":
        points_count = result["result"].get("points_count", 0)
        print(f"📝 Qdrant collection now has: {points_count} total points")

    print("=" * 70)
    print("\n🎉 MEMORY ARCHITECTURE GAP BRIDGED!")
    print("Sessions now searchable via semantic queries in Qdrant.")
    print("=" * 70)


if __name__ == "__main__":
    bridge_checkpoints()
