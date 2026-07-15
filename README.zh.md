# Session Reflect

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Version](https://img.shields.io/badge/version-0.4.0-green)
![OpenCode](https://img.shields.io/badge/opencode-compatible-black)

**从每次 AI 编程会话中提取经验，从此不再忘记。**

Session Reflect 分析你的 opencode 对话，识别有价值的经验（多轮攻坚、关键决策、个人偏好、实用发现），持久化到本地文件。在未来的会话中，这些积累的经验会自动可用——无需重复强调或重新发现同样的解决方案。

---

## 工作原理

```
┌─────────────────────────────────────────────────────┐
│  1.  触发: "总结会话经验" / "reflect session"        │
│  2.  技能扫描当前对话记录                             │
│  3.  分析过往会话的模式与规律                         │
│  4.  分类呈现发现供你审核                             │
│  5.  你选择要保存的内容                               │
│  6.  经验写入 .opencode/experiences.md                │
│  7.  每次新会话自动可用（引用注入）                    │
└─────────────────────────────────────────────────────┘
```

### 经验分类

| 类别 | 捕捉内容 |
|------|---------|
| 🛠 多轮攻坚 | 2+ 次才解决的问题及其根因 |
| 💡 关键决策 | 架构/技术选择及其理由 |
| 💡 实用发现 | 命令、快捷键、库、技巧 |
| 🎨 个人偏好 | 编码风格、命名约定、工具偏好 |
| 🔧 个人配置 | 终端配置、环境变量、编辑器选择、别名 |
| 📋 待办事项 | 后续跟进和未完成事项 |

---

## 安装

### 前置要求

- **opencode** CLI/TUI（将会话数据保存在 `~/.local/share/opencode/opencode.db` 的 SQLite 数据库中）
- **Python 3**（用于分析脚本）

### 通过 clawhub 安装

```bash
npx clawhub install session-reflect
```

### 手动安装

```bash
# 克隆仓库
git clone https://github.com/zhonxia/session-reflect.git

# 复制到 opencode skills 目录
cp -r session-reflect ~/.config/opencode/skills/session-reflect
```

### 启用跨会话记忆

```bash
# 在项目根目录创建 opencode.json：
{
  "references": {
    "experiences": {
      "path": ".opencode/experiences.md",
      "description": "过往会话的经验总结、教训、用户偏好和关键决策。"
    }
  }
}

# 创建 AGENTS.md：
echo "在回答之前，先检查 .opencode/experiences.md 中是否有与当前问题相关的历史经验记录。" >> AGENTS.md
```

---

## 使用方法

### 反思当前会话

直接对 opencode 说：

```
总结这次会话的经验
```
或
```
reflect session
```
或
```
提炼经验
```

### 查看已保存的经验

```bash
# 读取所有保存的经验
cat .opencode/experiences.md
```

### 示例流程

```
你:   总结这次会话的经验

AI:   📌 本次会话经验提炼（2项）

       🛠 多轮攻坚 ──────────────

         1. Docker 构建缓存
            ARG 顺序导致缓存未命中
            ⭐ 推荐保留

       💡 实用发现 ──────────────

         2. GitHub push SSH key 未配置
            改用 HTTPS 成功推送

       ─────────────────────────────
       保留哪些？(编号 / all / none)

你:   1

AI:   ✓ 已保存到 .opencode/experiences.md
```

---

## 跨会话记忆架构

本技能使用双层策略确保经验真正被利用：

| 层 | 机制 | 目的 |
|----|------|------|
| **AGENTS.md** | 项目根目录的强制规则 | 强制 AI 在每次回答前检查经验文件 |
| **opencode.json References** | 注册引用并附带描述 | 让 AI 知道文件存在及何时相关 |
| **session-reflect skill** | 按需分析工作流 | 生成和持久化新经验 |

这三层形成闭环：**产生 → 持久化 → 消费**。

> 不会提取或保存任何密码、API Key 或凭证。
> 经验文件是纯 Markdown — 像对待代码一样对待它。

---

## 项目结构

```
session-reflect/
├── SKILL.md                        # 技能指令（自动触发）
├── README.md                       # 本文档（英文）
├── README.zh.md                    # 本文档（中文）
├── .gitignore
├── scripts/
│   ├── analyze_history.py          # 读取 opencode.db 分析过往模式
│   └── manage_experience.py        # 读写/校验 experiences.md
└── references/
    └── format.md                   # 经验文件格式规范
```

---

## 系统要求

- **opencode** ≥ 1.0（推荐 CLI/TUI）
- Python 3.6+
- SQLite（Python 内置）

---

## 许可证

Apache 2.0
