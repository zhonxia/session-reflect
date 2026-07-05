---
name: session-reflect
description: >
  Extract durable lessons from an opencode/Codex conversation and save only
  user-approved insights to .opencode/experiences.md. Use when the user asks to
  summarize session experience, reflect on a session, extract lessons learned,
  save memory/knowledge, 提炼经验, 总结会话, 保存记忆, or review what should carry
  into future sessions. Do not use for ordinary history lookup, simple file
  search, or summaries that do not need persistent experience records.
---

# Session Reflect

Extract structured, actionable experience from the current conversation and
persist selected items for future sessions.

## Core Rules

- Never write before user approval. Present candidate entries first and wait for
  the user's selection or edits.
- Never save secrets: passwords, API keys, tokens, credentials, private keys, or
  sensitive personal data.
- Treat `.opencode/experiences.md` as the persistent store.
- Resolve bundled resources from the directory that contains this `SKILL.md`
  (`<skill-dir>`). In this repository, `<skill-dir>` is
  `skills/session-reflect/`.
- Keep entries reusable. Capture the lesson, not a transcript.

## Workflow

1. **Scan** the current conversation for reusable experience:
   multi-step resolutions, key decisions, user preferences, useful discoveries,
   personal setup facts, and action items.
2. **Review history** (when useful):
   `python3 <skill-dir>/scripts/analyze_history.py --limit 10`
3. **Cross-check** existing experiences and mark duplicates:
   `python3 <skill-dir>/scripts/manage_experience.py read`
4. **Verify** each candidate against the Candidate Rules below. **Every candidate
   must pass this check** — discard any that violate "Do Not Save" rules.
5. **Format** candidates using the Output Format template below.
6. After the user chooses entries, **append** each selected item with:
   `python3 <skill-dir>/scripts/manage_experience.py append --entry '<json>' --project '<project-name>'`
7. **Validate** after writing:
   `python3 <skill-dir>/scripts/manage_experience.py validate`

---

## Candidate Rules

Use these rules to decide what should become a saved experience.

### ❌ Do Not Save (check first — reject any that match)

- Session transcripts or broad summaries.
- Raw command output unless a short redacted excerpt is essential.
- One-off status updates with no future decision value.
- Obvious facts already encoded in source files (AGENTS.md, opencode.json, README, etc.).
- Facts that can be read directly from project source files.
- Speculation that was not validated.
- Secrets, credentials, private keys, API tokens, or exact environment variable values.

### ✅ Save

Save entries that can change future behavior:

| Signal | Save when |
|--------|-----------|
| Same problem needed 2+ attempts | The final fix or root cause is reusable |
| User corrected the agent | The correction reveals a stable preference or project rule |
| Tool, CLI, auth, path, or environment gotcha | The detail is likely to recur on this machine or project |
| Architecture or workflow choice | The rationale matters for future tradeoffs |
| Better recurring approach found | It prevents repeated wasted work |
| Unfinished work with concrete next step | The next session can resume from it |

### Recommendation Level

| Label | Meaning |
|-------|---------|
| ⭐ 推荐保留 | Clear future value and not already captured |
| 可选保留 | Some future value, but lower confidence or narrower scope |
| 不建议保存 | Mention only if the user asked for exhaustive review |

If an item cannot be distilled into a clear takeaway with all three fields (problem/insight/apply), do not mark it as ⭐.

### Promotion

If a lesson applies beyond the current project, promote instead of only saving to `.opencode/experiences.md`:

| Scope | Destination |
|-------|-------------|
| Current project | `.opencode/experiences.md` |
| All sessions in this repo | `AGENTS.md` |
| Personal global rule | User-level AGENTS/RTK/personal instruction file |
| Tool-specific gotcha | Tool reference or setup notes |

---

## Output Format

### Review Layout

- Count only new, non-duplicate items in the title.
- Group entries by category.
- Mark existing or near-duplicate entries with `✓ 已收录`.
- Mark high-value new entries with `⭐ 推荐保留`; use `可选保留` for lower-confidence items.
- End by asking the user which entries to keep: `编号 / all / none / 修改措辞`.

### Category Headers

| Header | Use for |
|--------|---------|
| `🛠 多轮攻坚` | Problems solved after multiple attempts |
| `💡 决策记录` | Architecture, tool, or process decisions |
| `💡 实用发现` | Commands, libraries, shortcuts, useful facts |
| `🎨 用户偏好` | Style, naming, workflow, and formatting preferences |
| `🔧 个人环境` | Local setup, shell, editor, paths, installed tools |
| `📋 待办提醒` | Follow-ups and unfinished work |

### Template

```text
📌 本次会话经验提炼（N项）

🛠 多轮攻坚 ─────────────────

  1. 标题

     问题：一句话
     经验：一句话
     适用：一句话
     关键词：tag1, tag2

     ⭐ 推荐保留

💡 实用发现 ─────────────────

  2. 标题

     问题：一句话
     经验：一句话
     适用：一句话

     ✓ 已收录

────────────────────────────────────

保留哪些？输入编号(如 1,2) / all / none，可直接修改措辞
```

---

## Entry Format

Each saved entry uses this structure:

```markdown
### 标题
- **问题**：场景或问题描述（一句话）
- **经验**：核心教训或发现（一句话）
- **适用**：什么时候会再次有用（一句话）
- **关键词**：tag1, tag2, tag3
```

### Field Descriptions

| Field | Purpose | Required |
|-------|---------|----------|
| **问题** | What happened — the scenario, doubt, or problem | Yes |
| **经验** | The key lesson — what was discovered, decided, or learned | Yes |
| **适用** | When this knowledge helps again — future scenarios | Yes |
| **关键词** | Search tags for retrieval: language, tool, concept | Recommended |

### JSON Format (for append script)

```json
{
  "title": "GitHub Push SSH 配置",
  "problem": "首次推送时 SSH key 未配置，git push 被拒绝",
  "insight": "改用 HTTPS remote URL 可绕过 SSH 验证",
  "apply": "新机器首次配置 GitHub 时",
  "keywords": ["git", "github", "ssh"]
}
```

### File Format

`.opencode/experiences.md` uses markdown with reverse chronological order:

```markdown
# 经验记录

项目：项目名（可选）

## YYYY-MM-DD

### 标题
- **问题**：描述
- **经验**：描述
- **适用**：描述
- **关键词**：tag1, tag2
```

---

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
- `validate`: check file format and reject sensitive content
