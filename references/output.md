# ⚠️ 已合并到 SKILL.md — 此文件保留仅用于向后兼容

内容已迁移到 SKILL.md > Output Format 章节。请直接使用 SKILL.md。

---

# Output Format

Use this reference when presenting candidate experience entries to the user.

## Review Layout

- Count only new, non-duplicate items in the title.
- Group entries by category.
- Mark existing or near-duplicate entries with `✓ 已收录`.
- Mark especially useful new entries with `⭐ 推荐保留`; use `可选保留` for
  lower-confidence items.
- End by asking the user which entries to keep: `编号 / all / none / 修改措辞`.

## Category Headers

| Header | Use for |
|--------|---------|
| `🛠 多轮攻坚` | Problems solved after multiple attempts |
| `💡 决策记录` | Architecture, tool, or process decisions |
| `💡 实用发现` | Commands, libraries, shortcuts, useful facts |
| `🎨 用户偏好` | Style, naming, workflow, and formatting preferences |
| `🔧 个人环境` | Local setup, shell, editor, paths, installed tools |
| `📋 待办提醒` | Follow-ups and unfinished work |

## Template

```text
📌 本次会话经验提炼（N项）

🛠 多轮攻坚 ─────────────────

  1. 标题 — 一句话核心教训

     ⭐ 推荐保留

💡 实用发现 ─────────────────

  2. 标题 — 一句话核心发现
     ✓ 已收录

────────────────────────────────────

保留哪些？输入编号(如 1,2) / all / none，可直接修改措辞
```

Each entry is a single line: `标题 — 一句话`. No field labels. If an entry doesn't have a clear one-sentence takeaway, do not recommend saving it.
