# Claude Code Changelog

Tracking new features and changes relevant to this repository.
Updated via `/update` command or the `updater` agent.

---

## March 2026

### Claude Code on the Web (March 2026)
Run tasks on Anthropic-managed cloud VMs via `claude --remote "..."` or claude.ai/code. Isolated sandboxes, automatic PR creation. Session handoff between cloud and terminal via `/teleport` (pull web session to terminal) and `/remote-control` (bridge terminal to web). Auto-fix PRs: Claude subscribes to a GitHub PR, responds to CI failures and review comments automatically.

### Computer Use (March 24, 2026)
Claude Code Desktop app (macOS, research preview for Pro/Max) can directly operate the computer — open files, click buttons, use browser and dev tools — as a fallback when no MCP connector is available. Desktop app must be open, computer awake.

### Dispatch (March 24, 2026)
Assign tasks from phone (iOS/Android) to desktop Claude app. Walk away, return to finished work. Persistent session between phone and desktop. Works with computer use.

### Auto Mode (March 24, 2026)
AI-driven permission decisions with built-in safety guardrails. Research preview on Team plan. AI classifier reviews each action before execution, detecting risky behavior and prompt injection attempts. Use in isolated environments initially.

### Channel-Based Permission Relay (--channels)
Research preview. Channel servers with `permission` capability forward tool approval prompts to a developer's phone. Enables truly async autonomous operation.

### /context Command (v2.1.74, March 12, 2026)
Surfaces actionable optimization tips: identifies which tools consume the most context, detects memory bloat, issues capacity warnings.

### /simplify and /batch (March 3, 2026)
Bundled built-in skill-commands. `/simplify` runs three parallel review agents (code reuse, quality, efficiency) on changed files. `/batch` orchestrates the same prompt across many files in parallel, each worker auto-runs `/simplify` before committing.

### New Hook Events
Five new events: `TaskCreated` (subagent task spawned), `PostCompact` (after /compact), `StopFailure` (API errors), `Elicitation` and `ElicitationResult` (structured MCP input). Hooks now support conditional `if` fields using permission rule syntax.

### --bare Flag
`claude --bare -p "..."` skips hooks, LSP, plugin sync, and skill directory walks. Designed for CI/scripted usage. Requires `ANTHROPIC_API_KEY` or `--settings` with `apiKeyHelper`.

### Commands/Skills Merge
Files in `.claude/commands/` and `.claude/skills/*/SKILL.md` both produce `/slash-command` interface. Skills location is now recommended for anything beyond a simple prompt.

### autoMemoryDirectory Setting
New `autoMemoryDirectory` in `settings.json` configures where auto-memory files are stored (useful for monorepos). Memory files now include last-modified timestamps.

### managed-settings.d/ Drop-In Directory
Independent policy fragments as partial `settings.json` files. Enables org-level policy distribution without overwriting developer settings.

### worktree.sparsePaths Setting
Git sparse-checkout for agent worktrees in monorepos. Agents only check out needed paths, reducing disk use and clone time.

### Voice Mode
`/voice` command activates push-to-talk mode. Hold spacebar to speak, release to send. Supports 20 languages. Free transcription (doesn't count against rate limits).

### /effort Command
Adaptive reasoning control: `/effort low`, `/effort medium`, `/effort high`, `/effort max`, `/effort auto`. Default is medium. Higher effort doesn't always improve coding outputs.

## February 2026

### Agent Teams (February 5, 2026)
2-16 coordinated agents per team. One lead coordinator + teammates in independent context windows. Shared task list + peer-to-peer mailbox messaging. Start with 3-5 teammates for optimal speed/coordination balance.

### Claude Opus 4.6
1 million token context window on Max, Team, and Enterprise plans.

### Subagents Enhancement
Up to 10 simultaneous subagents per session. Custom subagents via Markdown with YAML frontmatter. Worktree support for conflict-free parallel file operations.

## 2025-2026 (Cumulative)

### .claude/rules/ Directory (established feature, documented 2025-2026)
Modular instruction files as an alternative to monolithic CLAUDE.md. Each `.md` file covers one topic. Optional `paths:` YAML frontmatter for path-scoped rules (glob patterns, loaded on demand). Discovered recursively, supports symlinks. User-level variant at `~/.claude/rules/`. Preferred over subdirectory CLAUDE.md files for path-scoped modular instructions.

### Skills 2.0
Two categories: Capability Uplift (fill model gaps, limited lifespan) and Workflow/Preference (automation, compliance, longer value). Shell commands can inject live data into skill prompts.

### Plugins Ecosystem
101+ official plugins. Plugin types: Skills, Hooks, MCP servers. Notable: Firecrawl (web data), Context 7 (APIs), Playwright (testing).

### MCP Elicitation
MCP servers can request structured input during execution. Display interactive forms or open URLs without interrupting workflow.

### Hooks System Matured
Types: command, prompt, agent, http. Initial events: SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, Notification, PermissionRequest, Stop, ConfigChange, FileChanged, CwdChanged. (See March 2026 — New Hook Events for 5 additional events and conditional `if` fields.)

### Dangerous Command Blocker
Community-standard hook pattern. PreToolUse intercepts rm -rf, git reset --hard, git push --force, git clean -f. Takes 2 minutes to set up, protects all projects. Can be extended with DROP TABLE, credential deletion, etc.

---

*Last checked: 2026-03-27*
