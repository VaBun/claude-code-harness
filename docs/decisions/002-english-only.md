# ADR-002: All Content in English

## Context
The repository creator's primary audience includes Russian-speaking developers. The question was whether to write documentation in Russian and code in English, or use English throughout.

## Decision
All content in English — README, docs, CLAUDE.md, commands, agents, skills, settings.

## Rationale
- Files in .claude/ are designed to be copied into other projects. English is universal.
- Claude Code itself operates in English. CLAUDE.md in English is the standard convention.
- Mixed-language repos create friction for international contributors.
- The harness-init skill generates files for any project — they must be language-neutral.

## Consequences
- All documentation, including README.md, is in English.
- The harness-protocol.md was fully translated from the original Russian reference material.
- The repository is accessible to the global Claude Code community.
