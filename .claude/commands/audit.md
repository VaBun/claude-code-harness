Audit this repository for content freshness and structural health.

Check the following:

1. **Content freshness**:
   - Read docs/changelog.md — when was the last update?
   - Are there Claude Code features not yet covered in README.md?
   - Are any sections referencing deprecated features?

2. **Link health**:
   - Check all internal links between files (README → .claude/*, docs/*)
   - Verify referenced files actually exist

3. **Self-reference integrity**:
   - Does every file in .claude/ genuinely serve THIS repo?
   - Does every README section point to a live file?
   - Are CLAUDE.md golden rules still accurate?

4. **Structural health**:
   - Total file count (check limit in CLAUDE.md golden rules)
   - All JSON files valid
   - docs/progress.json up to date?
   - Any ADRs that contradict current reality?

5. **Golden rules compliance**:
   - Read CLAUDE.md golden rules
   - Scan for violations across the repo

Report findings. Do NOT fix anything — only report.
Format: PASS / WARN / FAIL for each check.
