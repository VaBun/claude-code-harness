# Claude Code Tips

A living knowledge system for Claude Code best practices. Every file in this repository is a working example of what it describes. The repo monitors new features, curates content quality, and deploys knowledge to other projects.

**Three ways to use this repo:**
1. **Learn** — read this guide, explore the live files it points to
2. **Deploy** — run the one-liner below to bootstrap any project
3. **Contribute** — run `/catchup`, pick a task from `docs/progress.json`

## Quick Start: Deploy Harness to Your Project

Run this in any project directory:

```bash
git clone --depth 1 https://github.com/VaBun/claude-code-harness.git /tmp/cc-harness && mkdir -p .claude/skills && cp -r /tmp/cc-harness/.claude/skills/harness-init .claude/skills/ && rm -rf /tmp/cc-harness
```

Then open Claude Code and say **"harness init"**. It will analyze your project and generate: CLAUDE.md, hooks, 5 slash commands, golden rules, architecture docs, and progress tracking.

---

## Repository Map

```
┌─ Project files (what you see on GitHub) ─────────────────┐
│  README.md        → this guide                           │
│  CLAUDE.md        → project constitution (golden rules)  │
│  docs/            → reference, state, decision log       │
│    capability-map  → built-in CC vs harness tracking     │
└──────────────────────────────────────────────────────────┘
┌─ .claude/ — Claude Code tools ───────────────────────────┐
│  settings.json    → hooks & permissions                  │
│  commands/        → /plan, /review, /catchup, ...        │
│  agents/          → reviewer, updater                    │
│  skills/          → harness-init (the deployer)          │
└──────────────────────────────────────────────────────────┘
┌─ .github/ — Automation ─────────────────────────────────┐
│  workflows/       → weekly feature monitoring            │
└──────────────────────────────────────────────────────────┘
```

---

## 1. CLAUDE.md — Project Constitution

The first file Claude reads in any session. Contains: project overview, key commands, golden rules, module guide. Keep it under 200 lines. Include only what the agent can't infer from code.

**What to include:** build/test/lint commands, architectural constraints, naming conventions, what NOT to do, **Definition of Done** (explicit acceptance criteria for completed work).
**What to skip:** standard language conventions, things linters catch, file-by-file descriptions.

**Companion files:** consider a `PRD.md` alongside CLAUDE.md for feature specs and acceptance criteria. Claude reads both at session start, preserving requirements across `/clear` boundaries.

**Hierarchy:** root `CLAUDE.md` for global context. Subdirectory `CLAUDE.md` files for module-specific rules (loaded on demand). Child files don't repeat parent — they add specifics.

**`.claude/rules/` directory:** for path-scoped modular instructions. Each `.md` file covers one topic. Add `paths:` YAML frontmatter (e.g., `paths: ["src/api/**/*.ts"]`) to load rules only when Claude reads matching files. Without frontmatter — loaded at launch. Discovered recursively, supports symlinks, user-level variant at `~/.claude/rules/`.

> See [`./CLAUDE.md`](CLAUDE.md) — this repo's own constitution.

---

## 2. Hooks — Deterministic Guardrails

Shell commands that execute at lifecycle points. Unlike CLAUDE.md instructions (~80% followed), hooks are 100% deterministic.

| Event | When | Can block? |
|-------|------|-----------|
| `PreToolUse` | Before tool executes | Yes (exit 2) |
| `PostToolUse` | After tool succeeds | No |
| `SessionStart` | Session begins/resumes | No |
| `UserPromptSubmit` | Before Claude processes prompt | Yes |
| `Notification` | Claude needs input | No |
| `PermissionRequest` | Permission dialog appears | Yes |
| `Stop` | Claude finishes responding | No |
| `StopFailure` | API error (rate limit, auth) | No |
| `TaskCreated` | Subagent task spawned | No |
| `PostCompact` | After `/compact` completes | No |
| `Elicitation` / `ElicitationResult` | MCP structured input | Yes |
| `ConfigChange` | Settings file modified | Yes |
| `FileChanged` / `CwdChanged` | Environment changes | No |

**Hook types:** `command` (shell), `prompt` (single-turn Claude eval), `agent` (multi-turn subagent), `http` (POST to endpoint).

**Matcher patterns:** `Edit|Write`, `Bash(git commit*)`, `mcp__github__*`. Hooks support conditional `if` fields using permission rule syntax.

**Cloud guard (pattern):** Check `CLAUDE_CODE_REMOTE=true` in SessionStart hooks to differentiate local vs cloud sessions. **Org policy:** `managed-settings.d/` drop-in directory for distributing hook policies across teams.

**Essential hook: Dangerous Command Blocker.** PreToolUse intercepts `rm -rf`, `git reset --hard`, `git push --force`. Takes 2 minutes to set up, prevents catastrophic accidents.

> See [`.claude/settings.json`](.claude/settings.json) — this repo's hooks: JSON validation pre-commit, dangerous command blocker, post-edit reminder.

---

## 3. Commands — Slash Commands

Markdown files in `.claude/commands/` invoked via `/command-name`. Each file is a natural-language prompt with optional `$ARGUMENTS` placeholder. Commands and skills now share the same `/slash-command` interface — skills (with SKILL.md frontmatter) are preferred for anything beyond a simple prompt.

**Built-in commands:** `/simplify` (parallel code review agents), `/batch` (same prompt across many files).

**Scopes:** project (`.claude/commands/`) or user (`~/.claude/commands/`).

**Scripted usage:** `claude --bare -p "..."` skips hooks/LSP/plugins for CI pipelines.

> See [`.claude/commands/`](.claude/commands/) — 6 commands: `/plan`, `/review`, `/catchup`, `/save`, `/audit`, `/update`. Each serves a real workflow in this repo.

---

## 4. Skills — Reusable Capabilities

Folders with `SKILL.md` defining what Claude can do. Skills trigger automatically when relevant, or manually via `/skill-name`.

**SKILL.md frontmatter:**
```yaml
---
name: skill-identifier
description: When to use this skill
tools: Read, Grep, Bash           # optional: restrict tools
context: fork                      # optional: run in subagent
model: sonnet                      # optional: override model
user-invocable: true               # optional: show in /menu
---
```

**Skills 2.0 categories:**
- **Capability Uplift** — fill model gaps (limited lifespan as models improve)
- **Workflow/Preference** — automation, compliance (longer value)

**Data injection:** Use `` !`shell command` `` in skill body to inject live data before Claude sees the prompt.

> See [`.claude/skills/harness-init/`](.claude/skills/harness-init/) — deploys a complete harness to any project. This is the repo's "product": one skill that unfolds into CLAUDE.md + hooks + commands + golden rules + architecture docs.

---

## 5. Agents — Subagents

Custom agents with isolated context windows ("context firewalls"), restricted tools, and specific models. Up to 10 simultaneous per session.

**Definition:** `.claude/agents/name.md` with YAML frontmatter:
```yaml
---
name: reviewer
description: When to use this agent
tools: Read, Grep, Glob, Bash     # allowed tools
disallowedTools: Write, Edit       # denied tools
model: sonnet                      # model override
---
```

**Key fields:** `maxTurns`, `memory` (project/user/local), `isolation` (worktree), `background` (true/false), `permissionMode`.

**Invocation:** natural language ("use the reviewer to check this"), `@"reviewer (agent)"`, or `--agent reviewer` flag.

> See [`.claude/agents/`](.claude/agents/) — `reviewer` (read-only content review) and `updater` (web monitoring for new CC features). Both genuinely serve this repo.

---

## 6. Agent Teams

2-16 coordinated agents working in parallel (February 2026). One lead coordinator + teammates with independent context windows. Communication via shared task list + peer-to-peer mailbox messaging.

**Best practice:** Start with 3-5 teammates. Use for tasks that decompose into independent subtasks (migrations, multi-file refactors, parallel feature work).

---

## 7. MCP Servers — External Tools

Model Context Protocol connects Claude Code to external services (GitHub, Linear, Slack, databases).

**Setup:** `claude mcp add <name> -- <command>` or `.mcp.json` file.

**MCP Elicitation:** Servers can request structured input during execution — display forms or open URLs mid-workflow.

**Scopes:** global (`~/.claude/.mcp.json`), project (`.claude/.mcp.json`), local (`.claude/.mcp.local.json`).

**Security:** grant only necessary access (scoped paths, specific pages). Store credentials in MCP config, never in prompts. Review data-modifying actions before approval.

---

## 8. Plugins

101+ official plugins bundling skills, hooks, and MCP servers into installable units. Browse and install via the plugin ecosystem.

**Notable:** Firecrawl (web data), Context 7 (APIs), Playwright (testing).

---

## 9. Scheduled Tasks & Async Execution

Five approaches to deferred/recurring work:

| Method | Scope | Min interval | Requires |
|--------|-------|-------------|----------|
| `/loop` | Session | 1 minute | CLI open |
| Desktop Tasks | Local | 1 minute | Desktop app |
| GitHub Actions | Repository | N/A (cron) | GitHub repo |
| Dispatch | Phone→Desktop | On-demand | Desktop app + mobile |
| Cloud (`--remote`) | Cloud VM | On-demand | claude.ai account |

**`/loop`** example: `/loop 5m check if deployment finished`

**CronCreate** tool: schedule prompts directly in conversation. Standard 5-field cron, local timezone. Auto-expires after 3 days.

**Dispatch:** assign a task from your phone, walk away, return to finished work on desktop. **Cloud:** `claude --remote "task"` runs on Anthropic-managed VMs — no local machine needed.

> See [`.github/workflows/check-updates.yml`](.github/workflows/check-updates.yml) — weekly cron that checks Anthropic's changelog and creates Issues for new features.

---

## 10. Claude Code on the Web

Run Claude Code on Anthropic-managed cloud VMs — no local machine needed.

**Launch:** `claude --remote "implement the migration"` from terminal, or start a session at claude.ai/code.

**Auto-fix PRs:** Claude subscribes to a GitHub PR, automatically responds to CI failures and review comments. Pushes fixes for clear cases, asks before acting on ambiguous ones. Requires the Claude GitHub App.

**Session handoff:** `/teleport` pulls a web session into your local terminal (branch + conversation). `/remote-control` bridges a terminal session to the web for cross-device continuation.

---

## 11. Worktrees — Parallel Work

Git worktrees give each agent an isolated copy of the repo. No file conflicts.

```bash
claude --worktree feature-auth    # Terminal 1
claude --worktree bugfix-db       # Terminal 2 (parallel)
```

**Pattern:** N worktrees → N agents → N PRs → human reviews and merges.

**Subagent integration:** Set `isolation: worktree` in agent frontmatter for automatic worktree creation.

**Monorepos:** `worktree.sparsePaths` setting enables git sparse-checkout — agents only check out paths they need.

---

## 12. Auto Mode & Autonomy

AI-driven permission decisions (March 2026, research preview). A classifier model reviews each action before execution, detecting risky behavior and prompt injection attempts.

**Permission relay (`--channels`):** channel servers forward approval prompts to your phone — enables truly async autonomous operation.

**Computer use:** Desktop app (macOS, research preview) can directly operate the computer — open files, click buttons, use browser — as fallback when no MCP connector is available.

**Recommendation:** Use in sandboxed environments first. The classifier's behavior is not fully transparent — don't trust it with production credentials yet.

---

## 13. Voice Mode

`/voice` activates push-to-talk. Hold spacebar → speak → release to send. 20 languages supported. Free transcription.

---

## 14. /effort — Adaptive Reasoning

`/effort low` (fast/cheap) → `medium` (default) → `high` → `max` (deepest reasoning, Opus only) → `auto` (model picks). Higher effort doesn't always help — medium is often optimal for coding.

**Model selection:** Sonnet for everyday coding and learning. Opus for complex architecture, extended autonomous sessions, multi-agent workflows. Haiku for trivial queries and subagent tasks. A less capable model often costs more per task due to correction passes.

---

## 15. Context Management

Three built-in tools for managing the context window:

- **`/clear`** — hard reset. Wipes ALL history. CLAUDE.md auto-reloads. Use between unrelated tasks.
- **`/compact`** — soft compression. Condenses context into summary, preserves essential thread. Use when context is partially relevant.
- **`/context`** — diagnostic. Shows which tools consume the most context, detects memory bloat, issues capacity warnings.

**Auto-memory:** persistent file-based memory across sessions. Configure storage location with `autoMemoryDirectory` in `settings.json` (useful for monorepos). Memory files include timestamps for staleness detection.

**Rule of thumb:** if less than 50% of prior context is relevant, `/clear`. Otherwise `/compact`.

**Best practice:** `/clear` after every commit to prevent hallucinations in long sessions.

---

## 16. Workflow Patterns

**Interview → Plan → Execute → Review:** Before planning, ask Claude to interview you — surface undecided requirements, trade-offs, acceptance criteria. Then: explore without changes → plan → implement → verify → commit. Activate plan mode with Shift+Tab twice.

**Specification quality test:** could a competent engineer read your prompt with no other context and build exactly what you envision? If not, add: library versions, data structures, file boundaries, acceptance criteria.

**Initializer → Coding Agent:** For new projects. First session creates skeleton (directory structure, empty files with correct imports and signatures). Subsequent sessions build logic one feature at a time.

**Harness Engineering Loop:** Agent makes mistake → add golden rule → encode in hook/test → mistake never happens again. The harness grows monotonically.

**Background Swarm:** N isolated tasks → N branches → N agents → N PRs. Condition: tasks don't touch same files, each is independently verifiable.

**Plan Locally, Execute Remotely:** Start in `--permission-mode plan` to collaborate on strategy with no file writes. When ready, fire `claude --remote "Execute the plan"` to run on cloud VMs. Multiple `--remote` calls give each task its own isolated VM.

**Document & Clear:** After 30+ minutes, `/save` → `/clear` → new session reads progress.json + decisions/. Prevents context decay.

---

## 17. Harness Engineering — 5 Layers

The discipline of building scaffolding around AI agents. Not the agent, not the code — the environment.

```
┌─────────────────────────────────────────────────┐
│  5. ENTROPY CONTROL — Periodic cleanup           │
├─────────────────────────────────────────────────┤
│  4. WORKFLOW PATTERNS — How to work              │
├─────────────────────────────────────────────────┤
│  3. FEEDBACK LOOPS — Hooks, tests, verification  │
├─────────────────────────────────────────────────┤
│  2. KNOWLEDGE BASE — Docs, decisions, progress   │
├─────────────────────────────────────────────────┤
│  1. SKELETON — Repo structure, CLAUDE.md         │
└─────────────────────────────────────────────────┘
```

**Key insight:** The agent is not the hard part — the harness is. LangChain improved agent accuracy from 52.8% to 66.5% by changing only the harness, not the model. Anthropic's own engineering blog describes subagents as "context firewalls" and recommends declarative intent specs over low-level instructions.

> See [`docs/harness-protocol.md`](docs/harness-protocol.md) — full 5-layer protocol specification.
> See [`docs/capability-map.md`](docs/capability-map.md) — what's built into CC vs what the harness adds. Updated via `/update`; tracks feature migrations over time.

---

## 18. Decision Log (ADR)

Architecture Decision Records capture **why** choices were made. Critical for multi-session work: new sessions read decisions instead of re-debating them.

**Format:** Context → Decision → Rationale → Consequences. One file per decision in `docs/decisions/`.

**/save** writes to both `docs/progress.json` (what) and `docs/decisions/` (why).
**/catchup** reads from both, plus `git log`.

> See [`docs/decisions/`](docs/decisions/) — this repo's own ADRs: why self-reference, why English, why single README.

---

## 19. Patterns for Your Projects

> **Note on self-reference.** Sections 1-18 above describe features that are both documented and demonstrated in this repo — every tool genuinely serves it. This section collects general-purpose patterns that apply to **software projects** but can't be self-referential in a knowledge-management repo. They're here because they make Claude Code significantly more effective.

**Four-file continuity system.** Maintain `CLAUDE.md` + `PRD.md` + `README.md` + `progress.md` as cross-session memory. Start each new session with: *"Read CLAUDE.md, PRD.md, README.md, and progress.md. Confirm understanding of project state."*

**Architecture for AI.** Separate layers (presentation, business logic, data access, integration) into distinct directories. Heuristic: if Claude modifies more than 3-5 files for a single feature, either the feature is poorly scoped or the codebase has too many cross-dependencies.

**MCP workflow examples.** GitHub: "Open a PR with these changes, then check CI status." Playwright: "Write an end-to-end test for the login flow, run it, fix failures." Slack: "Check #deployments for the latest status." Google Docs: "Read the product spec and create PRD.md from it."

**Manual parallel sessions.** Run multiple Claude terminal windows with explicit scope boundaries in each prompt: *"Scope: client/ directory only. Do not touch server/."* Simpler than worktrees — no git setup — at the cost of no automatic conflict prevention.

**Ask Before Edits vs. Automatic Edit.** Default mode shows diffs for approval before modifying files. Automatic mode writes without approval. Use automatic only after plan mode confirms the approach is sound.

---

## Self-Updating

This repo monitors Claude Code evolution at three levels:

1. **GitHub Actions** — weekly cron checks Anthropic changelog, creates Issues
2. **`/update` command** — interactive WebSearch for new features
3. **`updater` agent** — background web monitoring, can run via `/loop`

> See [`docs/changelog.md`](docs/changelog.md) — tracked CC features and changes.
