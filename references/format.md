# 经验文件格式规范

`.opencode/experiences.md` 采用 Markdown 格式，按日期倒序组织。

## 文件结构

```markdown
# 经验记录

项目：项目名（可选）

## YYYY-MM-DD

### [类别标签] 标题  `#标签1 #标签2`
- **内容**：详细的经验描述。

### [类别标签] 标题
- **内容**：描述文本。
- **备注**：附加信息（可选）。
```

## 类别标签

| 标签 | 含义 | 适用场景 |
|------|------|----------|
| `多轮攻坚` | Multi-step Resolution | 多次尝试才解决的问题及其根因 |
| `决策记录` | Key Decision | 架构/技术选型及其理由 |
| `用户偏好` | User Preference | 代码风格、命名规范、工具偏好 |
| `实用发现` | Useful Discovery | 好用的命令、库、模式 |
| `个人环境` | Personal Setup | 终端配置、环境变量、已安装工具、shell 偏好、系统信息 |
| `待办提醒` | Action Item | 下次需要继续做的事情 |

## 标签系统

使用 `#标签名` 添加可搜索标签：

```markdown
### [多轮攻坚] React Hook 顺序问题  `#react #hooks #bug`
- **内容**：Hooks 必须按固定顺序调用，条件分支内不能有 hooks。
```

## 读取方式

当技能被触发时，Claude 应：

1. 先检查 `.opencode/experiences.md` 是否存在
2. 读取文件内容获取已有经验
3. 读取 prompt-history.jsonl 或 opencode.db 获取历史会话数据
4. 对比当前会话，识别新模式和经验

## 写入规则

1. 所有新条目必须经用户确认后才能写入
2. 写入前展示完整条目内容给用户确认
3. 按日期分组，同一天的多条记录依次排列
4. 使用脚本 `scripts/manage_experience.py append --entry '...'` 写入
