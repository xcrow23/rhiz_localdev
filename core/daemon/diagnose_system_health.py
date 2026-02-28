"""
Rhiz System Health Diagnostic

One-command health check for all critical subsystems:
- Dyad state integrity
- Checkpoint system
- Memory/Qdrant connectivity
- MCP server status
- Trading infrastructure (if configured)

Created: 2026-01-19
Purpose: Provide comprehensive system status for troubleshooting
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Detect RHIZ_ROOT
RHIZ_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(RHIZ_ROOT))

try:
    from qdrant_client import QdrantClient
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class SystemHealthDiagnostic:
    """Comprehensive system health checker."""

    def __init__(self):
        self.rhiz_root = RHIZ_ROOT
        self.results = {}
        self.warnings = []
        self.errors = []

    def check_dyad_state(self) -> Tuple[bool, str]:
        """Check dyad.md integrity."""
        try:
            dyad_path = self.rhiz_root / "core" / "daemon" / "dyad.md"

            if not dyad_path.exists():
                return False, f"dyad.md not found at {dyad_path}"

            # Read and parse
            with open(dyad_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract YAML frontmatter
            if "---" in content:
                parts = content.split("---")
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    data = yaml.safe_load(yaml_content)

                    # Check required sections
                    required = ["CAPTAIN_STATE", "FIRST_MATE", "SHARED_FOCUS", "ACTIVE_DOMAINS"]
                    missing = [s for s in required if s not in data]

                    if missing:
                        return False, f"Missing sections: {', '.join(missing)}"

                    return True, f"Dyad state intact ({len(data)} sections)"

            return False, "Invalid dyad.md format (no YAML frontmatter)"

        except Exception as e:
            return False, f"Error reading dyad.md: {e}"

    def check_checkpoints(self) -> Tuple[bool, str]:
        """Check checkpoint system."""
        try:
            checkpoint_dir = self.rhiz_root / "core" / "memory" / "checkpoints"

            if not checkpoint_dir.exists():
                return False, f"Checkpoint directory not found: {checkpoint_dir}"

            # Count checkpoints
            checkpoints = list(checkpoint_dir.glob("session_*.yaml"))

            if len(checkpoints) == 0:
                return False, "No checkpoints found"

            # Try loading most recent
            checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            latest = checkpoints[0]

            try:
                with open(latest, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                # Check schema compliance
                if "checkpoint" not in data:
                    self.warnings.append(f"Latest checkpoint ({latest.name}) missing 'checkpoint' wrapper")

                return True, f"{len(checkpoints)} checkpoints found, latest: {latest.name}"

            except yaml.YAMLError as e:
                return False, f"Latest checkpoint YAML error: {e}"

        except Exception as e:
            return False, f"Error checking checkpoints: {e}"

    def check_qdrant(self) -> Tuple[bool, str]:
        """Check Qdrant connectivity and collections."""
        if not QDRANT_AVAILABLE:
            return False, "qdrant-client not installed (pip install qdrant-client)"

        try:
            client = QdrantClient(host="localhost", port=6333, timeout=5)

            # Get collections
            collections = client.get_collections().collections
            collection_names = [c.name for c in collections]

            if "rhiz_memories" not in collection_names:
                return False, "Collection 'rhiz_memories' not found"

            # Get collection info
            info = client.get_collection("rhiz_memories")
            point_count = info.points_count

            return True, f"Qdrant connected, rhiz_memories: {point_count} points"

        except ConnectionError:
            return False, "Cannot connect to Qdrant (localhost:6333) - is Docker container running?"
        except Exception as e:
            return False, f"Qdrant error: {e}"

    def check_memory_scripts(self) -> Tuple[bool, str]:
        """Check memory system scripts."""
        try:
            scripts_dir = self.rhiz_root / "core" / "memory" / "scripts"

            required_scripts = [
                "embeddings.py",
                "search.py",
                "ingest.py",
                "validate_checkpoint.py",
                "deduplicate_memory.py"
            ]

            missing = []
            for script in required_scripts:
                if not (scripts_dir / script).exists():
                    missing.append(script)

            if missing:
                return False, f"Missing scripts: {', '.join(missing)}"

            return True, f"All {len(required_scripts)} memory scripts present"

        except Exception as e:
            return False, f"Error checking scripts: {e}"

    def check_mcp_servers(self) -> Tuple[bool, str]:
        """Check MCP server configurations."""
        try:
            # Check for rhiz-mcp
            rhiz_mcp_dir = self.rhiz_root / "tools" / "rhiz-mcp"
            memory_mcp_dir = self.rhiz_root / "tools" / "memory-mcp"

            servers = []
            if rhiz_mcp_dir.exists():
                server_file = rhiz_mcp_dir / "src" / "server.py"
                if server_file.exists():
                    servers.append("rhiz-mcp")

            if memory_mcp_dir.exists():
                server_file = memory_mcp_dir / "src" / "server.py"
                if server_file.exists():
                    servers.append("memory-mcp")

            if not servers:
                return False, "No MCP servers found"

            # Check .mcp.json config
            mcp_config = self.rhiz_root / ".mcp.json"
            if mcp_config.exists():
                with open(mcp_config, "r") as f:
                    import json
                    config = json.load(f)
                    configured_servers = list(config.get("mcpServers", {}).keys())
                    return True, f"MCP: {', '.join(servers)} ({len(configured_servers)} configured)"
            else:
                self.warnings.append(".mcp.json not found - MCP servers may not be registered")
                return True, f"MCP: {', '.join(servers)} present"

        except Exception as e:
            return False, f"Error checking MCP: {e}"

    def check_trading_infrastructure(self) -> Tuple[bool, str]:
        """Check trading system components (optional)."""
        try:
            trading_dir = self.rhiz_root / "domains" / "trading"

            if not trading_dir.exists():
                return True, "Trading domain not configured (optional)"

            components = []

            # Check Fathom
            if (trading_dir / "fathom").exists():
                components.append("Fathom")

            # Check Fathom Commander
            if (trading_dir / "fathom_commander").exists():
                components.append("FC")

            # Check SIL
            if (trading_dir / "strategic_intelligence").exists():
                components.append("SIL")

            if components:
                return True, f"Trading: {', '.join(components)} present"
            else:
                return True, "Trading components not found"

        except Exception as e:
            return False, f"Error checking trading: {e}"

    def check_hooks(self) -> Tuple[bool, str]:
        """Check session hooks."""
        try:
            hooks_dir = self.rhiz_root / "core" / "hooks"

            if not hooks_dir.exists():
                return False, f"Hooks directory not found: {hooks_dir}"

            required_hooks = ["session_start.py", "session_end.py"]
            present = []
            missing = []

            for hook in required_hooks:
                if (hooks_dir / hook).exists():
                    present.append(hook)
                else:
                    missing.append(hook)

            if missing:
                return False, f"Missing hooks: {', '.join(missing)}"

            return True, f"Session hooks: {len(present)}/{len(required_hooks)}"

        except Exception as e:
            return False, f"Error checking hooks: {e}"

    def run_diagnostics(self) -> Dict:
        """Run all diagnostic checks."""
        print("=" * 80)
        print("RHIZ SYSTEM HEALTH DIAGNOSTIC")
        print("=" * 80)
        print(f"Root: {self.rhiz_root}")
        print(f"Time: {datetime.now().isoformat()}")
        print("")

        checks = [
            ("Dyad State", self.check_dyad_state),
            ("Checkpoints", self.check_checkpoints),
            ("Qdrant Memory", self.check_qdrant),
            ("Memory Scripts", self.check_memory_scripts),
            ("MCP Servers", self.check_mcp_servers),
            ("Session Hooks", self.check_hooks),
            ("Trading Infrastructure", self.check_trading_infrastructure),
        ]

        passed = 0
        failed = 0

        for name, check_func in checks:
            try:
                success, message = check_func()
                self.results[name] = {"success": success, "message": message}

                status = "[OK]" if success else "[FAIL]"
                print(f"{status:6} {name:25} {message}")

                if success:
                    passed += 1
                else:
                    failed += 1
                    self.errors.append(f"{name}: {message}")

            except Exception as e:
                self.results[name] = {"success": False, "message": f"Exception: {e}"}
                print(f"[FAIL] {name:25} Exception: {e}")
                failed += 1
                self.errors.append(f"{name}: {e}")

        # Summary
        print("")
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Passed: {passed}/{len(checks)}")
        print(f"Failed: {failed}/{len(checks)}")

        if self.warnings:
            print(f"\n[WARNINGS] ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.errors:
            print(f"\n[ERRORS] ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        # Overall health
        health_percentage = (passed / len(checks)) * 100

        if health_percentage == 100:
            health_status = "EXCELLENT"
        elif health_percentage >= 80:
            health_status = "GOOD"
        elif health_percentage >= 60:
            health_status = "FAIR"
        else:
            health_status = "POOR"

        print(f"\nOverall Health: {health_percentage:.0f}% ({health_status})")
        print("=" * 80)

        return {
            "passed": passed,
            "failed": failed,
            "total": len(checks),
            "health_percentage": health_percentage,
            "health_status": health_status,
            "warnings": self.warnings,
            "errors": self.errors,
            "results": self.results
        }


def diagnose():
    """Run diagnostic and return results."""
    diagnostic = SystemHealthDiagnostic()
    return diagnostic.run_diagnostics()


if __name__ == "__main__":
    result = diagnose()
    sys.exit(0 if result["failed"] == 0 else 1)
