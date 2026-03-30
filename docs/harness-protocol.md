# Harness Protocol: Scaffolding for AI Coding Agents

> A protocol for keeping projects in a "ready-to-go" state for AI coding agents.
> Synthesized from OpenAI (Harness Engineering), Anthropic (Effective Harnesses for Long-Running Agents), Mitchell Hashimoto (AGENTS.md + harness engineering), Martin Fowler, and the community. Updated for Claude Code March 2026.

---

## Why This Protocol

The key insight of 2025–2026: **discipline has shifted from code to scaffolding.** The agent can write code. But the scaffolding — the environment in which the agent writes *good* code and doesn't lose context — is designed by humans.

> "Building software still demands discipline, but the discipline shows up more in the scaffolding rather than the code." — OpenAI, Harness Engineering

> "When something failed, the fix was almost never 'try harder.' The question was always: what capability is missing, and how do we make it both legible and enforceable for the agent?" — OpenAI

> "Anytime you find an agent makes a mistake, you take the time to engineer a solution such that the agent never makes that mistake again." — Mitchell Hashimoto

The protocol solves three problems:
1. **Project is always agent-ready** — every new context window starts with full understanding of the situation.
2. **Human retains comprehension** — documentation, progress, and decisions are recorded so both human and agent share the same picture.
3. **Mistakes convert to rules** — every agent error becomes a permanent protective mechanism.

---

## Protocol Architecture

The protocol is organized as **five layers**, from foundational to dynamic:

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
│  1. SKELETON — Repository structure              │
└─────────────────────────────────────────────────┘
```

---

## Layer 1: SKELETON — Repository Structure

The repository is the only reality for the agent. Anything not in the repo does not exist for the agent.

> "From the agent's point of view, anything it can't access in-context while running effectively doesn't exist. Knowledge that lives in Google Docs, chat threads, or people's heads are not accessible to the system." — OpenAI

### Target File Structure

```
project/
├── CLAUDE.md                    # Main context file (project constitution)
├── .claude/
│   ├── settings.json            # Hooks, permissions, environment
│   ├── commands/                # Slash commands
│   │   ├── plan.md              # /plan — plan a feature without coding
│   │   ├── review.md            # /review — review current changes
│   │   ├── load.md              # /load — restore context after /clear
│   │   ├── save.md              # /save — save progress + decisions
│   │   └── audit.md             # /audit — check harness health
│   ├── agents/                  # Custom subagents
│   │   └── reviewer.md          # Read-only code reviewer
│   └── skills/                  # Reusable skills
│       └── ...
├── docs/
│   ├── architecture.md          # Architecture (for human AND agent)
│   ├── decisions/               # Architecture Decision Records
│   │   └── 001-choice-of-db.md
│   ├── progress.json            # Current progress (machine-readable)
│   ├── features.md              # Feature checklist with statuses
│   └── golden-rules.md          # Codified rules for the codebase
├── scripts/
│   ├── verify.sh                # Quick verification (tests + lint + typecheck)
│   └── screenshot.sh            # UI screenshot (if frontend exists)
├── src/                         # Source code
└── tests/                       # Tests
```

### CLAUDE.md: Project Constitution

The most important file. The agent reads it first. Keep it under 200 lines. Include only what the agent cannot infer from code. Structure:

```markdown
# Project: [Name]

## Overview
[2-3 sentences: what it is, why, for whom]

## Tech Stack
- Language: Python 3.12
- Framework: FastAPI
- DB: PostgreSQL + SQLAlchemy
- Tests: pytest

## Architecture
[Brief diagram or link to docs/architecture.md]

## Key Commands
- `make test` — run tests
- `make lint` — linter + typecheck
- `make verify` — full verification
- `make dev` — start dev server

## Golden Rules
1. Always use type hints (no `Any`)
2. No hand-rolled helpers — use shared utils from `src/utils/`
3. Validate data at boundaries — don't guess data structures
4. Every new endpoint must have a test
5. Atomic commits with descriptive messages
[... grows as agent mistakes are discovered]

## Current State
See docs/progress.json for current status.
See docs/features.md for feature checklist.

## Module Guide
- `src/api/` — REST endpoints
- `src/core/` — business logic
- `src/models/` — SQLAlchemy models
- `src/utils/` — shared utilities
- `tests/` — mirrors src/ structure
```

### Principle: Hierarchical Context

```
CLAUDE.md (root)               # Global context
├── src/api/CLAUDE.md          # API layer specifics
├── src/core/CLAUDE.md         # Business logic specifics
└── tests/CLAUDE.md            # Testing conventions
```

Child files don't repeat the root — they add module-specific context.

---

## Layer 2: KNOWLEDGE BASE — Project Docbase

The docbase is a "navigational map" of the project. Not just documentation — a **system optimized for agent navigation**.

> "Documentation is treated as a navigable map rather than a manual." — OpenAI

### docs/architecture.md

Architecture description sufficient for the agent to make local decisions without violating global invariants.

```markdown
# Architecture

## System Diagram
[Text diagram or mermaid diagram]

## Module Boundaries
- API layer does NOT contain business logic
- Core layer does NOT know about HTTP
- Models are pure data, no side-effects

## Data Flow
Request → Router → Handler → Service → Repository → DB

## Invariants (violation = bug)
1. All data mutations through transactions
2. Authentication only through middleware, not in handlers
3. Errors through exception hierarchy, not return codes
```

### docs/features.md

Feature checklist — format inspired by Anthropic's approach (initializer agent creates full list, coding agent works one at a time):

```markdown
# Features

## Auth
- [x] User registration with email/password
- [x] Login with JWT
- [ ] Password reset flow
- [ ] OAuth2 (Google)

## Core
- [x] Create project
- [ ] Invite collaborators
- [ ] Role-based permissions

## API
- [x] REST endpoints for auth
- [ ] WebSocket for real-time updates
```

### docs/progress.json

**Key file for long-running agents.** Allows a new context window to instantly understand the current state.

> Anthropic insight: agents are less likely to "rewrite" JSON files than markdown. JSON is perceived as "code" and treated more respectfully.

```json
{
  "current_task": "Implement password reset flow",
  "status": "in_progress",
  "completed_steps": [
    "Added reset_token field to User model",
    "Created /auth/forgot-password endpoint"
  ],
  "next_steps": [
    "Create /auth/reset-password endpoint",
    "Add email sending via background task",
    "Write tests for both endpoints"
  ],
  "blockers": [],
  "decisions_made": [
    "Reset tokens expire in 1 hour (see ADR-003)",
    "Using background task for email, not synchronous"
  ],
  "last_updated": "2026-02-18T14:30:00Z"
}
```

### docs/decisions/ — Architecture Decision Records

Every significant decision gets its own file. Format:

```markdown
# ADR-001: Choice of PostgreSQL over MongoDB

## Context
We need a database for [reason]. Key requirements: [list].

## Decision
PostgreSQL with SQLAlchemy ORM.

## Rationale
- Relational data model fits our domain
- Strong typing + migrations via Alembic
- Team experience

## Consequences
- Must manage migrations explicitly
- JOIN-heavy queries need attention to N+1
```

ADRs matter not just for the agent but **for the human** — they capture *why* a decision was made, not just *what*.

### docs/golden-rules.md

Mechanical, verifiable rules. Each rule is a codified lesson:

```markdown
# Golden Rules

## Code Style
- MAX function length: 50 lines. If longer → extract.
- NO magic numbers. Use constants from `src/constants.py`.
- ALL public functions MUST have docstrings.

## Architecture
- NO direct DB queries in API handlers. Use service layer.
- NO circular imports. Module dependency: api → core → models.
- SHARED utilities go to `src/utils/`. No hand-rolled helpers.

## Data Handling
- VALIDATE at boundaries (API input, external API responses).
- USE typed SDKs/Pydantic models. No dict["key"] YOLO access.
- ALL datetime in UTC. Convert to local only in presentation.

## Testing
- Every endpoint → at least one happy path + one error test.
- Tests MUST be independent. No shared mutable state.
- Use factories, not fixtures with hardcoded data.

## Git
- Atomic commits. One logical change per commit.
- Descriptive messages: "Add password reset endpoint with 1hr token expiry"
- NEVER commit with failing tests.
```

> "In a human-first workflow, these rules might feel pedantic or constraining. With agents, they become multipliers: once encoded, they apply everywhere at once." — OpenAI

---

## Layer 3: FEEDBACK LOOPS — Hooks, Tests, Verification

Deterministic guardrails around probabilistic agent behavior. Unlike CLAUDE.md instructions (~80% compliance), hooks are 100% deterministic.

### Principle: Block at Commit, Hint at Write

```
                    ┌──────────────┐
                    │  Agent edits │
                    │    files     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Post-edit   │  ← hint hook (non-blocking)
                    │  lint check  │     "Warning: function > 50 lines"
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Agent tries │
                    │  to commit   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Pre-commit  │  ← blocking hook
                    │  verify.sh   │     tests + lint + typecheck
                    └──────┬───────┘
                           │
                   ┌───────┴────────┐
                   │                │
              PASS               FAIL
              commit             agent must fix
              proceeds           before committing
```

> "We intentionally do not use 'block-at-write' hooks. Blocking an agent mid-plan confuses or even 'frustrates' it." — Shrivu Shankar

### scripts/verify.sh

```bash
#!/bin/bash
set -e

echo "=== Running type check ==="
mypy src/ --strict

echo "=== Running linter ==="
ruff check src/ tests/

echo "=== Running tests ==="
pytest tests/ -x --tb=short

echo "=== All checks passed ==="
```

### Hooks Configuration (.claude/settings.json)

The modern format uses nested `hooks` arrays with typed hook objects:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "scripts/verify.sh",
            "blocking": true
          }
        ]
      },
      {
        "matcher": "Bash(rm -rf*)|Bash(git reset --hard*)|Bash(git push --force*)|Bash(git clean -f*)",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'BLOCKED: Dangerous command' >&2 && exit 2",
            "blocking": true
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "ruff check --fix $CLAUDE_FILE_PATHS",
            "blocking": false
          }
        ]
      }
    ]
  }
}
```

**Hook types:** `command` (shell script), `prompt` (single-turn Claude evaluation), `agent` (multi-turn subagent verification), `http` (POST to endpoint).

**Essential hook: Dangerous Command Blocker.** A PreToolUse hook that intercepts `rm -rf`, `git reset --hard`, `git push --force`, and similar destructive commands. Takes 2 minutes to set up, prevents catastrophic accidents. Community standard as of 2026.

### Agent Self-Verification

Hashimoto: the agent needs tools to **verify its own work**.

```markdown
## Verification Tools (in CLAUDE.md)

- `make verify` — full check (tests + lint + typecheck)
- `make test-file FILE=tests/test_auth.py` — run specific test
- `scripts/screenshot.sh` — capture UI screenshot (if frontend)
- `scripts/check-api.sh` — smoke test API endpoints
After ANY code change, run `make verify` before committing.
If screenshot.sh exists, use it to visually verify UI changes.
```

---

## Layer 4: WORKFLOW PATTERNS — How to Work

### Pattern A: Initializer → Coding Agent (Anthropic)

For new projects or major features. Two "types" of agent with different prompts:

**Initializer agent** (first context window):
- Sets up project structure
- Creates features.md with full feature list (all marked `[ ]`)
- Initializes git
- Creates progress.json
- Does NOT write application code

**Coding agent** (all subsequent windows):
- Reads progress.json + features.md + git log
- Takes ONE feature
- Implements → tests → commits → updates progress.json
- Marks feature as `[x]`

> "This incremental approach turned out to be critical to addressing the agent's tendency to do too much at once." — Anthropic

### Pattern B: Plan → Execute → Review (everyday work)

```
Human: "Add password reset flow"
  │
  ▼
Agent (plan mode): Creates plan in docs/plans/password-reset.md
  │
  ▼
Human: Reviews plan, adjustments
  │
  ▼
Agent: Implements step by step (each step → commit → verify)
  │
  ▼
Human: Reviews diffs, merges
```

### Pattern C: Document & Clear (long sessions)

```
[30+ minutes of work, context filling up]
  │
  ▼
Human: "Save current status to docs/progress.json"
  │
  ▼
Agent: Records everything: what's done, what's next, decisions made
  │
  ▼
Human: /clear (or /compact if partial context is still useful)
  │
  ▼
New session: "Read CLAUDE.md, docs/progress.json, docs/decisions/, continue"
```

**Note:** `/clear` is a hard reset (wipes all history). `/compact` condenses context while preserving essential thread. Use `/clear` when less than 50% of context is relevant; `/compact` otherwise.

### Pattern D: Harness Engineering Loop (Hashimoto)

```
Agent makes a mistake
  │
  ├─ Simple mistake (wrong command, wrong API)
  │   └─ → Add rule to CLAUDE.md / golden-rules.md
  │
  └─ Systemic mistake (can't verify its result)
      └─ → Write a verification script/tool
          └─ → Add tool reference to CLAUDE.md
```

> The harness grows incrementally. Every mistake is fuel for improvement.

### Pattern E: Garbage Collection (OpenAI)

Periodic (daily/weekly) background agent runs:

- **Audit agent**: scans codebase for golden-rules violations
- **Docs sync agent**: verifies docs/architecture.md matches actual code
- **Quality grade agent**: scores each module's "cleanliness", opens PR for refactoring

> "We used to spend every Friday (20% of the week) cleaning up 'AI slop.' That didn't scale. Instead, we started encoding golden principles and built a recurring cleanup process." — OpenAI

### Pattern F: Background Swarm (for isolated tasks)

```
Human defines N isolated tasks
  │
  ▼
Each task → separate branch → separate agent (via worktree)
  │
  ├─ Agent 1: Migrate test framework (branch: migrate-tests)
  ├─ Agent 2: Clean up feature flags (branch: cleanup-flags)
  └─ Agent 3: Add API documentation (branch: api-docs)
  │
  ▼
Each agent opens PR → human reviews → merge
```

**Prerequisites:** tasks are **isolated** (don't touch the same files), **verifiable** (clear "done/not done" criteria), **don't require architectural decisions**.

**2026 update:** Claude Code now supports native git worktrees (`--worktree` flag) and Agent Teams (2-16 coordinated agents). For tasks that DO need coordination, use Agent Teams instead of independent swarm.

---

## Layer 5: ENTROPY CONTROL — Fighting Entropy

> "AI-induced code entropy: each agent-generated change subtly degrades the maintainability and correctness of the codebase." — VentureBeat

### The Problem

The agent generates code faster than humans can maintain its quality. Without active measures, entropy grows unboundedly.

### Control Mechanisms

**1. Golden Rules as a living document**
Not written once — amended every time a new category of errors is discovered.

**2. Structural tests (architecture tests)**
Tests that verify structure, not behavior:

```python
# tests/test_architecture.py

def test_no_db_queries_in_api_layer():
    """API handlers must not import from models directly."""
    api_files = get_python_files("src/api/")
    for f in api_files:
        content = f.read_text()
        assert "from src.models" not in content, \
            f"{f} imports models directly. Use service layer."

def test_no_circular_imports():
    """Module dependency must be acyclic."""
    # ... import graph analysis

def test_all_endpoints_have_tests():
    """Every API endpoint must have at least one test."""
    endpoints = extract_endpoints("src/api/")
    test_files = get_python_files("tests/")
    for endpoint in endpoints:
        assert any(endpoint.name in t.read_text() for t in test_files), \
            f"Endpoint {endpoint.name} has no tests"
```

**3. Periodic refactoring agents**
Weekly agent run with prompt:
```
Read docs/golden-rules.md. Scan the codebase for violations.
For each violation, create a minimal PR that fixes it.
Do not change functionality. Only improve structure.
```

**4. Comprehension checkpoints**
Weekly ritual for the human:
- Read git log for the week
- For each new module: "Can I explain what it does and why?"
- If not → `explain` session with agent → update docs/

---

## Bootstrap Protocol

### For a new project (greenfield)

```
1. Create directory structure (skeleton)
2. Write CLAUDE.md with project description and tech stack
3. Create docs/architecture.md with key decisions
4. Create docs/features.md with feature checklist (all [ ])
5. Create docs/golden-rules.md with initial rules
6. Set up scripts/verify.sh
7. Configure hooks in .claude/settings.json
8. First commit: "Initial harness setup"
9. Begin work using Pattern A (Initializer → Coding Agent)
```

### For an existing project (brownfield)

```
1. Add CLAUDE.md to root
   - Project description, stack, key commands
   - Module "map": what lives where
2. Add docs/golden-rules.md
   - Start with 5-10 rules you know from experience
3. Add docs/architecture.md
   - Document current architecture (even if imperfect)
4. Set up verify.sh + hooks in .claude/settings.json
5. Work using Pattern D (Harness Engineering Loop):
   - Every agent mistake → new rule or script
   - Harness grows iteratively
```

**Shortcut:** Install the `harness-init` skill from this repository. It analyzes your project and generates all harness files adapted to your specific tech stack in one command.

---

## Protocol Principles

### 1. Repository is the System of Record
All knowledge lives in the repo. Slack discussions, Notion docs, verbal agreements — don't exist for the agent. If a decision isn't in the repo, it hasn't been made.

### 2. Optimize for Agent Legibility
Code and documentation are optimized primarily for agent navigation. This coincides with optimizing for new developers — if the agent can figure it out, a newcomer can too.

### 3. Enforce Boundaries, Allow Local Autonomy
Strictly control architectural boundaries (modules, dependencies, invariants). Within a module, give the agent freedom. This is the "large platform organization" pattern: centralized boundary management, local autonomy in implementation.

### 4. Human Taste as Continuous Feedback
Human "taste" (style preferences, architectural choices, naming) isn't loaded once — it's continuously fed through reviews, refactoring, and rule updates.

> "Human taste is fed back into the system continuously. Review comments, refactoring PRs, and user-facing bugs are captured as documentation updates or encoded directly into tooling." — OpenAI

### 5. Build to Delete
Models improve. What required complex scaffolding yesterday is solved with a single prompt tomorrow. Don't get attached to harness infrastructure — it should be easy to replace.

> "Capabilities that required complex, hand-coded pipelines in 2024 are now handled by a single context-window prompt in 2026. Developers must build harnesses that allow them to rip out the 'smart' logic they wrote yesterday." — Philipp Schmid

### 6. Every Mistake is Fuel
Every agent error is an opportunity to strengthen the harness. Not "fix and forget" but "fix and prevent forever." The harness grows monotonically.

### 7. Comprehension Over Speed
If you don't understand what the agent did — stop. Project comprehension is an irreversible resource. A lost function can be rewritten in minutes. Lost understanding takes hours to recover.

---

## Protocol Evolution

This protocol is a **living document**. It must evolve with the project and with the tools.

**Daily:**
- Amend golden-rules.md when errors are discovered
- Update progress.json

**Weekly:**
- Run garbage collection agents (or /audit command)
- Comprehension checkpoint for the human
- Review and trim CLAUDE.md (is it growing too large?)

**At project phase changes:**
- Update architecture.md
- Review features.md
- Reassess: which rules are outdated? which need to be added?

---

## Maturity Map

| Level | Description | Indicator |
|-------|------------|-----------|
| 0 — Ad hoc | No harness. Agent works "as it goes" | Frequent doom loops |
| 1 — Basic | CLAUDE.md + verify.sh + git discipline | Agent reliably solves simple tasks |
| 2 — Structured | + docbase + hooks + slash commands | Agent handles complex features, /clear works smoothly |
| 3 — Self-healing | + garbage collection + structural tests | Entropy under control, project doesn't degrade |
| 4 — Orchestrated | + multi-agent patterns + background swarm | Parallel work, human = architect |

Most projects need level 2-3. Level 4 is justified for large products with dedicated teams.

---

## Next Steps

This document is a protocol specification. Building on it:

1. **Claude Code skill** that bootstraps harness for a new project in one command → see the `harness-init` skill in this repository
2. **Slash commands** automating routine operations (plan, load, save, review) → see `.claude/commands/` in this repository
3. **Garbage collection agent** running on schedule → see the `reviewer` and `updater` agents
4. **Self-updating system** that tracks new features → see `.github/workflows/check-updates.yml`

The protocol is intentionally tool-agnostic: it works with Claude Code, Codex, Cursor, Copilot — any agent benefits from well-structured scaffolding.
