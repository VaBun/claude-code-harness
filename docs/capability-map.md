# Capability Map: Claude Code Built-in vs Harness

> This document tracks which capabilities come from Claude Code natively
> and which are added by the harness. Updated via `/update` command.
> When CC absorbs a harness feature, mark it as "migrated to native."

## Status Legend

- **native** — fully built into Claude Code
- **harness** — added by this project, CC doesn't provide it
- **extended** — CC has basic version, harness overrides/enhances
- **deprecated** — CC absorbed this, harness version no longer needed

---

## Context & Session Management

| Capability | Built-in (CC) | Harness adds | Status |
|---|---|---|---|
| Context reset | `/clear` | — | native |
| Context compression | `/compact` | — | native |
| Context restore after /clear | — | `/catchup` (reads progress.json + decisions/ + git log) | harness |
| Progress persistence | — | `/checkpoint` (writes progress.json + ADR) | harness |
| Reasoning depth | `/effort low\|medium\|high\|max` | — | native |
| Voice input | `/voice` (push-to-talk, 20 languages) | — | native |

## Planning & Review

| Capability | Built-in (CC) | Harness adds | Status |
|---|---|---|---|
| Plan mode | `/plan` (built-in: explore → plan → implement) | `/plan` command (overrides: adds ADR reading, project-specific checks) | extended |
| Code review | — | `/review` command + `reviewer` agent | harness |
| Content audit | — | `/audit` command (link health, freshness) | harness |

## Safety & Guardrails

| Capability | Built-in (CC) | Harness adds | Status |
|---|---|---|---|
| Permission system | `settings.json` allow/deny lists | — | native |
| Auto mode (AI permissions) | AI classifier reviews each action (March 2026, research preview) | — | native |
| Dangerous command blocker | — | PreToolUse hook (`rm -rf`, `git reset --hard`, `git push --force`, `git clean -f`) | harness |
| Pre-commit validation | — | PreToolUse hook (JSON validation before `git commit`) | harness |
| Post-edit hints | — | PostToolUse hook (reminder to run /review) | harness |

## Agents & Orchestration

| Capability | Built-in (CC) | Harness adds | Status |
|---|---|---|---|
| Subagents | Agent tool (up to 10 simultaneous) | `reviewer`, `updater` (project-specific agents) | extended |
| Agent teams | Agent Teams (2-16 coordinated, shared task list + mailbox) | — | native |
| Worktrees | `--worktree` flag, `isolation: worktree` in agent frontmatter | — | native |

## External Integration

| Capability | Built-in (CC) | Harness adds | Status |
|---|---|---|---|
| MCP servers | `claude mcp add`, `.mcp.json` (global/project/local scopes) | — | native |
| MCP elicitation | Servers can request structured input mid-workflow | — | native |
| Plugins | 101+ official plugins (skills + hooks + MCP bundled) | — | native |

## Automation & Monitoring

| Capability | Built-in (CC) | Harness adds | Status |
|---|---|---|---|
| Session-scoped cron | CronCreate tool (5-field cron, local timezone, 3-day expiry) | — | native |
| Recurring commands | `/loop 5m prompt` (session-scoped) | — | native |
| Persistent scheduled tasks | — | GitHub Actions cron (`check-updates.yml`, weekly) | harness |
| Feature monitoring | — | `/update` command + `updater` agent (WebSearch) | harness |

## Knowledge Management

| Capability | Built-in (CC) | Harness adds | Status |
|---|---|---|---|
| Project constitution | CLAUDE.md (auto-read on session start) | — | native |
| Hierarchical context | Subdirectory CLAUDE.md files (child adds, doesn't repeat parent) | — | native |
| Slash commands | `.claude/commands/*.md` mechanism | 6 project-specific commands | extended |
| Skills | `.claude/skills/*/SKILL.md` mechanism | `harness-init` skill (deploys harness to other projects) | extended |
| Architecture decisions | — | `docs/decisions/` (ADR pattern) | harness |
| Golden rules | — | Golden rules section in CLAUDE.md | harness |
| Machine-readable state | — | `docs/progress.json` (current task, completed, next, blockers) | harness |

---

## Summary

| Status | Count | Examples |
|---|---|---|
| native | ~16 | /clear, /compact, /effort, /voice, auto mode, Agent Teams, worktrees, MCP, plugins, cron |
| harness | ~13 | /catchup, /checkpoint, /review, /audit, /update, dangerous cmd blocker, ADR, progress.json, golden rules |
| extended | ~5 | /plan (overridden), commands (6 custom), skills (harness-init), agents (reviewer, updater) |
| deprecated | 0 | — (none yet; will appear as CC evolves) |

---

## Version History

| Date | Change |
|---|---|
| 2026-03 | Initial mapping. CC: ~16 native capabilities. Harness: ~13 additions, ~5 extensions. |
