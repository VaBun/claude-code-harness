Review this repository for correctness and internal consistency.

## Part 1: Discover the rules
1. Read CLAUDE.md — extract all golden rules, key commands, module guide
2. Read docs/golden-rules.md (if exists) — extract additional rules
3. Read docs/decisions/ (if exists) — extract active decisions/constraints

## Part 2: Uncommitted changes
4. Run `git diff` and `git diff --cached` to see all changes
5. Check each changed file against the rules discovered in Part 1

## Part 3: Cross-file consistency
6. **CLAUDE.md ↔ file system**: do commands, modules, and structure described in CLAUDE.md match what actually exists?
7. **README ↔ file system**: do all internal links resolve? Do counts, lists, and descriptions match reality?
8. **settings.json ↔ documentation**: do configured hooks and permissions match what docs describe?
9. **docs/ ↔ reality**: for every doc file (progress.json, decisions/, architecture.md, capability-map.md, or whatever exists) — does its content match the current state of the project?

## Part 4: Structural checks
10. All JSON files valid
11. All internal links between files resolve
12. Check every constraint from golden rules that can be verified mechanically (file counts, naming conventions, language requirements, etc.)

## Part 5: Toolchain health
13. **Hooks ↔ installed tools**: for every command referenced in .claude/settings.json hooks, verify the tool is actually available (e.g., `which ruff`, `which mypy`, `which pytest`). Report WARN if a blocking hook depends on a missing tool.
14. **verify.sh ↔ installed tools**: if scripts/verify.sh exists, check that every tool it calls is installed.

Do NOT fix anything — only report.
Format: PASS / WARN / FAIL for each check, grouped by part.
