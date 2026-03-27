# Claude Code Changelog

Tracking new features and changes relevant to this repository.
Updated via `/update` command or the `updater` agent.

---

## March 2026

### Auto Mode (March 24, 2026)
AI-driven permission decisions with built-in safety guardrails. Research preview on Team plan. AI classifier reviews each action before execution, detecting risky behavior and prompt injection attempts. Use in isolated environments initially.

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

### Skills 2.0
Two categories: Capability Uplift (fill model gaps, limited lifespan) and Workflow/Preference (automation, compliance, longer value). Shell commands can inject live data into skill prompts.

### Plugins Ecosystem
101+ official plugins. Plugin types: Skills, Hooks, MCP servers. Notable: Firecrawl (web data), Context 7 (APIs), Playwright (testing).

### MCP Elicitation
MCP servers can request structured input during execution. Display interactive forms or open URLs without interrupting workflow.

### Hooks System Matured
Types: command, prompt, agent, http. Events: SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, Notification, PermissionRequest, Stop, ConfigChange, FileChanged, CwdChanged.

### Dangerous Command Blocker
Community-standard hook pattern. PreToolUse intercepts rm -rf, git reset --hard, DROP TABLE, credential deletion. Takes 2 minutes to set up, protects all projects.

---

*Last checked: 2026-03-27*
