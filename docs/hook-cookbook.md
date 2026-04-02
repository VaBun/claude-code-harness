# Hook Cookbook

> Copy-paste hook patterns for `.claude/settings.json`. Organized by category.
> Each hook includes: JSON config, explanation, applicable stacks.
> See also: [Hooks section in README](../README.md#2-hooks--deterministic-guardrails)

---

## How Hooks Work — Quick Reference

```
Event flow:    PreToolUse → [tool runs] → PostToolUse
               SessionStart → [session active] → Stop
               UserPromptSubmit → [Claude processes]

Exit codes:    0 = allow (stdout added to context)
               2 = block (stderr sent to Claude as feedback)
               other = allow but log stderr

Hook types:    command | prompt | agent | http
```

**Key fields:**
- `matcher` — filters by tool name: `"Bash(git commit*)"`, `"Write|Edit"`, `"mcp__github__*"`
- `if` — filters by tool name + arguments (more efficient, hook process doesn't spawn if no match)
- `blocking` — if true, exit 2 prevents the action
- `async` — if true, hook runs in background without blocking

---

## 1. Safety & Protection

### 1.1 Dangerous Command Blocker

The most important hook. 2 minutes to set up, prevents catastrophic accidents.

```json
{
  "matcher": "Bash(rm -rf*)|Bash(git reset --hard*)|Bash(git push --force*)|Bash(git clean -f*)",
  "hooks": [{
    "type": "command",
    "command": "echo 'BLOCKED: Dangerous command detected. Use safer alternatives.' >&2 && exit 2",
    "blocking": true
  }]
}
```
**Event:** PreToolUse | **Stacks:** all

### 1.2 Protected Files

Block writes to sensitive files. Claude gets feedback and finds alternatives.

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "FILE=$(echo $TOOL_INPUT | jq -r '.file_path // .path // empty'); case \"$FILE\" in *.env|*.env.*|*credentials*|*.key|*.pem|*secret*|*.p12) echo \"BLOCKED: $FILE is a protected file. Never write secrets to code.\" >&2 && exit 2;; */package-lock.json|*/yarn.lock|*/pnpm-lock.yaml|*/Cargo.lock|*/poetry.lock|*/go.sum) echo \"BLOCKED: $FILE is a lockfile. Run the package manager instead.\" >&2 && exit 2;; esac",
    "blocking": true
  }]
}
```
**Event:** PreToolUse | **Stacks:** all

### 1.3 SQL Injection Prevention

Block raw DROP/TRUNCATE commands in database shells.

```json
{
  "matcher": "Bash(psql*)|Bash(mysql*)|Bash(sqlite3*)",
  "hooks": [{
    "type": "command",
    "command": "CMD=$(echo $TOOL_INPUT | jq -r '.command'); echo \"$CMD\" | grep -iE '(DROP\\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE|DELETE\\s+FROM\\s+\\S+\\s*$)' && echo 'BLOCKED: Destructive SQL detected. Use migrations.' >&2 && exit 2 || true",
    "blocking": true
  }]
}
```
**Event:** PreToolUse | **Stacks:** any with database access

### 1.4 Command Audit Log

Log every shell command Claude runs. Useful for post-session review.

```json
{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) $(echo $TOOL_INPUT | jq -r '.command')\" >> .claude/command-audit.log",
    "blocking": false
  }]
}
```
**Event:** PostToolUse | **Stacks:** all

---

## 2. Code Quality

### 2.1 Auto-Format on Edit (Prettier)

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "FILE=$(echo $TOOL_INPUT | jq -r '.file_path // .path // empty'); case \"$FILE\" in *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.md) npx prettier --write \"$FILE\" 2>/dev/null;; esac; true",
    "blocking": false
  }]
}
```
**Event:** PostToolUse | **Stacks:** TypeScript, JavaScript

### 2.2 Auto-Format on Edit (Ruff)

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "FILE=$(echo $TOOL_INPUT | jq -r '.file_path // .path // empty'); case \"$FILE\" in *.py) ruff check --fix --quiet \"$FILE\" && ruff format --quiet \"$FILE\";; esac; true",
    "blocking": false
  }]
}
```
**Event:** PostToolUse | **Stacks:** Python

### 2.3 Auto-Format on Edit (gofmt)

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "FILE=$(echo $TOOL_INPUT | jq -r '.file_path // .path // empty'); case \"$FILE\" in *.go) gofmt -w \"$FILE\";; esac; true",
    "blocking": false
  }]
}
```
**Event:** PostToolUse | **Stacks:** Go

### 2.4 Auto-Format on Edit (cargo fmt)

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "FILE=$(echo $TOOL_INPUT | jq -r '.file_path // .path // empty'); case \"$FILE\" in *.rs) rustfmt \"$FILE\" 2>/dev/null;; esac; true",
    "blocking": false
  }]
}
```
**Event:** PostToolUse | **Stacks:** Rust

### 2.5 Type-Check on Edit (TypeScript)

Run `tsc --noEmit` after editing `.ts` files. Non-blocking — just reports errors.

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "FILE=$(echo $TOOL_INPUT | jq -r '.file_path // .path // empty'); case \"$FILE\" in *.ts|*.tsx) npx tsc --noEmit 2>&1 | head -20;; esac; true",
    "blocking": false,
    "async": true
  }]
}
```
**Event:** PostToolUse | **Stacks:** TypeScript

### 2.6 Pre-Commit Verification Gate

Block commits unless full verification passes. The most valuable quality hook.

```json
{
  "matcher": "Bash(git commit*)",
  "hooks": [{
    "type": "command",
    "command": "make verify || scripts/verify.sh",
    "blocking": true
  }]
}
```
**Event:** PreToolUse | **Stacks:** all (adjust command to your verify tool)

### 2.7 Test Runner on Source Change

Auto-run related tests when source files change. Uses `async` to avoid blocking.

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "FILE=$(echo $TOOL_INPUT | jq -r '.file_path // .path // empty'); case \"$FILE\" in *.py) TEST=\"tests/test_$(basename \"$FILE\")\"; [ -f \"$TEST\" ] && python -m pytest \"$TEST\" -x --tb=short -q 2>&1 | tail -5;; esac; true",
    "blocking": false,
    "async": true
  }]
}
```
**Event:** PostToolUse | **Stacks:** Python (adapt pattern for other languages)

---

## 3. Workflow Automation

### 3.1 Context Re-Injection After /compact

When context is compacted, important reminders are lost. Re-inject them.

```json
{
  "matcher": "compact",
  "hooks": [{
    "type": "command",
    "command": "echo 'Reminders after compact: 1) Read CLAUDE.md for golden rules. 2) Check docs/progress.json for current task. 3) Run git status to see uncommitted work.'",
    "blocking": false
  }]
}
```
**Event:** PostCompact | **Stacks:** all

### 3.2 Git Context on Session Start

Inject current branch and recent work into Claude's context at startup.

```json
{
  "matcher": "startup|resume",
  "hooks": [{
    "type": "command",
    "command": "echo \"Branch: $(git branch --show-current 2>/dev/null || echo 'not a git repo')\" && echo \"Last 3 commits:\" && git log --oneline -3 2>/dev/null || true",
    "blocking": false
  }]
}
```
**Event:** SessionStart | **Stacks:** all git repos

### 3.3 Post-Edit Reminder

Gentle nudge to review before committing. Non-blocking.

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "echo 'Reminder: run /review before committing'",
    "blocking": false
  }]
}
```
**Event:** PostToolUse | **Stacks:** all

### 3.4 Completion Gate (Agent-Based)

When Claude finishes, a subagent checks if all tasks are actually done.

```json
{
  "matcher": "",
  "hooks": [{
    "type": "prompt",
    "prompt": "Check if all tasks described in the conversation are complete. If something is unfinished, respond with {\"decision\": \"block\", \"reason\": \"Unfinished: ...\"}. If all done, respond with {\"decision\": \"allow\"}.",
    "blocking": true
  }]
}
```
**Event:** Stop | **Stacks:** all

> **Warning:** Stop hooks must check `stop_hook_active` from stdin and exit 0 if true, to prevent infinite loops. See Gotchas section.

### 3.5 Direnv Integration

Reload environment variables when changing directories.

```json
{
  "hooks": [{
    "type": "command",
    "command": "command -v direnv >/dev/null && eval \"$(direnv export bash 2>/dev/null)\" && env >> \"$CLAUDE_ENV_FILE\" || true",
    "blocking": false
  }]
}
```
**Event:** CwdChanged | **Stacks:** all (requires direnv)

---

## 4. Notifications

### 4.1 macOS Native Notification

```json
{
  "hooks": [{
    "type": "command",
    "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'",
    "blocking": false
  }]
}
```
**Event:** Notification | **Stacks:** macOS

### 4.2 Linux Native Notification

```json
{
  "hooks": [{
    "type": "command",
    "command": "notify-send 'Claude Code' 'Claude needs your attention'",
    "blocking": false
  }]
}
```
**Event:** Notification | **Stacks:** Linux (requires libnotify)

### 4.3 Sound Alert on Completion

```json
{
  "hooks": [{
    "type": "command",
    "command": "afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || true",
    "blocking": false
  }]
}
```
**Event:** Stop | **Stacks:** macOS / Linux

### 4.4 Slack Webhook on Session End

```json
{
  "hooks": [{
    "type": "http",
    "url": "${SLACK_WEBHOOK_URL}",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": "{\"text\": \"Claude Code session completed.\"}",
    "blocking": false
  }]
}
```
**Event:** Stop | **Stacks:** all (requires `SLACK_WEBHOOK_URL` env var)

---

## 5. Permission Management

### 5.1 Auto-Approve Read Operations

Skip permission prompts for safe read-only tools.

```json
{
  "matcher": "Read|Glob|Grep",
  "hooks": [{
    "type": "command",
    "command": "echo '{\"permissionDecision\": \"allow\"}'",
    "blocking": true
  }]
}
```
**Event:** PreToolUse | **Stacks:** all

### 5.2 Auto-Approve Plan Mode Exit

```json
{
  "matcher": "ExitPlanMode",
  "hooks": [{
    "type": "command",
    "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'",
    "blocking": true
  }]
}
```
**Event:** PermissionRequest | **Stacks:** all

### 5.3 Block Web Access (Offline Mode)

For air-gapped or restricted environments.

```json
{
  "matcher": "WebFetch|WebSearch",
  "hooks": [{
    "type": "command",
    "command": "echo 'BLOCKED: Web access disabled in this project.' >&2 && exit 2",
    "blocking": true
  }]
}
```
**Event:** PreToolUse | **Stacks:** all

---

## 6. MCP-Specific

### 6.1 Log All MCP Tool Calls

```json
{
  "matcher": "mcp__.*",
  "hooks": [{
    "type": "command",
    "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) MCP: $(echo $TOOL_INPUT | jq -r '.tool_name // \"unknown\"')\" >> .claude/mcp-audit.log",
    "blocking": false
  }]
}
```
**Event:** PostToolUse | **Stacks:** all with MCP servers

### 6.2 Rate-Limit MCP Calls

Prevent runaway MCP tool usage (e.g., API quota protection).

```json
{
  "matcher": "mcp__.*",
  "hooks": [{
    "type": "command",
    "command": "LOG=.claude/mcp-audit.log; [ -f \"$LOG\" ] && COUNT=$(awk -v d=\"$(date -u +%Y-%m-%dT%H:%M 2>/dev/null)\" '$0 ~ d' \"$LOG\" | wc -l) && [ \"$COUNT\" -gt 30 ] && echo 'BLOCKED: MCP rate limit (30/min). Wait before retrying.' >&2 && exit 2 || true",
    "blocking": true
  }]
}
```
**Event:** PreToolUse | **Stacks:** all with MCP servers

---

## 7. JSON Validation

### 7.1 Validate JSON Before Commit

```json
{
  "matcher": "Bash(git commit*)",
  "hooks": [{
    "type": "command",
    "command": "python3 -c \"import json, sys, pathlib; [json.loads(f.read_text()) for f in pathlib.Path('.').rglob('*.json') if f.stat().st_size > 0]; print('JSON validation passed')\"",
    "blocking": true
  }]
}
```
**Event:** PreToolUse | **Stacks:** all

### 7.2 Validate YAML Before Commit

```json
{
  "matcher": "Bash(git commit*)",
  "hooks": [{
    "type": "command",
    "command": "python3 -c \"import yaml, pathlib; [yaml.safe_load(f.read_text()) for f in pathlib.Path('.').rglob('*.yml') if f.stat().st_size > 0]; [yaml.safe_load(f.read_text()) for f in pathlib.Path('.').rglob('*.yaml') if f.stat().st_size > 0]; print('YAML validation passed')\"",
    "blocking": true
  }]
}
```
**Event:** PreToolUse | **Stacks:** all with YAML configs

---

## Gotchas & Patterns

### Exit Code Semantics

| Exit code | Effect |
|-----------|--------|
| 0 | Allow. Stdout added to Claude's context (SessionStart, UserPromptSubmit). |
| 2 | Block. Stderr sent to Claude as feedback. JSON output ignored. |
| Other | Allow, but stderr logged. |

### Stop Hook Infinite Loop

Stop hooks that block create loops (Claude stops → hook blocks → Claude retries → hook blocks...). **Always** check `stop_hook_active`:

```bash
# In your Stop hook script:
ACTIVE=$(echo "$1" | jq -r '.stop_hook_active // false')
[ "$ACTIVE" = "true" ] && exit 0
# ... your actual logic ...
```

### Shell Profile Echo Contamination

If `~/.zshrc` or `~/.bashrc` has unconditional `echo` statements, they prepend to hook stdout and corrupt JSON output. Fix:

```bash
# In your shell profile, wrap echoes:
if [[ $- == *i* ]]; then
  echo "Welcome!"  # only in interactive shells
fi
```

### `async: true` for Slow Hooks

PostToolUse hooks that run tests or type-checks can be slow. Use `"async": true` so they run in background:

```json
{
  "type": "command",
  "command": "npm test 2>&1 | tail -5",
  "blocking": false,
  "async": true
}
```

### `if` Field vs `matcher`

`matcher` filters at hook-group level by tool name. `if` filters at handler level by tool name AND arguments — the hook process doesn't even spawn if `if` doesn't match. More efficient for high-frequency events:

```json
{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "if": "Bash(git *)",
    "command": "echo 'Git command detected'",
    "blocking": false
  }]
}
```

### `CLAUDE_ENV_FILE` for Persistent State

Hooks can write environment variables that persist across all Bash calls in a session:

```bash
echo "PROJECT_ROOT=$(pwd)" >> "$CLAUDE_ENV_FILE"
echo "GIT_BRANCH=$(git branch --show-current)" >> "$CLAUDE_ENV_FILE"
```

---

## Recommended Starter Set

For any new project, start with these 4 hooks:

1. **Dangerous Command Blocker** (§1.1) — 2 min, prevents catastrophe
2. **Protected Files** (§1.2) — 2 min, prevents secret leaks
3. **Auto-Format** (§2.1-2.4) — pick your stack's formatter
4. **Pre-Commit Verification** (§2.6) — ensures quality at commit time

Add more as needed. Each hook that catches a real mistake justifies itself.

---

*Sources: [Anthropic Hooks Guide](https://code.claude.com/docs/en/hooks-guide), [DEV Community hooks collection](https://dev.to/lukaszfryc/claude-code-hooks-complete-guide-with-20-ready-to-use-examples-2026-dcg), [claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery), [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code), community practice.*
