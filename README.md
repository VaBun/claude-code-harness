# Claude Code Tips

A living knowledge system for Claude Code best practices. Every file in this repository is a working example of what it describes. The repo monitors new features, curates content quality, and deploys knowledge to other projects.

**Three ways to use this repo:**
1. **Learn** — read this guide, explore the live files it points to
2. **Deploy** — install the `harness-init` skill to bootstrap any project
3. **Contribute** — run `/catchup`, pick a task from `docs/progress.json`

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

**What to include:** build/test/lint commands, architectural constraints, naming conventions, what NOT to do.
**What to skip:** standard language conventions, things linters catch, file-by-file descriptions.

**Hierarchy:** root `CLAUDE.md` for global context. Subdirectory `CLAUDE.md` files for module-specific rules. Child files don't repeat parent — they add specifics.

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
| `ConfigChange` | Settings file modified | Yes |
| `FileChanged` / `CwdChanged` | Environment changes | No |

**Hook types:** `command` (shell), `prompt` (single-turn Claude eval), `agent` (multi-turn subagent), `http` (POST to endpoint).

**Matcher patterns:** `Edit|Write`, `Bash(git commit*)`, `mcp__github__*`.

**Essential hook: Dangerous Command Blocker.** PreToolUse intercepts `rm -rf`, `git reset --hard`, `git push --force`. Takes 2 minutes to set up, prevents catastrophic accidents.

> See [`.claude/settings.json`](.claude/settings.json) — this repo's hooks: JSON validation pre-commit, dangerous command blocker, post-edit reminder.

---

## 3. Commands — Slash Commands

Markdown files in `.claude/commands/` invoked via `/command-name`. Each file is a natural-language prompt with optional `$ARGUMENTS` placeholder.

```
.claude/commands/plan.md      → /plan add MCP section
.claude/commands/review.md    → /review
```

**Scopes:** project (`.claude/commands/`) or user (`~/.claude/commands/`).

> See [`.claude/commands/`](.claude/commands/) — 6 commands: `/plan`, `/review`, `/catchup`, `/checkpoint`, `/audit`, `/update`. Each serves a real workflow in this repo.

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

Custom agents with isolated context windows, restricted tools, and specific models. Up to 10 simultaneous per session.

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

---

## 8. Plugins

101+ official plugins bundling skills, hooks, and MCP servers into installable units. Browse and install via the plugin ecosystem.

**Notable:** Firecrawl (web data), Context 7 (APIs), Playwright (testing).

---

## 9. Scheduled Tasks

Three approaches to recurring automation:

| Method | Scope | Min interval | Requires |
|--------|-------|-------------|----------|
| `/loop` | Session | 1 minute | CLI open |
| Desktop Tasks | Local | 1 minute | Desktop app |
| GitHub Actions | Repository | N/A (cron) | GitHub repo |

**`/loop`** example: `/loop 5m check if deployment finished`

**CronCreate** tool: schedule prompts directly in conversation. Standard 5-field cron, local timezone. Auto-expires after 3 days.

> See [`.github/workflows/check-updates.yml`](.github/workflows/check-updates.yml) — weekly cron that checks Anthropic's changelog and creates Issues for new features.

---

## 10. Worktrees — Parallel Work

Git worktrees give each agent an isolated copy of the repo. No file conflicts.

```bash
claude --worktree feature-auth    # Terminal 1
claude --worktree bugfix-db       # Terminal 2 (parallel)
```

**Pattern:** N worktrees → N agents → N PRs → human reviews and merges.

**Subagent integration:** Set `isolation: worktree` in agent frontmatter for automatic worktree creation.

---

## 11. Auto Mode

AI-driven permission decisions (March 2026, research preview). A classifier model reviews each action before execution, detecting risky behavior and prompt injection attempts.

**Recommendation:** Use in sandboxed environments first. The classifier's behavior is not fully transparent — don't trust it with production credentials yet.

---

## 12. Voice Mode

`/voice` activates push-to-talk. Hold spacebar → speak → release to send. 20 languages supported. Free transcription.

---

## 13. /effort — Adaptive Reasoning

`/effort low` (fast/cheap) → `medium` (default) → `high` → `max` (deepest reasoning, Opus only). Higher effort doesn't always help — medium is often optimal for coding.

---

## 14. Context Management

Two strategies for managing the context window:

- **`/clear`** — hard reset. Wipes ALL history. CLAUDE.md auto-reloads. Use between unrelated tasks.
- **`/compact`** — soft compression. Condenses context into summary, preserves essential thread. Use when context is partially relevant.

**Rule of thumb:** if less than 50% of prior context is relevant, `/clear`. Otherwise `/compact`.

**Best practice:** `/clear` after every commit to prevent hallucinations in long sessions.

---

## 15. Workflow Patterns

**Plan → Execute → Review:** Use plan mode for non-trivial tasks. Explore without changes → plan → implement → verify → commit.

**Initializer → Coding Agent:** For new projects. First session creates structure + feature list. Subsequent sessions work one feature at a time.

**Harness Engineering Loop:** Agent makes mistake → add golden rule → encode in hook/test → mistake never happens again. The harness grows monotonically.

**Background Swarm:** N isolated tasks → N branches → N agents → N PRs. Condition: tasks don't touch same files, each is independently verifiable.

**Document & Clear:** After 30+ minutes, `/checkpoint` → `/clear` → new session reads progress.json + decisions/. Prevents context decay.

---

## 16. Harness Engineering — 5 Layers

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

**Key insight:** The agent is not the hard part — the harness is. LangChain improved agent accuracy from 52.8% to 66.5% by changing only the harness, not the model.

> See [`docs/harness-protocol.md`](docs/harness-protocol.md) — full 5-layer protocol specification.
> See [`docs/capability-map.md`](docs/capability-map.md) — what's built into CC vs what the harness adds. Updated via `/update`; tracks feature migrations over time.

---

## 17. Decision Log (ADR)

Architecture Decision Records capture **why** choices were made. Critical for multi-session work: new sessions read decisions instead of re-debating them.

**Format:** Context → Decision → Rationale → Consequences. One file per decision in `docs/decisions/`.

**/checkpoint** writes to both `docs/progress.json` (what) and `docs/decisions/` (why).
**/catchup** reads from both, plus `git log`.

> See [`docs/decisions/`](docs/decisions/) — this repo's own ADRs: why self-reference, why English, why single README.

---

## Quick Start: Deploy Harness to Your Project

```bash
# Install the harness-init skill (once)
cp -r /path/to/claude-code-tips/.claude/skills/harness-init/ ~/.claude/skills/harness-init/

# In any project, open Claude Code and say:
# "harness init"
#
# It will:
# 1. Analyze your project (language, framework, tooling)
# 2. Generate CLAUDE.md with real commands and module guide
# 3. Create .claude/settings.json with hooks for your stack
# 4. Install 5 generic slash commands (plan, review, catchup, checkpoint, audit)
# 5. Create docs/golden-rules.md adapted to your tech stack
# 6. Create docs/architecture.md from your actual module structure
# 7. Set up docs/progress.json for state tracking
```

This is `/init` taken to its full potential — from a single CLAUDE.md to a complete Level 2 harness.

---

## Self-Updating

This repo monitors Claude Code evolution at three levels:

1. **GitHub Actions** — weekly cron checks Anthropic changelog, creates Issues
2. **`/update` command** — interactive WebSearch for new features
3. **`updater` agent** — background web monitoring, can run via `/loop`

> See [`docs/changelog.md`](docs/changelog.md) — tracked CC features and changes.
