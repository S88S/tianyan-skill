# 多 runtime 兼容性审查

> SKILL.md 的「Runtime 适配性审查」章节引用本文件。Phase 1 基线评估时跑红灯扫描需查这里。

---

## 背景

Agent Skills（https://agentskills.io）是一套开放协议。一份合规的 skill 应当能在
Claude Code、Codex、Cursor、OpenCode、Gemini CLI 等多种 skills-compatible runtime 上通用。

这是 skill 分发力的根基——**一份被误判为"绑定单一 runtime"的 skill，会被其他 runtime
的 agent 直接拒绝安装**，白白损失潜在用户。

**适用范围**：除非 skill 名称明确声明绑定单一 runtime（如 `xxx-for-claude-code`、
`xxx-codex-edition`），所有 skill 都应通过本审查。

---

## 红灯信号（出现即扣分，须在 P0 优化轮修复）

| 红灯类型 | 典型表现 | 危害 |
|---|---|---|
| Badge 钉死 | 形如 `[![Claude Code Skill]]`、`[![Cursor Only]]` 的单一 runtime 徽章 | 首屏就把其他 runtime 用户劝退 |
| 措辞钉死 | "在 Claude Code 里""Cursor 用户可以""Codex 中使用" | agent 解析时误判为"不是给我用的" |
| 安装命令钉死 | 只给某一 runtime 的私有路径或私有 CLI | 其他 runtime 的 agent 无从安装 |
| 工具调用钉死 | 工作流硬编码某 runtime 独有工具（如某家 chrome MCP、PostToolUse hook）且不给替代 | 其他 runtime 缺该工具 → 流程跑不通 |
| 路径硬编码 | 把 `~/.claude/skills/xxx/`、`.claude/agents/yyy` 当作唯一路径 | 其他 runtime 用各自的 skills 目录 |

---

## 绿灯措辞（推荐改写）

| 红灯 | 绿灯 |
|---|---|
| "在 Claude Code 里" | "在你的 agent 里" / "在任何 skills-compatible runtime 中" |
| "Claude Code skill" | "Agent Skill" |
| "Claude Code 用户" | "skills-aware agent 用户" |
| 单一 runtime badge | `Agent Skills Standard` + `Multi-Runtime` 等中立徽章 |
| 只给一行某 runtime 安装命令 | 三层：① 自动检测的一行命令 ② 折叠展开的各 runtime 手动路径 ③ "作为参考资料 cat 进 context" fallback |
| 工具名硬编码 | "用一个 browser automation 工具（例如 Playwright 等）" |

---

## 例外清单（允许的单一-runtime 痕迹）

下面几类**不算红灯**，属正当出现：

1. **Frontmatter `description` 里的中英文触发词**——这是 skill 入口，各 runtime 解析 frontmatter 时同样能匹配；
2. **同生态内部联动的 skill 名引用**——如"调用 xx-design""与 xx-skill 配套"，只要不是安装/运行硬依赖；
3. **明确标注的 runtime-specific 章节**——如"### 仅某 runtime 优化（按需触发）"，并说明是 nice-to-have；
4. **commit message、CHANGELOG、内部脚本**——不属于用户读到的 skill 内容。

---

## 审查时机

- **Phase 1 基线评估**：每个 skill 跑一次红灯扫描，命中项以 `runtime_warn=N` 写入 results.tsv 的 `note` 列（不新增列，保持向后兼容）；
- **Phase 2 优化循环**：红灯命中数 ≥ 1 的 skill，强制把第一轮方向定为 P0「runtime drift 修复」；
- **Phase 3 汇总报告**：单独一栏「runtime 中立度」，展示命中数 X → 0 的进度。

---

## 红灯扫描快速命令

```bash
grep -nE "(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)" SKILL.md README.md 2>/dev/null
```

输出非空 = 该 skill 未通过审查，必须在优化循环里修复。
