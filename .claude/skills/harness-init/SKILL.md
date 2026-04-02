# Harness Skill

Skill for bringing any project to a "harnessed" state — ready for productive
work with AI coding agents. Works for both greenfield (new project)
and brownfield (existing project).

## When to use

- User asks to "harness this project", "set up project for agent work",
  "prepare scaffolding", "bring project to harnessed state"
- User wants to add CLAUDE.md, golden rules, verify, slash commands
- User mentions "harness protocol", "harness engineering"
- User says "harness update" — update existing harness to latest templates

## Principles

1. **Do no harm** — existing code and configuration are not changed. Harness is added alongside.
2. **Adapt** — file contents are tailored to the specific project (language, framework, tooling).
3. **Don't duplicate** — if there's a Makefile with `make test`, don't reinvent verify.sh. Use what exists.
4. **Incrementality** — for brownfield: create a scaffold that will grow with use.

## Mode Detection

If the user says **"harness init"** → full initialization (Process below).
If the user says **"harness update"** → update mode (Update Process below).

Auto-detect: if `.claude/commands/` already has `plan.md`, `review.md`, `load.md`, `save.md`, `audit.md` — suggest update mode instead of init.

---

## Update Process

Updates an existing harness to the latest command templates without touching user-customized files.

### File ownership model

| Category | Files | Update action |
|----------|-------|---------------|
| **Harness-owned** (generic commands) | `.claude/commands/plan.md`, `review.md`, `load.md`, `save.md`, `audit.md` | Safe to update |
| **User-owned** (customized at init) | `CLAUDE.md`, `.claude/settings.json`, `docs/golden-rules.md`, `docs/architecture.md`, `docs/progress.json` | **Never overwrite** |

### Step U1: Fetch latest templates

```bash
git clone --depth 1 https://github.com/VaBun/claude-code-harness.git /tmp/cc-harness
```

### Step U2: Show what changed

For each harness-owned command file, compare the current version with the new template:

```bash
for cmd in plan.md review.md load.md save.md audit.md; do
  if [ -f ".claude/commands/$cmd" ] && [ -f "/tmp/cc-harness/.claude/skills/harness-init/templates/commands/$cmd" ]; then
    diff -u ".claude/commands/$cmd" "/tmp/cc-harness/.claude/skills/harness-init/templates/commands/$cmd" || true
  fi
done
```

Present the diffs to the user in a clear format:
- **Changed:** files with differences (show the diff)
- **Unchanged:** files identical to latest templates
- **Missing:** template files not yet in the project (new commands added upstream)

### Step U3: Ask for confirmation

Show a summary like:

```
Harness update summary:
  CHANGED:  plan.md (interview-driven planning added)
  CHANGED:  save.md (commit message format updated)
  UNCHANGED: review.md, load.md, audit.md

User-owned files (NOT touched):
  CLAUDE.md, .claude/settings.json, docs/*

Apply updates? [y/n]
```

Wait for user approval before proceeding.

### Step U4: Apply updates

Only copy files the user approved. Then clean up:

```bash
rm -rf /tmp/cc-harness
```

### Step U5: Report new features

Check if the new harness version introduces features the user might want to adopt manually:
- New hook patterns in `.claude/settings.json` template
- New golden rules for their stack
- New sections recommended for CLAUDE.md

Present these as **suggestions**, not automatic changes. Example:

```
New in this version:
  - /plan now interviews you before planning (already updated above)
  - New hook event: PostCompact — consider adding to your settings.json
  - New pattern: .claude/rules/ directory for path-scoped instructions

These are suggestions — apply them manually if relevant to your project.
```

### Step U6: Clean up

```bash
rm -rf /tmp/cc-harness
```

---

## Init Process

### Step 1: Analyze the project

Run the analyzer from the skill directory:

```bash
python3 SKILL_DIR/scripts/analyze.py PROJECT_ROOT
```

The JSON report contains:
- `primary_language`, `framework` — for template customization
- `tooling` — linters, tests, CI
- `existing_harness` — which harness components already exist
- `modules` — module map for the Module Guide
- `is_greenfield` — project type
- `makefile_targets` — available Makefile targets

### Step 2: Determine the plan

Full list of harness components:

```
SKELETON
├── CLAUDE.md                         — project constitution
├── .claude/settings.json             — hooks configuration
└── .claude/commands/                 — slash commands (plan, load, save, review, audit)

KNOWLEDGE BASE
├── docs/architecture.md              — architecture and invariants
├── docs/golden-rules.md              — codified rules
├── docs/features.md                  — feature checklist (greenfield only)
├── docs/progress.json                — current progress
└── docs/decisions/                   — ADR directory

FEEDBACK LOOPS
├── scripts/verify.sh                 — full verification (if no Makefile verify target)
└── hooks in .claude/settings.json    — pre-commit + post-edit
```

**Decision matrix:**

| Component | Already exists | Greenfield | Brownfield |
|-----------|---------------|------------|------------|
| CLAUDE.md | No → create | Full structure | Full structure |
| CLAUDE.md | Yes → augment | — | Add missing sections |
| .claude/commands/ | No → create | All 5 commands | All 5 commands |
| .claude/commands/ | Partial → augment | Missing ones | Missing ones |
| docs/architecture.md | No → create | Minimal scaffold + TODO | Based on module analysis |
| docs/architecture.md | Yes → don't touch | — | — |
| docs/golden-rules.md | No → create | Adapted to stack | Adapted to stack |
| docs/golden-rules.md | Yes → don't touch | — | — |
| docs/features.md | No | Create with checklist | **Do NOT create** |
| docs/progress.json | No → create | Initial state | Initial state |
| scripts/verify.sh | No + no Makefile → create | For the stack | For the stack |
| scripts/verify.sh | No + Makefile verify exists → Do NOT create | Reference in CLAUDE.md | Reference in CLAUDE.md |
| .claude/settings.json | No → create | With hooks | With hooks |

### Step 3: Generate files

**CRITICAL**: Do not generate generic placeholder content.
Every file must be specific to the given project — with real commands,
real modules, real rules for the specific stack.

---

## Template: CLAUDE.md

```markdown
# Project: {project_name}

## Overview
{2-3 sentences. For brownfield: extract from README/package.json/pyproject.toml.
For greenfield: ask the user. If unknown: <!-- TODO: describe your project -->}

## Tech Stack
- Language: {primary_language} {version}
- Framework: {framework}
- Package Manager: {package_manager.manager}
- Tests: {tooling.test_framework}
- Linter: {tooling.linters | join(", ")}
- Type Checker: {tooling.type_checker}
{Only actually detected components. Don't list what's not there.}

## Architecture
{Brief description of modules from analyze.modules}
See docs/architecture.md for details.

## Key Commands
{REAL commands, determined by stack and Makefile:}
- `{test_cmd}` — run tests
- `{lint_cmd}` — linter
- `{verify_cmd}` — full verification (tests + lint + typecheck)
- `{dev_cmd}` — dev server
After ANY code change, run `{verify_cmd}` before committing.

## Golden Rules
{Top 5 rules from golden-rules.md — most important for the agent}
Full list: docs/golden-rules.md

## Current State
See docs/progress.json for current status.
{Greenfield: See docs/features.md for feature checklist.}

## Module Guide
{From analyze.modules:}
- `{mod.path}/` — {description based on module name and contents}
```

**Command mapping — use for {test_cmd} substitution etc.:**

| Stack | test_cmd | lint_cmd | verify_cmd | dev_cmd |
|-------|----------|----------|------------|---------|
| Python + pytest + ruff + mypy | `pytest tests/ -x` | `ruff check .` | `make verify` or `scripts/verify.sh` | `uvicorn main:app --reload` |
| Python + pytest + ruff (no mypy) | `pytest tests/ -x` | `ruff check .` | `ruff check . && pytest -x` | depends |
| TS + vitest + eslint | `npx vitest run` | `npx eslint .` | `scripts/verify.sh` | `npm run dev` |
| TS + jest + eslint | `npx jest` | `npx eslint .` | `scripts/verify.sh` | `npm run dev` |
| Go | `go test ./...` | `golangci-lint run` | `scripts/verify.sh` | `go run cmd/*/main.go` |
| Rust | `cargo test` | `cargo clippy` | `cargo clippy && cargo test` | `cargo run` |
| Ruby + rspec | `bundle exec rspec` | `bundle exec rubocop` | `scripts/verify.sh` | `rails s` |

If there's a Makefile with test/lint/verify targets — prefer `make test`, `make lint`, `make verify`.

---

## Template: docs/architecture.md

```markdown
# Architecture

## System Diagram
{Text diagram of modules and their relationships.
Brownfield: based on analyze.modules.
Greenfield: <!-- TODO: fill in after initial architecture --> }

## Module Boundaries
{For each module — what it does and what it must NOT do:}
- `{mod.path}/` — {purpose}. Does NOT {constraint}.

## Data Flow
{If framework is known:}
{FastAPI: Request → Router → Dependency Injection → Service → Repository → DB}
{Django: Request → URL routing → View → Service → Model/ORM → DB}
{Next.js: Request → Middleware → Route Handler / Server Component → Data Layer}
{Express: Request → Middleware → Controller → Service → DB}
{Go: Request → Router → Handler → Service → Repository → DB}
{If unknown: <!-- TODO: describe data flow --> }

## Invariants (violation = bug)
{Depend on stack and architecture:}
1. {invariant 1 — e.g.: "All mutations through transactions"}
2. {invariant 2 — e.g.: "Authentication only through middleware"}
3. {invariant 3 — e.g.: "No direct DB access from API/handler layer"}
{Minimum 3 invariants. Not generic — specific to this project.}
```

---

## Template: docs/golden-rules.md

Rules MUST be adapted to the specific stack. Each template below includes:
- **Universal rules** (from rules-cookbook.md — apply to every stack)
- **Stack-specific rules** (adapted to the detected language/framework)

### Universal Section (include in ALL stacks)
```markdown
## Universal
- IMPORTANT: Before writing new code, check if the functionality already exists. Search first.
- Write pure functions. Side effects only at boundaries (handlers, CLI entry points).
- Each function does one thing. No boolean flag parameters that change behavior.
- Raise errors explicitly. No silent failures. No bare exception handlers.
- Error messages MUST include context: what failed, with what input, expected vs actual.
- Use structured logging with fields, not string interpolation.
- Install dependencies via project config (pyproject.toml, package.json), not globally.
- NEVER mark a task done without running verification.
- Make every change as simple as possible. Prefer deleting code over adding code.
- Only touch what is necessary. No "while I'm here" improvements.
- When agent makes a mistake → add a rule here. The harness grows monotonically.
```

### Python
```markdown
# Golden Rules

## Universal
{Include universal section above}

## Code Style
- MAX function length: 50 lines. If longer → extract.
- ALL public functions MUST have docstrings with type hints.
- Use pathlib over os.path. Use f-strings over .format().
- NO bare `except:`. Always catch specific exception types.
- Strict typing: no `Any` without justification.

## Architecture
- NO circular imports.
- Shared utilities go to `{utils_path}/`. No hand-rolled helpers in individual modules.
- NO direct DB queries outside repository/service layer.

## Data Handling
- VALIDATE at boundaries using Pydantic models.
- ALL datetime in UTC. Convert to local only in presentation layer.
- NO `dict["key"]` without validation. Use typed models.

## Testing
- Prefer integration tests over unit tests with mocks.
- Tests MUST be independent. No shared mutable state.
- Use factories over fixtures with hardcoded data.

## Git
- Atomic commits. One logical change per commit.
- Descriptive commit messages in imperative mood.
- NEVER commit with failing tests. Run `{verify_cmd}` first.
```

### TypeScript / JavaScript
```markdown
# Golden Rules

## Universal
{Include universal section above}

## Code Style
- MAX function length: 40 lines.
- ALL exports MUST have TypeScript types or JSDoc.
- Use `const` over `let`. Never use `var`.
- NO `any` type. Use `unknown` + type guards.

## Architecture
- NO circular dependencies.
- Shared utilities in `{utils_path}/`. No duplicated helpers.
- Components: presentation only. Business logic in hooks/services.
- NO direct fetch() in components. Use data layer/hooks.

## Data Handling
- VALIDATE external data at API boundaries (zod/joi/yup).
- Handle errors explicitly. No swallowed promises.
- Use ISO 8601 for dates.

## Testing
- Prefer integration tests over unit tests with mocks.
- Every API route → happy path + error test.
- Mock external dependencies, not internal modules.

## Git
- Atomic commits. Run `{verify_cmd}` before committing.
```

### Go
```markdown
# Golden Rules

## Universal
{Include universal section above}

## Code Style
- MAX function length: 50 lines.
- ALL exported functions MUST have godoc comments.
- Always check errors. No `_` for error returns.
- Use table-driven tests.

## Architecture
- Standard layout: cmd/, internal/, pkg/.
- NO import cycles.
- Interfaces at consumer, not provider.

## Testing
- Every exported function → at least one test.
- Use testify for assertions.
- Subtests for parameterized cases.

## Git
- Run `go vet ./... && go test ./...` before committing.
```

### Rust
```markdown
# Golden Rules

## Universal
{Include universal section above}

## Code Style
- MAX function length: 50 lines.
- ALL public items MUST have doc comments (///).
- Use `Result<T, E>` for fallible operations. No `.unwrap()` in non-test code.

## Architecture
- Shallow module tree (max 3 levels).
- Error types per module via thiserror.
- Traits at consumer side.

## Testing
- Every public function → at least one test.
- Integration tests in tests/ directory.

## Git
- Run `cargo clippy && cargo test` before committing.
```

---

## Template: docs/progress.json

```json
{
  "current_task": "Project harness initialization",
  "status": "completed",
  "completed_steps": [
    "Generated CLAUDE.md",
    "Created docs/architecture.md",
    "Created docs/golden-rules.md",
    "Set up .claude/settings.json with hooks",
    "Installed slash commands"
  ],
  "next_steps": [
    "{First real step for the project}"
  ],
  "blockers": [],
  "decisions_made": [],
  "last_updated": "{ISO timestamp}"
}
```

---

## Template: scripts/verify.sh

Create ONLY if there is no Makefile with a verify/check target.

**Python:**
```bash
#!/bin/bash
set -e
echo "=== Type check ===" && {mypy_or_pyright} {src_dir}/ --strict
echo "=== Lint ===" && ruff check {src_dir}/ tests/
echo "=== Tests ===" && pytest tests/ -x --tb=short -q
echo "=== All checks passed ==="
```

**TypeScript:**
```bash
#!/bin/bash
set -e
echo "=== Type check ===" && npx tsc --noEmit
echo "=== Lint ===" && npx eslint {src_dir}/
echo "=== Tests ===" && npx vitest run
echo "=== All checks passed ==="
```

**Go:**
```bash
#!/bin/bash
set -e
echo "=== Vet ===" && go vet ./...
echo "=== Lint ===" && golangci-lint run
echo "=== Tests ===" && go test ./... -short
echo "=== All checks passed ==="
```

**Rust:**
```bash
#!/bin/bash
set -e
echo "=== Clippy ===" && cargo clippy -- -D warnings
echo "=== Tests ===" && cargo test
echo "=== All checks passed ==="
```

After creation: `chmod +x scripts/verify.sh`

---

## Template: .claude/settings.json

```json
{
  "permissions": {
    "allow": [
      "Bash(make *)",
      "Bash(git *)",
      "Bash(cat *)",
      "Bash(ls *)",
      "Bash(find *)",
      "Bash(grep *)",
      "{additional permissions based on stack}"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "{verify_cmd}",
            "blocking": true
          }
        ]
      },
      {
        "matcher": "Bash(rm -rf*)|Bash(git reset --hard*)|Bash(git push --force*)|Bash(git clean -f*)",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'BLOCKED: Dangerous command detected. Use safer alternatives.' >&2 && exit 2",
            "blocking": true
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(echo $TOOL_INPUT | jq -r '.file_path // .path // empty'); case \"$FILE\" in *.env|*.env.*|*credentials*|*.key|*.pem|*secret*) echo \"BLOCKED: $FILE is a protected file. Never write secrets to code.\" >&2 && exit 2;; esac",
            "blocking": true
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Branch: $(git branch --show-current 2>/dev/null)\" && echo \"Last 3 commits:\" && git log --oneline -3 2>/dev/null || true",
            "blocking": false
          }
        ]
      }
    ],
    "PostCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminders after compact: 1) Read CLAUDE.md for golden rules. 2) Check docs/progress.json for current task. 3) Run git status to see uncommitted work.'",
            "blocking": false
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "{lint_fix_cmd} $CLAUDE_FILE_PATHS",
            "blocking": false
          }
        ]
      }
    ]
  }
}
```

**Stack-specific substitutions:**

| Stack | verify_cmd | lint_fix_cmd | additional permissions |
|-------|-----------|-------------|----------------------|
| Python + ruff | `make verify` or `scripts/verify.sh` | `ruff check --fix` | `Bash(python *), Bash(pytest *), Bash(ruff *)` |
| TS + eslint | `scripts/verify.sh` or `npm run verify` | `npx eslint --fix` | `Bash(npm *), Bash(npx *)` |
| TS + biome | `npx biome check` | `npx biome check --fix` | `Bash(npm *), Bash(npx *)` |
| Go | `scripts/verify.sh` | `gofmt -w` | `Bash(go *)` |
| Rust | `cargo clippy && cargo test` | `cargo fmt --` | `Bash(cargo *)` |

---

## Template: Slash commands

Copy all files from `SKILL_DIR/templates/commands/` to the project's `.claude/commands/`:
- `plan.md`, `load.md`, `save.md`, `review.md`, `audit.md`

---

## Step 4: Self-check

After generating all files, go through this checklist:

- [ ] CLAUDE.md contains REAL commands, not `{placeholders}`
- [ ] Golden rules are specific to the stack (Python/TS/Go/...), not generic
- [ ] verify.sh uses real tools found by the analyzer
- [ ] Hooks in settings.json use correct verify and lint commands
- [ ] Module Guide in CLAUDE.md matches the actual project structure
- [ ] No conflicts with existing .pre-commit-config.yaml or similar
- [ ] verify.sh is marked executable (chmod +x)
- [ ] All TODOs are marked for the user

## Step 5: Dependency check

Before the final message, verify that tools referenced in hooks are installed:

```bash
# For each tool in settings.json hooks (ruff, mypy, pytest, etc.):
which <tool> 2>/dev/null || echo "MISSING: <tool>"
```

If any tool is missing, add a **⚠ Missing dependencies** section to the final message listing what needs to be installed (e.g., `pip install ruff mypy pytest`).

## Step 6: Final message

Provide the user with:

1. **List of created files** with brief descriptions
2. **⚠ Missing dependencies** (if any) — tools required by hooks but not yet installed, with install commands
3. **TODOs** — what needs to be filled in manually
4. **Next steps:**
   - Greenfield: "Fill in docs/features.md, run /plan for the first feature"
   - Brownfield: "Review docs/architecture.md, extend golden-rules.md as you work"
5. **Reminder:** "Every time the agent makes a mistake — add a rule to golden-rules.md.
   The harness grows through use."
