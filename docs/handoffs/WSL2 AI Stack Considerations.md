# WSL2 development environment migration: a technical deep dive

**The WSL2-based AI development stack — Claude Code, MCP servers, Docker, and Qdrant — is fully viable but requires navigating a specific set of configuration pitfalls.** The most critical finding: MCP server failures on WSL2 stem primarily from stdio pipe bugs in Claude Code itself, path translation issues when working from `/mnt/c/`, and NAT networking isolation — not from fundamental architectural incompatibility. Docker runs at near-native Linux performance inside WSL2 regardless of whether you use Docker Desktop or native installation. Qdrant lacks built-in cross-instance sync but offers snapshot and migration tooling sufficient for a local-dev-plus-VPS workflow. Context management for long AI coding sessions has matured rapidly, with Claude Code now offering built-in session memory, compaction, and a rich MCP memory server ecosystem.

---

## MCP servers on WSL2: failure modes are specific and fixable

The Model Context Protocol uses **stdio transport** for local servers — Claude Code spawns the MCP server as a child process and communicates via JSON-RPC 2.0 over stdin/stdout pipes. This architecture works within WSL2 but has exposed several distinct failure modes.

**Protocol validation bugs in Claude Code itself** have been the largest source of "complete MCP failure." A widely-reported bug in v1.0.43 (July 2025) caused Claude Code to successfully start MCP servers but fail to expose their tools to AI sessions — the `tools/list` request would time out after 30 seconds due to a missing `protocolVersion` field in the initialize request. Multiple GitHub issues (#3426, #768) confirmed this affected WSL2 users specifically. A separate bug in v1.0.57 caused Claude Code to hang on startup entirely on WSL2/Ubuntu with NVM.

**Python-based MCP servers face specific stdio hazards.** Any package that prints to stdout (such as `python-dotenv` v17+ emitting load messages) corrupts the JSON-RPC stream and causes immediate failure. Python servers using `uvx` have encountered `BrokenPipeError` in `mcp/server/stdio.py` when the connection closes before initialization completes. The fix is strict — all server logging must go to stderr, never stdout.

**Path and filesystem issues compound the problem.** Working from Windows-mounted filesystems (`/mnt/c/`, `/mnt/e/`) is associated with `.mcp.json` config loading failures and degraded search performance. GitHub issue #5037 documents servers being silently ignored when Claude Code runs from `/mnt/e/` paths. **The official recommendation is unambiguous: keep projects on the native Linux filesystem** (`~/projects/`), where `.mcp.json` detection works reliably.

**Network isolation breaks HTTP/SSE-based MCP servers across the WSL2-Windows boundary.** WSL2's default NAT networking gives it a separate IP address from Windows, so `localhost` inside WSL2 does not resolve to Windows' localhost. The fix is enabling mirrored networking in `.wslconfig`:

```ini
[wsl2]
networkingMode = mirrored
```

For Claude Desktop on Windows communicating with MCP servers inside WSL2 via stdio, the established workaround uses `wsl.exe` as the command wrapper:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "wsl.exe",
      "args": ["bash", "-lc", "source ~/.nvm/nvm.sh && npx -y @some/mcp-server"]
    }
  }
}
```

The "Claude in Chrome" feature, when enabled on the Windows side, causes Claude Code to crash on WSL2 startup — the workaround is `claude --no-chrome`. Anthropic's official troubleshooting docs cover WSL2 installation issues but have **no dedicated WSL2-specific MCP documentation**.

---

## Docker Desktop versus native engine: native wins for AI workflows

Both approaches deliver near-native Linux container performance because they share the same Linux kernel running in WSL2's Hyper-V VM. The differences lie in overhead, licensing, networking transparency, and control.

**Docker Desktop with WSL2 backend** creates a dedicated `docker-desktop` WSL2 distribution running a LinuxKit-based environment. It provides a GUI, bundled Kubernetes, automatic `host.docker.internal` DNS, and Docker Scout vulnerability scanning. However, it carries **licensing restrictions**: organizations with 250+ employees or $10M+ annual revenue must purchase subscriptions ($9–24/month per user). It also adds baseline memory consumption from its management processes, and has documented issues including DNS breakage in WSL2 instances (docker/for-win #14023) and opaque storage management via VHDX files.

**Native Docker Engine** (installed via `apt` or `get.docker.com`) is Apache 2.0 licensed with **zero commercial restrictions**. It offers a lighter resource footprint, transparent storage at `/var/lib/docker`, direct Linux networking without vpnkit abstraction, and standard `systemctl` management. The tradeoffs are manual installation, no GUI (though Portainer fills this gap), and manual setup for `host.docker.internal` and Docker Compose plugin.

For AI development workflows involving MCP servers and vector databases, **native Docker is the stronger choice**. The direct networking simplifies container-to-host communication — critical when Qdrant needs to be reachable from Claude Code and MCP servers running in the same WSL2 instance. The zero-licensing-overhead matters for teams scaling up. The transparency aids debugging when MCP-Docker interactions fail.

**The critical performance variable is filesystem location, not Docker approach.** Files on WSL2's native ext4 filesystem get full I/O performance with inotify support. Files accessed via `/mnt/c/` suffer **up to 20x slower performance** due to the Plan9/9P protocol translation. This applies equally to both Docker approaches.

Memory management requires attention regardless of approach. WSL2 dynamically allocates RAM but doesn't release it easily until `wsl --shutdown`. Configure limits in `.wslconfig` with `memory=XGB` and consider `autoMemoryReclaim=gradual` (available in WSL 1.3.10+).

---

## WSL2 networking: localhost works, with caveats worth knowing

**A Qdrant container running in WSL2 Docker is accessible via `localhost:6333` from within WSL2.** When you run `docker run -p 6333:6333 qdrant/qdrant`, Docker maps the container port to WSL2's network interface, and `curl localhost:6333` works from within WSL2. From Windows, the same port is accessible via automatic localhost forwarding in NAT mode.

The known networking quirks fall into predictable categories. **Localhost forwarding can break after sleep/wake cycles** or VPN reconnection because WSL2's internal IP changes. The fix is `wsl --shutdown` and restart. **Subnet conflicts** between WSL2's randomly-selected subnet and Docker's bridge network (`172.17.0.0/16`) or corporate VPN ranges cause intermittent failures — Docker's `bip` engine setting resolves this. **Inside a container, `localhost` refers to the container itself**, not WSL2; to reach WSL2 services from a container, use `host.docker.internal` (Docker Desktop) or `--add-host host-gateway` (native Docker).

WSL2 networking has improved substantially. **Mirrored networking mode** (available since Windows 11 22H2) eliminates most cross-boundary issues by giving WSL2 the same IP addresses as the host. DNS tunneling, now default on Windows 11 22H2+, resolved most DNS reliability issues. However, mirrored mode is still not the default, and some Windows builds have been observed falling back to NAT silently. For the Qdrant use case, NAT mode with standard port mapping is sufficient since all components (Claude Code, MCP servers, Qdrant) run inside WSL2.

DNS resolution remains WSL2's most persistent pain point — GitHub issue microsoft/WSL#8365 has **239+ upvotes** and ongoing reports through 2025. Corporate VPNs are the primary trigger. Docker Desktop starting can break WSL2 DNS entirely. Mitigations include DNS tunneling, mirrored networking, or manual `/etc/resolv.conf` configuration.

---

## Context compression patterns that actually work in production

Teams managing LLM context windows have converged on several proven patterns, from simple file-based approaches to sophisticated agent-directed compression.

**Claude Code's built-in memory system is the foundation.** It implements a 4-tier hierarchy: enterprise policy, project memory (`CLAUDE.md`), project rules (`.claude/rules/`), and user memory (`~/.claude/CLAUDE.md`). The newer **Session Memory feature** automatically extracts summaries — first after ~10,000 tokens, then every ~5,000 tokens or 3 tool calls — storing them as markdown at `~/.claude/session-memory/`. New sessions receive relevant past summaries automatically. The `/compact` command summarizes the current conversation and starts fresh with that summary preloaded.

**Factory.ai's incremental compression approach** represents the production-grade pattern. Rather than re-summarizing the entire conversation each time the context fills, they maintain a **persistent rolling summary** and only summarize newly-dropped spans, merging them into the existing summary. This keeps compression cost constant per event. Their framework preserves four critical categories: session intent (user goals), high-level play-by-play (action sequence), artifact trail (files modified, test results), and breadcrumbs (paths and function names for re-accessing truncated content).

**The MCP memory server ecosystem has matured rapidly.** Anthropic's official `@modelcontextprotocol/server-memory` stores entities, observations, and relations as a local knowledge graph in JSONL. More sophisticated options include Memento MCP (Neo4j-backed with semantic retrieval and temporal awareness), mcp-memory-service (with knowledge graph visualization and cloud sync), and Zep/Graphiti (temporal knowledge graphs tracking how information changes over time).

**Two research-backed architectures stand out for development workflows:**

- **MemGPT/Letta's two-tier model** (inspired by OS memory paging): compact core memory stays in-context while archival memory lives in a vector database, with the agent self-managing what moves between tiers. Now an open-source framework with multi-agent memory sharing.
- **The Focus architecture** (arXiv, January 2026): agents declare investigation boundaries with `start_focus`/`complete_focus` primitives, compress completed explorations into high-level learnings, and delete raw logs. This achieved **18–57% token savings** on exploration-heavy tasks.

For teams using Qdrant specifically, the pattern is to embed conversation segments into vectors with metadata (timestamp, task ID, tags), retrieve via semantic similarity when context is needed, and inject relevant memories into the context window. The `memory-mcp` project demonstrates this with a two-tier system: Tier 1 is an auto-generated CLAUDE.md (~150 lines, ranked by confidence × access frequency), and Tier 2 is a full memory store accessible via MCP tools using Claude Code hooks for automatic capture at session boundaries.

---

## Qdrant across local and cloud: snapshot workflows bridge the gap

Qdrant does **not offer built-in cross-instance real-time sync** between isolated instances. Cross-cluster replication is on their roadmap but not yet available. Three official mechanisms bridge local development and cloud VPS environments.

**The snapshot-based workflow** is the primary method. Snapshots are tar archives containing collection configuration, all vectors and payloads, HNSW index structures, and write-ahead log data (~32 MB per shard baseline). For a collection of 10K–100K vectors at 768 dimensions, expect snapshot sizes of **70–500 MB**. The workflow: create a snapshot via `POST /collections/{name}/snapshots`, download it, then upload to the target instance via `POST /collections/{name}/snapshots/upload?priority=snapshot`. Snapshots can only be restored to instances running the **same Qdrant minor version**.

**The official migration tool** (Docker-based, at `github.com/qdrant/migration`) streams collections between instances in live batches via gRPC, supporting configurable batch sizes and resumable transfers. It also supports migration from Chroma, Pinecone, Milvus, and several other databases.

**The Python client's `migrate()` function** offers programmatic sync:

```python
from qdrant_client import QdrantClient
from qdrant_client.migrate import migrate

source = QdrantClient(url="http://localhost:6333")
dest = QdrantClient(url="http://vps:6333", api_key="key")
migrate(source, dest, collection_names=["my_collection"],
        recreate_on_collision=True, batch_size=100)
```

Collection schema management requires an infrastructure-as-code approach since **vector size and distance metric cannot be changed after creation**. Define collection schemas in version-controlled Python files, use `collection_exists()` for idempotent creation, and leverage aliases for zero-downtime collection swaps. Since Qdrant v1.10, snapshots can be stored directly to S3 by configuring `snapshots_config.snapshots_storage: s3`, though direct restore from S3 requires pre-signed URLs passed to the recovery endpoint.

The recommended dual-environment workflow: keep both instances on the same Qdrant minor version, define schemas in version-controlled code, use the Python `migrate()` function for routine syncs, reserve snapshot-based transfers for exact copies including indexes, and automate periodic backups via the snapshot API plus S3 or local storage.

---

## Claude Code on WSL2: installation is clean, the edges are rough

Claude Code installs on WSL2 via the native installer — `curl -fsSL https://claude.ai/install.sh | bash` — which places a binary at `~/.local/bin/claude`. No Node.js or npm is required. The legacy npm installation method (`npm install -g @anthropic-ai/claude-code`) still works but introduces a common pitfall: WSL2 may use Windows-side Node.js instead of Linux versions, requiring `npm config set os linux` or explicit path management. **Claude Code v2.x also supports native Windows** (installed via PowerShell or WinGet), but WSL2 runs the Linux build and sees itself as running on standard Linux.

Claude Code discovers `.mcp.json` by searching the current directory and parent directories, expanding environment variables at runtime. **On WSL2's native filesystem (`~/projects/`), this works reliably.** On Windows-mounted paths (`/mnt/c/`), users have reported partial config loading — some servers connect while others are silently ignored. The official troubleshooting documentation explicitly recommends moving projects to the Linux filesystem for better performance and reliability.

**The practical decision between Claude Code in WSL2 versus Claude Desktop on Windows** depends on where your development tools live. Claude Code in WSL2 spawns MCP servers as native Linux child processes with direct access to Docker, Python, and system tools — **tool compatibility is effectively 100%** versus roughly 70% on native Windows. Claude Desktop on Windows requires `wsl.exe` wrappers for WSL2-side servers and cannot natively execute commands inside WSL2. For a stack centered on Docker containers, Python MCP servers, and Qdrant, Claude Code running natively in WSL2 is the more integrated choice.

Key operational flags to know: `--no-chrome` prevents the Chrome Native Host crash on WSL2, `MCP_TIMEOUT` (environment variable) adjusts the 30-second default for MCP server initialization, and sandboxing on WSL2 requires `socat` and `bubblewrap` packages installed. WSL1 does not support sandboxing at all.

## Conclusion

The WSL2 AI development stack works, but demands a specific configuration discipline. **Store everything on the native Linux filesystem** — this single decision eliminates the majority of performance issues, `.mcp.json` detection failures, and Docker volume mount problems. **Enable mirrored networking** if any component needs cross-boundary communication. **Use native Docker Engine** for transparency and zero licensing friction. **Pin Qdrant versions** across environments and use the Python `migrate()` function for routine sync. For context management, Claude Code's built-in Session Memory plus a knowledge-graph MCP server covers most needs; teams wanting more should look at Factory.ai's incremental compression pattern or the Focus architecture's agent-directed checkpointing. The ecosystem is maturing fast — most of the WSL2-specific MCP bugs documented here have been filed and addressed within the last six months.