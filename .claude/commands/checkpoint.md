Save current progress and decisions to persistent state files.

Do the following:

1. Update docs/progress.json with:
   - current_task: what you're working on right now
   - status: "in_progress" or "completed"
   - completed_steps: what was accomplished this session
   - next_steps: what should happen next
   - blockers: anything preventing progress
   - decisions_made: list of decisions with brief rationale
   - last_updated: current ISO timestamp

2. If any significant decisions were made this session:
   - Create a new file in docs/decisions/ with the next ADR number
   - Use the ADR format: Context → Decision → Rationale → Consequences
   - Only log decisions that future sessions need to know about

3. Commit all changes with message: "checkpoint: [brief summary]"

Do NOT skip the decisions step — comprehension preservation is critical.
