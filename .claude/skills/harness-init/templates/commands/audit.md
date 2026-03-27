Perform a harness health audit:

1. Read docs/golden-rules.md
2. Scan the codebase for violations of those rules
3. Check if docs/architecture.md reflects the actual module structure
4. Check if docs/features.md status matches reality
5. Check if CLAUDE.md is accurate and up-to-date
6. Look for common entropy signals:
   - Dead code or unused imports
   - Functions > 50 lines
   - Missing tests for recent code
   - Duplicated logic that should be in shared utils

Report all findings. Do NOT fix anything — only report.
Suggest which issues are highest priority to address.
