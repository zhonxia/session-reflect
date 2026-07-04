# Session Reflect

An opencode skill that analyzes conversation sessions to extract lessons, patterns, and decisions — and persists them for cross-session memory.

## How it works

1. Trigger by saying "总结会话经验" or "reflect session"
2. Skill scans the current conversation for multi-step resolutions, key decisions, preferences, discoveries, and action items
3. Cross-references with `.opencode/experiences.md` to avoid duplicates
4. Presents findings in categorized card-style layout for user selection
5. Saves approved entries to the experiences file

## Cross-session memory

The experiences file at `.opencode/experiences.md` is registered as an opencode reference — in new sessions, Claude automatically knows it exists and reads it when relevant.

## Requirements

- opencode CLI/TUI (stores full session data in SQLite at `~/.local/share/opencode/opencode.db`)
- Python 3

## Files

```
SKILL.md                          # Skill instructions (triggered by description match)
scripts/analyze_history.py        # Reads opencode.db for past session patterns
scripts/manage_experience.py      # Reads/writes/validates experiences.md
references/format.md              # Experiences file format specification
```
