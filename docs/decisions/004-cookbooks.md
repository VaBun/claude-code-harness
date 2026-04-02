# ADR-004: Hook and Rules Cookbooks as Standalone Docs

## Context

The harness-init skill deploys hooks and golden rules to target projects, but the curated patterns lived only inside SKILL.md templates. Community sources (Anthropic docs, DEV Community, GitHub repos) offer 35+ hook patterns and 50+ golden rules. We needed a place to collect, organize, and reference these.

Options considered:
- A) New README sections — keeps single-guide rule but makes README too long
- B) Standalone docs (`docs/hook-cookbook.md`, `docs/rules-cookbook.md`) linked from README
- C) Fold into existing sections — insufficient for 25+ hooks and 30+ rules

## Decision

Option B: standalone cookbook files in `docs/`, linked from README sections §2 (Hooks) and §19 (Patterns for Your Projects). File count limit raised from 30 to 35.

## Rationale

- Cookbooks are reference material, not narrative — they don't belong inline in README
- README links to them, preserving golden rule #2 (single guide)
- Cookbooks serve the main project goal: they are the source of truth for what harness-init deploys
- Both cookbooks are genuinely used by this repo (settings.json uses cookbook hooks, CLAUDE.md uses cookbook rules)
- File count limit raised because new files are genuine additions, not bloat

## Consequences

- harness-init templates now reference cookbook patterns (universal rules section, 6 hooks instead of 3)
- settings.json in this repo expanded from 3 hooks to 6 (dog-fooding)
- CLAUDE.md golden rules expanded from 10 to 13 (universal rules from cookbook)
- Must keep cookbooks current when /update finds new hook events or community patterns
