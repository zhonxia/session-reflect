---
name: session-reflect
description: >
  Analyze the current opencode conversation session to extract valuable
  lessons, patterns, decisions, and user preferences. Persist selected
  insights to .opencode/experiences.md for cross-session memory.

  Trigger when the user wants to:
  - Reflect on or summarize the current session
  - Extract lessons learned from conversation history
  - Save experience/memory/knowledge from the session
  - Review what was accomplished and what to do next
  - Analyze patterns across past sessions
  - 总结会话、提炼经验、保存记忆、回顾进展

  Do NOT trigger for simple history lookups or file searches.
---

# Session Reflect

Extract structured, actionable experience from opencode conversations and persist it for future sessions.

## Workflow

When triggered, follow these steps in order:

### 1. Scan Current Session

Analyze the ongoing conversation for these categories:

| Category | What to look for |
|----------|------------------|
| **Multi-step Resolutions** | Problems that took 2+ attempts. Note: what was tried, what failed, what finally worked |
| **Key Decisions** | Architecture/tech/library choices with rationale ("chose X over Y because Z") |
| **User Preferences** | Recurring style: code conventions, naming, tools, workflows, formatting |
| **Useful Discoveries** | Commands, shortcuts, libraries, tricks that were new or noteworthy |
| **Action Items** | Unfinished business, follow-ups, things to resume next session |

### 2. Read Supplemental History

Use `scripts/analyze_history.py` to get structured data from past sessions:

```bash
python3 scripts/analyze_history.py --limit 10
```

Look for:
- Recurring topics or problem domains
- Repeated tool usage patterns
- Whether similar issues appeared before
- Session cost/token patterns that signal complexity

### 3. Cross-Reference Existing Experiences

Read `.opencode/experiences.md` if it exists. For each candidate entry,
check the existing entries for matches. Mark duplicates as `已有记录（不重复）`.

### 4. Present Findings to User

Format findings using card-style layout grouped by category.
Use emoji category headers with horizontal separators.
Mark duplicate entries inline.

**Formatting rules (strict):**
- Each category block: `🛠 类别 ─────────` on its own line, always followed by a blank line
- Each entry: numbered, title on its own line, content indented below, always separated by blank lines
- Duplicates: same structure but mark `已有记录（不重复）` on the content line
- Footer separator: `───` on its own line, then prompt on next line
- Count at top: count only new (non-duplicate) items

Example output:

```
📌 本次会话经验提炼（2项）

🛠 多轮攻坚 ─────────────────

  1. Docker 构建缓存

     ARG 顺序导致缓存未命中，将不变 ARG 放 Dockerfile 顶部

     ⭐ 推荐保留

💡 决策记录 ─────────────────

  2. 选择 Vitest

     因项目使用 ESM，Vitest 原生支持，无需额外配置

💡 实用发现 ─────────────────

  3. `gh pr diff`

     快速查看 PR 变更，比浏览器方便
     已有记录（不重复）

────────────────────────────────────

保留哪些？输入编号(如 1,2) / all / none，可直接修改措辞
```

### 5. Save Selected Items

For each approved entry, use the helper script:

```bash
python3 scripts/manage_experience.py append \
  --entry '{"category":"multi-step","title":"Docker 构建缓存","content":"ARG 顺序导致缓存未命中，不变 ARG 放顶部","tags":["docker","build"]}' \
  --project "$(basename $(pwd))"
```

Always confirm the entry was saved before continuing.

## Scripts

### `scripts/analyze_history.py`
Reads `opencode.db` (SQLite) from `~/.local/share/opencode/` and outputs structured session summaries.
- `--limit N`: last N sessions (default 5)
- `--session ID`: specific session
- `--json`: machine-readable output

### `scripts/manage_experience.py`
Reads, appends, and validates `.opencode/experiences.md`.
- `read`: dump existing entries as JSON
- `append --entry '...'`: add a new entry
- `validate`: check file format

## References

See `references/format.md` for the experiences file format specification, category labels, and conventions.

## Notes

- This skill works best with the opencode CLI/TUI (which stores full session data in `opencode.db`). The desktop app stores only prompt history in JSONL format.
- Always present findings for user approval before writing. Never auto-append entries.
- For the current session analysis, Claude already has the full conversation in context — no file reading needed for step 1.
