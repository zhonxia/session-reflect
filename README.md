# Session Reflect

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Version](https://img.shields.io/badge/version-0.1.0-green)
![OpenCode](https://img.shields.io/badge/opencode-compatible-black)

**Extract lessons from every AI coding session — and never forget them.**

Session Reflect analyzes your opencode conversations, identifies valuable experiences (multi-step fixes, key decisions, personal preferences, useful discoveries), and persists them to a local file. In future sessions, the accumulated experience is automatically available — no more repeating yourself or rediscovering the same solutions.

---

## How It Works

```
┌─────────────────────────────────────────────────────┐
│  1.  Trigger with "总结会话经验" / "reflect session"  │
│  2.  Skill scans your current conversation           │
│  3.  Past session history is analyzed for patterns   │
│  4.  Categorized findings presented for your review  │
│  5.  You choose what to save                         │
│  6.  Experiences written to .opencode/experiences.md  │
│  7.  Available in every new session (auto)           │
└─────────────────────────────────────────────────────┘
```

### Categories of Experience

| Category | What it captures |
|----------|------------------|
| 🛠 Multi-step Resolutions | Problems that took 2+ attempts and their root cause |
| 💡 Key Decisions | Architecture/tech choices with rationale |
| 💡 Useful Discoveries | Commands, shortcuts, libraries, tricks |
| 🎨 User Preferences | Coding style, naming conventions, tool preferences |
| 🔧 Personal Setup | Terminal config, env vars, editor choice, aliases |
| 📋 Action Items | Follow-ups and unfinished business |

---

## Installation

### Prerequisites

- **opencode** CLI/TUI (stores full session data in SQLite at `~/.local/share/opencode/opencode.db`)
- **Python 3** (for analysis scripts)

### Install with clawhub

```bash
npx clawhub install session-reflect
```

### Manual Install

```bash
# Clone the repository
git clone https://github.com/zhonxia/session-reflect.git

# Copy to your opencode skills directory
cp -r session-reflect ~/.config/opencode/skills/session-reflect
```

### Enable Cross-Session Memory

```bash
# Create opencode.json in your project root:
{
  "references": {
    "experiences": {
      "path": ".opencode/experiences.md",
      "description": "Past session experiences, lessons learned, user preferences, and key decisions."
    }
  }
}

# Create AGENTS.md with:
echo "在回答之前，先检查 .opencode/experiences.md 中是否有与当前问题相关的历史经验记录。" >> AGENTS.md
```

---

## Usage

### Reflect on the Current Session

Simply say to opencode:

```
总结这次会话的经验
```
or
```
reflect session
```
or
```
提炼经验
```

### Review Saved Experiences

```bash
# Read all saved experiences
cat .opencode/experiences.md
```

### Example Flow

```
You:  总结这次会话的经验

Claude: 📌 本次会话经验提炼（2项）

        🛠 多轮攻坚 ──────────────

          1. Docker 构建缓存
             ARG 顺序导致缓存未命中
             ⭐ 推荐保留

        💡 实用发现 ──────────────

          2. GitHub push SSH key 未配置
             改用 HTTPS 成功推送

        ─────────────────────────────
        保留哪些？(编号 / all / none)

You:  1

Claude: ✓ 已保存到 .opencode/experiences.md
```

---

## Cross-Session Memory Architecture

The skill uses a two-layer strategy to make sure experiences are actually used:

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| **AGENTS.md** | Mandatory rule in project root | Forces Claude to check experiences before every answer |
| **opencode.json References** | Registered reference with description | Lets Claude know the file exists and when it's relevant |
| **session-reflect skill** | On-demand analysis workflow | Produces and persists new experiences |

These three layers form a closed loop: **produce → persist → consume**.

> No passwords, API keys, or credentials are ever extracted or saved.
> The experiences file is plain markdown — treat it like code.

---

## Project Structure

```
session-reflect/
├── SKILL.md                        # Skill instructions (auto-triggered)
├── README.md                       # This file
├── .gitignore
├── scripts/
│   ├── analyze_history.py          # Reads opencode.db for past session patterns
│   └── manage_experience.py        # Reads/writes/validates experiences.md
└── references/
    └── format.md                   # Experiences file format specification
```

---

## Requirements

- **opencode** ≥ 1.0 (CLI/TUI recommended)
- Python 3.6+
- SQLite (bundled with Python)

---

## License

Apache 2.0
