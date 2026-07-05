# ⚠️ 已合并到 SKILL.md — 此文件保留仅用于向后兼容

内容已迁移到 SKILL.md > Entry Format / File Format 章节。请直接使用 SKILL.md。

---

# 经验文件格式规范

`.opencode/experiences.md` 采用 Markdown 格式，按日期倒序组织。

## 文件结构

```markdown
# 经验记录

项目：项目名（可选）

## YYYY-MM-DD
标题 — 一句话总结核心教训

另一个标题 — 对应的核心教训
```

每条经验是单独一行，格式为 `标题 — 一句话`。

## 写入规则

1. 所有新条目必须经用户确认后才能写入
2. 写入前展示完整条目内容给用户确认
3. 按日期分组，同一天的多条记录依次排列
4. 使用脚本 `<skill-dir>/scripts/manage_experience.py append --entry '...'` 写入
5. 写入后运行 `<skill-dir>/scripts/manage_experience.py validate`
6. 写入脚本会拒绝缺少 title/content 的条目、明显敏感内容、近似重复条目

## 候选条目 JSON

写入脚本接收的 `--entry` 是 JSON 字符串：

```json
{
  "title": "Docker 构建缓存",
  "content": "ARG 顺序影响缓存键，不变 ARG 放前可最大化缓存命中"
}
```

`title` 和 `content` 均必需且不可为空。`category` 和 `tags` 字段已废弃，不再使用。
