# ADR-003: README as the Single Guide

## Context
The initial plan included 14 separate guide chapters in docs/guide/, reference cards in docs/reference/, and a cheatsheet. This was deemed over-engineered.

## Decision
README.md is the single guide. No separate docs/guide/ directory. Each README section points to a live working file in .claude/ or docs/.

## Rationale
- Expressive minimalism: pack knowledge densely by folding it into working files, not spreading it across docs.
- The working files ARE the examples. Separate "example" directories duplicate without adding value.
- A single README with 17 sections is scannable. 14 separate files require navigation overhead.
- Inspired by conceptualization theory: README is the "grammar" (rules of combination), .claude/ files are the "alphabet" (primitives). Grammar + alphabet is sufficient — no need for a separate textbook.

## Consequences
- README must stay under ~300 lines to remain scannable.
- Each section is concise (explanation + pointer to live file), not exhaustive.
- Deep reference material (harness protocol) lives in docs/ — README links to it.
- If the repo grows beyond what a single README can cover, we revisit this decision.
