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

## Design Philosophy

The skill uses a two-layer context injection strategy to ensure experiences
are actually utilized in new sessions:

**Layer 1 — AGENTS.md (active check)**
A mandatory rule in the project's `AGENTS.md`:
```
在回答之前，先检查 .opencode/experiences.md 中是否有与当前问题相关的历史经验记录。
```
This forces Claude to check the experiences file before every answer.
It applies to all sessions regardless of skill triggers.

**Layer 2 — opencode.json References (passive awareness)**
The experiences file is registered as an opencode reference with a description:
```json
"references": {
  "experiences": {
    "path": ".opencode/experiences.md",
    "description": "Past session experiences, lessons learned, user preferences, and key decisions."
  }
}
```
Claude knows the file exists and its purpose, and reads it when it judges the
topic relevant — but does not check it before every reply.

**How they work together:**
- AGENTS.md solves "Claude doesn't know to look" (breadth)
- References solve "Claude knows the file but doesn't always connect it" (precision)
- session-reflect skill solves "how to produce experiences" (source)

All three form a closed loop: **produce (skill) → persist (experiences.md) → consume (AGENTS + References)**

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
| **Personal Setup** | Terminal config, env vars, installed tools, shell preferences, system info, alias, editor choice |
| **Action Items** | Unfinished business, follow-ups, things to resume next session |

**Writing structure for each entry:**
Every entry must contain these four layers — don't just describe what happened:

| Layer | Purpose | Example |
|-------|---------|---------|
| **现象** | What happened (the observable fact) | "README 改成了用户手册风格" |
| **洞察** | Why it matters (the deeper lesson) | "顶级 skill 把 README 当产品 landing page，直接影响采用率" |
| **价值** | When it helps again (future scenarios) | "下次开源项目直接复用这个结构" |
| **行动** | How to apply it (concrete next steps) | "新建项目时复制徽章 + ASCII 流程图 + 安装步骤模板" |

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
check the existing entries for matches. Mark duplicates as `✓ 已收录`.

### 4. Present Findings to User

Format findings using card-style layout grouped by category.
Use emoji category headers with horizontal separators.
Mark duplicate entries inline.

**Category emoji mapping:**
- `🛠` = Multi-step Resolutions
- `💡` = Key Decisions / Useful Discoveries
- `🎨` = User Preferences
- `🔧` = Personal Setup
- `📋` = Action Items

**Formatting rules (strict):**
- Each category block: `🛠 类别 ─────────` on its own line, always followed by a blank line
- Each entry: numbered, title on its own line, content indented below, always separated by blank lines
- Duplicates: same structure but mark `✓ 已收录` on the content line
- Footer separator: `───` on its own line, then prompt on next line
- Count at top: count only new (non-duplicate) items

Example output:

```
📌 本次会话经验提炼（2项）

🛠 多轮攻坚 ─────────────────

  1. Docker 构建缓存失效

     【现象】多次构建缓存未命中，每次都要重新下载依赖
     【洞察】Dockerfile 中 ARG 声明顺序影响缓存键计算，
            不变的部分放在前面可以最大化缓存命中
     【价值】以后写 Dockerfile 都要注意：不变指令放前面，
            变化指令放后面
     【行动】项目 Dockerfile 首部集中声明所有 ARG

     ⭐ 推荐保留

💡 决策记录 ─────────────────

  2. 选择 Vitest

     【现象】从 Jest 切换到 Vitest
     【洞察】项目使用 ESM，Jest 的 ESM 支持不成熟，
            Vitest 原生支持 ESM，零配置
     【价值】新项目如果是 ESM 优先考虑 Vitest 而非 Jest

💡 实用发现 ─────────────────

  3. `gh pr diff`

     快速查看 PR 变更，比浏览器方便
     ✓ 已收录

🔧 个人环境 ─────────────────

  4. 默认编辑器

     系统 $EDITOR 是 neovim，git 也使用 nvim 作为编辑器

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
- **Security: NEVER extract or save passwords, API keys, tokens, or any credentials.** The experiences file is plain markdown and may be committed to git. Use a dedicated password manager (1Password, Bitwarden) or opencode MCP secrets for sensitive data.
