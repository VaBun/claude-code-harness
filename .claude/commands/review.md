Review all uncommitted changes in this repository.

1. Run `git diff` and `git diff --cached` to see all changes
2. For each changed file, check against CLAUDE.md golden rules:
   - Does every file genuinely serve this repo?
   - Is README the single guide with sections pointing to live files?
   - No placeholder content?
   - File count still under 25?
   - Decisions logged in docs/decisions/?
3. Check for broken internal links between files
4. Verify all JSON files are valid
5. Summarize findings. Do NOT fix anything — only report.

Format: list issues by severity (critical / warning / suggestion).
