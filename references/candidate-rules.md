# ⚠️ 已合并到 SKILL.md — 此文件保留仅用于向后兼容

内容已迁移到 SKILL.md > Candidate Rules 章节。请直接使用 SKILL.md。

---

# Candidate Rules

Use this reference when deciding what should become a saved experience.

## Save

Save entries that can change future behavior:

| Signal | Category | Save when |
|--------|----------|-----------|
| Same problem needed 2+ attempts | `multi-step` | The final fix or root cause is reusable |
| User corrected the agent | `preference` or `decision` | The correction reveals a stable preference or project rule |
| Tool, CLI, auth, path, or environment gotcha | `discovery` or `setup` | The detail is likely to recur on this machine or project |
| Architecture or workflow choice | `decision` | The rationale matters for future tradeoffs |
| Better recurring approach found | `discovery` | It prevents repeated wasted work |
| Unfinished work with concrete next step | `action` | The next session can resume from it |

## Do Not Save

Do not save:

- Session transcripts or broad summaries.
- Raw command output unless a short redacted excerpt is essential.
- One-off status updates with no future decision value.
- Obvious facts already encoded in source files.
- Speculation that was not validated.
- Secrets, credentials, private keys, API tokens, or exact environment variable
  values.

## Recommendation Level

Use these labels when presenting candidates:

| Label | Meaning |
|-------|---------|
| `⭐ 推荐保留` | Clear future value and not already captured |
| `可选保留` | Some future value, but lower confidence or narrower scope |
| `不建议保存` | Mention only if the user asked for exhaustive review |

If an item cannot be distilled into a clear one-sentence takeaway, do not mark it as
`⭐ 推荐保留`.

## Promotion

If a lesson applies beyond the current project, recommend promotion instead of
only writing `.opencode/experiences.md`:

| Scope | Destination |
|-------|-------------|
| Current project | `.opencode/experiences.md` |
| All sessions in this repo | `AGENTS.md` |
| Personal global rule | user-level AGENTS/RTK/personal instruction file |
| Tool-specific gotcha | tool reference or setup notes |
