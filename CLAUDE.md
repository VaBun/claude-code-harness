# Project: claude-code-tips

## Overview
Living knowledge system for Claude Code best practices.
Monitors new features, curates content quality, deploys
knowledge to other projects via the harness-init skill.
Self-referential: every tool in this repo genuinely serves it.

## Key Commands
- `/plan SECTION` — plan a new section (don't write yet)
- `/review` — review uncommitted changes against golden rules
- `/load` — restore context after /clear or new session
- `/save` — save progress to docs/progress.json + log decisions
- `/audit` — check content freshness and link health
- `/update` — search web for new Claude Code features

## Golden Rules
1. Every file must genuinely serve THIS repo — no demo-only files.
2. README.md is the single guide. No separate docs/guide/ directory.
3. Each README section points to a live working file in the repo (except §19 "Patterns for Your Projects" — general-purpose techniques that can't be self-referential).
4. No placeholder content. Every example is real and working.
5. Keep total file count under 30.
6. Log significant decisions in docs/decisions/ using ADR format.
7. When agent makes a mistake → add a golden rule here.
8. Run /save after every major change. Future sessions depend on it.
9. All content in English.
10. Commit messages: imperative mood, reference what changed and why.

## Current State
See docs/progress.json for current task and status.
See docs/decisions/ for why things are the way they are.

## Module Guide
- `.claude/commands/` — slash commands for content management workflows
- `.claude/agents/` — subagents for review and web monitoring
- `.claude/skills/harness-init/` — deploys harness to other projects (the "product")
- `docs/` — reference materials, system state, decision log
- `docs/capability-map.md` — built-in CC vs harness tracking (update via `/update`)
- `docs/decisions/` — architecture decision records (the "why" behind choices)
- `.github/workflows/` — automated monitoring via GitHub Actions
