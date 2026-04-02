# Golden Rules Cookbook

> Curated collection of stack-agnostic rules for CLAUDE.md and `docs/golden-rules.md`.
> Each rule includes: the rule, why it matters, when to apply it.
> See also: [Patterns for Your Projects in README](../README.md#19-patterns-for-your-projects)

---

## How to Use This Cookbook

Pick rules that apply to your project. Copy them into your `CLAUDE.md` (top 5-10 most critical) or `docs/golden-rules.md` (full set). Don't use all of them — instruction budget is limited (see Rule 1.1).

Rules are organized by category. Each has:
- **Rule** — the instruction itself (copy-paste ready)
- **Why** — the failure mode it prevents
- **When** — which projects benefit

---

## 1. CLAUDE.md Quality

### 1.1 Instruction Budget

**Rule:** Keep CLAUDE.md under 150 custom instructions. The system prompt already uses ~50 of Claude's ~200 instruction-following budget. As instruction count increases, compliance degrades uniformly.

**Why:** Too many rules means none are followed reliably. A 300-line CLAUDE.md performs worse than a 100-line one.

**When:** Every project. Audit quarterly — for each line, ask: "Would removing this cause Claude to make mistakes?" If no, cut it.

### 1.2 Emphasis for Critical Rules

**Rule:** Use "IMPORTANT:", "YOU MUST", "NEVER" for high-priority rules. Use normal case for guidelines.

**Why:** Claude weighs emphasized instructions more heavily. Without emphasis, critical rules blend with nice-to-haves.

**When:** Reserve for 3-5 rules that, if violated, cause real damage (data loss, security, breaking production).

### 1.3 Compaction Preservation

**Rule:** Add to CLAUDE.md: "When compacting context, always preserve: the current task, all modified files, test commands, and any decisions made this session."

**Why:** `/compact` can lose important details. Explicit preservation instructions survive compaction.

**When:** Any project with sessions longer than 30 minutes.

### 1.4 Progressive Disclosure

**Rule:** Keep CLAUDE.md lean. Store detailed guidance in `docs/` or `.claude/rules/` files. Reference them: "For API conventions, read `docs/api-conventions.md` before modifying `src/api/`."

**Why:** Claude reads everything in context. 500 lines of rules wastes context on irrelevant details. Path-scoped `.claude/rules/*.md` files load on demand.

**When:** Any project where CLAUDE.md exceeds 100 lines. Split domain-specific rules into `.claude/rules/` with `paths:` frontmatter.

---

## 2. Code Quality (Universal)

### 2.1 Pure Functions First

**Rule:** Write pure functions — modify only return values, never inputs or global state. Side effects only at boundaries (API handlers, CLI entry points).

**Why:** Pure functions are easier to test, debug, and reason about. Agents produce fewer bugs with pure functions because inputs and outputs are explicit.

**When:** Every project. Exceptions: UI event handlers, database writes (inherently side-effectful).

### 2.2 Single-Purpose Functions

**Rule:** Each function does one thing. No multi-mode behavior. No boolean flag parameters that change behavior.

**Why:** Flag parameters (e.g., `process(data, is_admin=True)`) create hidden branching. The agent misses edge cases in the less-tested branch.

**When:** Every project.

### 2.3 Check Before Creating

**Rule:** Before writing new code, check if the functionality already exists in the codebase. Search for similar function names, patterns, and utilities.

**Why:** Agents often recreate existing utilities, creating drift between the original and the copy. DRY violations compound.

**When:** Every project, especially large codebases.

### 2.4 Explicit Errors

**Rule:** Always raise errors explicitly. No silent failures. No bare `except:` / `catch {}`. Error messages must include enough context to debug (what failed, with what input, expected vs actual).

**Why:** Silent failures create invisible bugs. The agent can't self-correct if it doesn't see the error.

**When:** Every project. Critical for backend services and data pipelines.

### 2.5 No catch-all Exception Handlers

**Rule:** Catch specific exceptions only. If you must catch broadly, log the full exception and re-raise.

**Why:** Catch-all handlers hide root causes. A `catch (Exception e)` that returns a generic error makes debugging impossible.

**When:** Every project.

### 2.6 Structured Logging

**Rule:** Use structured logging with fields (key-value), not string interpolation. Example: `logger.info("user_created", user_id=id, email=email)` not `logger.info(f"Created user {id} with email {email}")`.

**Why:** Structured logs are searchable and parseable. String interpolation creates inconsistent formats that break log aggregation.

**When:** Any project with log aggregation (most backend services).

### 2.7 Strict Typing

**Rule:** Use strict typing everywhere: function parameters, return types, variables, collections. No `Any` / `unknown` / `object` without justification.

**Why:** Types are documentation that the compiler verifies. The agent follows type signatures to understand interfaces — loose types lead to wrong assumptions.

**When:** TypeScript, Python (with mypy/pyright), Go (inherent), Rust (inherent).

### 2.8 Dependencies via Project Config

**Rule:** Install dependencies in project environments, not globally. Add to project config files (`pyproject.toml`, `package.json`, `Cargo.toml`), not as one-off installs.

**Why:** Global installs create "works on my machine" bugs. The agent can't reproduce your environment.

**When:** Every project.

---

## 3. Architecture

### 3.1 Module Boundaries

**Rule:** Define clear module boundaries. Document what each module does AND what it must NOT do. Example: "API layer does NOT contain business logic. Core layer does NOT know about HTTP."

**Why:** Without explicit boundaries, agents let logic leak across layers. One leaked query in an API handler becomes a pattern.

**When:** Any project with more than one directory/module.

### 3.2 No Circular Dependencies

**Rule:** Module dependency graph must be acyclic. If A imports B, B must not import A (directly or transitively).

**Why:** Circular deps create initialization order bugs and make refactoring impossible. Add a structural test to enforce.

**When:** Every project. Consider adding `tests/test_architecture.py` with import graph validation.

### 3.3 Shared Utilities in One Place

**Rule:** All shared utilities live in `{utils_path}/`. No hand-rolled helpers in individual modules. If you need a utility, check `{utils_path}/` first.

**Why:** Agents love creating local helper functions. Without this rule, you get 5 slightly different `format_date()` implementations.

**When:** Every project.

---

## 4. Testing

### 4.1 Prefer Integration Over Unit Tests

**Rule:** When adding tests, prefer integration tests that exercise real behavior over unit tests with mocks. Spend money on real API calls rather than maintaining fragile mocks.

**Why:** Mock-heavy tests pass when the mock is correct, not when the code is correct. Integration tests catch real failures at boundaries.

**When:** API services, database-backed applications, external service integrations.

### 4.2 Minimum Viable Coverage

**Rule:** Add only the minimum tests needed for the requested change. Don't create exhaustive test suites speculatively.

**Why:** Speculative tests create maintenance burden. The agent writes tests for cases that will never occur.

**When:** Every project. Exceptions: safety-critical code, payment flows, auth.

### 4.3 Independent Tests

**Rule:** Tests must be independent. No shared mutable state between tests. Each test sets up its own state, runs, and tears down.

**Why:** Dependent tests create flaky test suites. Test A passes alone but fails when run after test B.

**When:** Every project.

### 4.4 Respect Existing Test Strategy

**Rule:** Follow the repository's existing testing patterns — structure, naming, assertion style, fixture patterns. Don't introduce a new testing paradigm.

**Why:** Consistency. A mix of testing styles confuses both agents and humans.

**When:** Brownfield projects with existing test suites.

---

## 5. Workflow

### 5.1 Simplicity First (Boris Cherny)

**Rule:** Make every change as simple as possible. Minimize code. Prefer deleting code over adding code. The simplest solution that works is the best solution.

**Why:** From the creator of Claude Code. Complexity compounds. Each unnecessary line is a future bug.

**When:** Every task, every project.

### 5.2 Root Cause Only

**Rule:** Find and fix root causes. No temporary fixes, no symptom suppression. If a fix doesn't address why the bug exists, it's not a fix.

**Why:** Temporary fixes accumulate into permanent technical debt. The agent will build on top of your workaround.

**When:** Every bug fix.

### 5.3 Minimal Scope

**Rule:** Only touch what is necessary for the current task. No side effects, no "while I'm here" improvements, no unrelated cleanups.

**Why:** Unrelated changes create noisy diffs, complicate reviews, and introduce unexpected regressions.

**When:** Every task. If you notice something unrelated, create a separate task.

### 5.4 Plan First for Non-Trivial Tasks

**Rule:** Enter plan mode (Shift+Tab twice) for any task requiring 3+ steps. Explore the codebase, read relevant files, then propose an approach before making changes.

**Why:** Agents that start coding immediately often go in circles. Planning reduces wasted tokens and wrong approaches.

**When:** Any task more complex than a single-file edit.

### 5.5 /clear After Every Commit

**Rule:** Run `/clear` after every commit or after two failed corrections of the same mistake.

**Why:** Long sessions accumulate stale context. After 30+ minutes, Claude starts referencing outdated file states. A fresh session with `/load` is faster than debugging hallucinations.

**When:** Sessions longer than 30 minutes. Mandatory after committing.

### 5.6 Writer/Reviewer Separation

**Rule:** Session A writes code, Session B reviews it in a fresh context. The reviewer won't be biased toward code it just wrote. Variant: Session A writes tests, Session B writes code to pass them.

**Why:** Self-review blindness. An agent reviewing its own work misses the same things it missed while writing.

**When:** Important features, security-sensitive code, public APIs.

### 5.7 Verify Before Marking Done

**Rule:** Never mark a task as complete without running verification. Run the test suite, check the build, verify the feature works.

**Why:** Agents are optimistic. Without verification, "done" means "code written" not "code working."

**When:** Every task.

---

## 6. Session & Context Management

### 6.1 Use /btw for Side Questions

**Rule:** Use `/btw` for quick questions that don't need to stay in context. The answer appears in a dismissible overlay and never enters conversation history.

**Why:** Saves context budget. A quick "what does this function do?" shouldn't consume space for the rest of the session.

**When:** Any time you have a quick question unrelated to the current task.

### 6.2 Subagents for Research

**Rule:** Use subagents for investigation and research so file-reading doesn't consume your main context window.

**Why:** Reading 10 files to understand a system fills the main context with content you'll only reference once. Subagents read, summarize, and return — the main context stays clean.

**When:** Any exploration task: understanding a new module, finding all usages, investigating a bug.

### 6.3 Save/Load Cycle

**Rule:** `/save` → `/clear` → `/load` is the session continuity cycle. Save current state before clearing. Load it back in the next session. Never rely on Claude "remembering" — it can't across `/clear`.

**Why:** The only reliable cross-session memory is files on disk. progress.json + decisions/ + git log give a new session everything it needs.

**When:** Every session that makes progress worth preserving.

---

## 7. Git Discipline

### 7.1 Atomic Commits

**Rule:** One logical change per commit. A feature, a bugfix, a refactor — not all three.

**Why:** Atomic commits are reviewable, revertable, and bisectable. Mixed commits make `git blame` and `git revert` useless.

**When:** Every project.

### 7.2 Never Commit Failing Tests

**Rule:** Run the full test suite before every commit. If tests fail, fix them first.

**Why:** Broken commits block other developers and agents working on the same codebase.

**When:** Every project. Enforce with a pre-commit hook (see Hook Cookbook §2.6).

### 7.3 Commit Messages in Imperative Mood

**Rule:** Write commit messages as commands: "Add password reset endpoint", not "Added" or "Adds". Include WHY if not obvious from the diff.

**Why:** Consistency with git conventions (git's own messages use imperative). The "why" helps future sessions understand intent.

**When:** Every project.

---

## 8. Harness Engineering

### 8.1 Every Mistake Becomes a Rule

**Rule:** When the agent makes a mistake, don't just fix it — add a rule to CLAUDE.md or golden-rules.md. If the mistake is systemic, add a hook or test.

**Why:** Without this loop, the same mistakes recur in every new session. Rules accumulate monotonically — the harness only gets stronger.

**When:** Every time. This is the core harness engineering principle.

### 8.2 JSON for Machine State

**Rule:** Use JSON (not Markdown) for machine-readable state files (progress, feature lists, configs).

**Why:** Agents treat JSON more carefully than Markdown. JSON is perceived as "code" and edited with more precision. Anthropic confirmed this observation.

**When:** Any progress tracking, feature checklists, or machine-readable state.

### 8.3 One Feature at a Time

**Rule:** Work on one feature at a time. Complete it fully (implement → test → verify → commit) before starting the next.

**Why:** Partial implementations accumulate and interact unpredictably. The agent loses track of what's done and what's pending.

**When:** Every feature-building session.

### 8.4 Session Startup Protocol

**Rule:** Every new session starts with: 1) Confirm working directory. 2) Read progress files (progress.json, decisions/). 3) Check git status and recent log. 4) Select highest-priority uncompleted task. 5) Verify fundamentals still work (build, tests).

**Why:** Anthropic's recommended protocol for long-running agents. Prevents starting work on wrong assumptions.

**When:** Every session. Automate with a `/load` command.

---

## Recommended Starter Set

For any new project, start with these 10 rules:

1. **Instruction Budget** (§1.1) — keep CLAUDE.md under 150 lines
2. **Check Before Creating** (§2.3) — don't duplicate existing code
3. **Explicit Errors** (§2.4) — no silent failures
4. **Module Boundaries** (§3.1) — document what modules must NOT do
5. **Simplicity First** (§5.1) — simplest solution wins
6. **Minimal Scope** (§5.3) — don't touch unrelated code
7. **Plan First** (§5.4) — plan before coding for 3+ step tasks
8. **Verify Before Done** (§5.7) — prove it works
9. **Atomic Commits** (§7.1) — one change per commit
10. **Every Mistake Becomes a Rule** (§8.1) — the harness engineering loop

Add more as your project reveals its specific failure modes.

---

*Sources: [Anthropic Best Practices](https://code.claude.com/docs/en/best-practices), [Boris Cherny's Workflow](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/), [Anthropic Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), [Mitchell Hashimoto](https://serenitiesai.com/articles/mitchell-hashimoto-ai-workflow), [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/), [Kirill Markin's Rules](https://kirill-markin.com/articles/claude-code-rules-for-ai/), [HumanLayer CLAUDE.md Guide](https://www.humanlayer.dev/blog/writing-a-good-claude-md), community practice.*
