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

1. **Scan** the current conversation for distillable items:
   Knowledge (facts taught by user or found via search),
   Lessons (what to do), Decisions (why), AntiPatterns (what not to do).
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
| `🧠 Knowledge` | Objective facts about systems, tools, or behaviors |
| `💡 Lesson` | What to do — best practices and actionable methods |
| `⚖️ Decision` | Why something was designed or chosen this way |
| `🚫 AntiPattern` | What not to do — verified dead ends |

### Template

```text
📌 本次会话蒸馏（N项）

🧠 Knowledge ─────────────────

  1. 标题

     类型：Knowledge
     来源：User
     问题：一句话
     经验：事实描述
     适用：复用场景
     触发：keyword1, keyword2
     证据：⭐⭐⭐

     ⭐ 推荐保留

💡 Lesson ─────────────────

  2. 标题

     类型：Lesson
     来源：Experiment
     问题：一句话
     经验：核心方法
     适用：复用场景
     否定：true
     触发：keyword1

     ✓ 已收录

────────────────────────────────────

保留哪些？输入编号(如 1,2) / all / none，可直接修改措辞
```

---

## Entry Format

Each saved entry uses this structure:

```markdown
### 标题
- **类型**：Knowledge | Lesson | Decision | AntiPattern | Resume
- **来源**：User | WebSearch | Experiment | OfficialDocs | Inference（可选）
- **问题**：场景或问题描述（一句话）
- **经验**：事实 / 方法 / 推理 / 不要做
- **适用**：什么时候会再次有用（一句话）
- **否定**：true（可选，标记为"不要再试"）
- **触发**：keyword1, keyword2（可选，用于精准检索）
- **证据**：⭐⭐⭐（可选，可信度标记）
- **关键词**：tag1, tag2, tag3
```

### Type Reference

| Type | Judgment question | Example |
|------|-------------------|---------|
| `Knowledge` | Is this telling the future AI a **fact** about how something works? | opencode CLI uses SQLite, not JSONL |
| `Lesson` | Is this telling the future AI **what to do** in a specific situation? | SSH fails → use HTTPS remote URL |
| `Decision` | Is this explaining **why** something was designed or chosen this way? | AGENTS.md for breadth, Skill for depth |
| `AntiPattern` | Is this telling the future AI **not to do** something? | Don't spread rules across multiple .md files |
| `Resume` | Is this tracking **unfinished work** for next session? | Implement PDF export for report module |

### Field Descriptions

| Field | Purpose | Required |
|-------|---------|----------|
| **类型** | Distillation type (for retrieval and filtering) | Yes |
| **来源** | Where this knowledge came from | Recommended for Knowledge |
| **问题** | What happened — the scenario, doubt, or problem | Yes |
| **经验** | The core fact, method, reasoning, or warning | Yes |
| **适用** | When this helps again — future scenarios | Yes |
| **否定** | Mark true if this is a "don't try this" entry | Optional |
| **触发** | Exact-match keywords for retrieval | Recommended |
| **证据** | Confidence: ⭐ hypothesis / ⭐⭐ observed / ⭐⭐⭐ verified | Recommended |
| **关键词** | Search tags: language, tool, concept | Recommended |

### JSON Format (for append script)

```json
{
  "title": "GitHub Push SSH 配置",
  "kind": "Lesson",
  "source": "Experiment",
  "problem": "首次推送时 SSH key 未配置，git push 被拒绝",
  "insight": "改用 HTTPS remote URL 可绕过 SSH 验证",
  "apply": "新机器首次配置 GitHub 时",
  "trigger": ["permission denied", "push failed"],
  "evidence": "⭐⭐⭐",
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
- **类型**：Knowledge
- **来源**：User
- **问题**：描述
- **经验**：描述
- **适用**：描述
- **触发**：keyword1, keyword2
- **证据**：⭐⭐⭐
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
