# ADR-001: Self-Referential Design

## Context
This repository teaches Claude Code best practices. The question arose: should the tools in .claude/ (hooks, commands, agents, skills) be demonstration pieces, or should they genuinely serve the repo itself?

## Decision
Every tool must genuinely serve THIS repository. No demo-only files. The harness-init skill is the only exception — it's a "product" that deploys harness to other projects.

## Rationale
- Demonstration-only tools are dishonest and fragile — they rot because nobody uses them.
- Genuine self-reference creates a feedback loop: improving the tool improves the repo, improving the repo tests the tool.
- Each file can be read three ways (documentation, recipe, working example), creating the "fascination" that makes people return.
- This aligns with the conceptualization theory principle: attractors (self-reference loops) drive deeper engagement than static content.

## Consequences
- Every new tool must pass the test: "Would removing this break a real workflow in this repo?"
- The set of tools is constrained by what a knowledge-management repo actually needs (not what a software project needs).
- The repo's scope was expanded from "tips collection" to "living knowledge system" specifically to create genuine need for all CC tools.
