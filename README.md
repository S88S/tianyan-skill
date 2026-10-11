# 天演（Tianyan）· 多引擎合一的 Agent Skill 进化系统

> **判据先行 → 知识编译 → 证据驱动 → 编辑受限 → 门控分层 → 棘轮保留 → 测试集生长**
>
> 一句话：先把"尺子"校准，把经验编译成持久知识，再用证据喂编辑，用四层门控拦错误，用棘轮保底，用自博弈防过拟合。

天演是一个用于**自动化进化 Agent Skill（SKILL.md）** 的开源系统。它对任意一个 skill 执行完整的进化循环——从判据校准、基线评估，到证据驱动编辑、四层门控，最终产出**可审计、可回滚**的改进版本。

与只做单点优化的工具不同，天演把多个来源的最高杠杆机制**整合成一条可落地的流水线**。

---

## 亮点

- **判据先校准**：动手改之前，先用"故意劣化对照实验"证明评分标准能识别已知劣化——识别不出就不硬跑。
- **知识永不回滚**：技能可回滚，经验编译成的持久 wiki 不丢；被拒提案的根因也是资产。
- **四层门控**：程序门 → 沙盒回归/探针 → 分数门 → 配对盲评门 → 人审，逐层拦错。
- **防膨胀内置**：Zip-on-Write 每轮检查，技能只进化不变胖。
- **测试集会生长**：验证集随轮次生长，防过拟合。

---

## 核心机制（九机制各取最高杠杆）

| # | 机制 | 解决的问题 |
|---|---|---|
| 1 | 判据校准（故意劣化对照） | rubric 不校准就是拿歪尺子量 |
| 2 | 持久 wiki 知识层 | 经验须编译成跨迭代复利的知识 |
| 3 | 证据包驱动编辑（8 正 + 16 负） | 编辑不能自由发挥，改要有依据 |
| 4 | 程序性验证门 | 能代码检查的绝不让 LLM 猜 |
| 5 | 编辑三操作 + 受保护区 + 原子提案 | 结构化编辑、可归因 |
| 6 | 测试集生长 | 验证集固定必然过拟合 |
| 7 | paired 同-judge 盲评 | 跨评委绝对分噪音大，同尺比较才可信 |
| 8 | git 棘轮 + CHECKPOINT | 只保留改进，人在回路 |
| 9 | 版本化发布管理 | 演化产出必须可审计、可回滚 |

---

## 工作流

```
Phase 0   判据校准        —— 故意劣化对照实验，校准评分标准
Phase 0.5 种子测试集      —— 每 skill 3 条种子 prompt
Phase 1   基线评估        —— 9 维 triage，诊断最弱维度簇
Phase 2   证据驱动编辑循环 —— 采样 → wiki 编译 → 证据包 → 编辑者
Phase 3   四层门控        —— 程序门 / 沙盒回归 / 分数门 / 配对盲评 → 人审
Phase 4   测试集生长      —— 出题器 + Cross-Time Replay
Phase 5   回归 + 成果卡片  —— 全量回归、生成成果卡片
Phase 6   版本化发布      —— 版本号 + 评测摘要 + 审批 + 回滚命令
```

---

## 安装

天演遵循 [Agent Skills](https://agentskills.io) 开放协议，可在任何 skills-compatible runtime 上运行（Claude Code、Codex、Cursor、OpenCode 等）。

```bash
npx skills add <你的仓库地址> --skill tianyan-skill
```

或手动：把整个 `tianyan-skill/` 目录放入你所用 runtime 的 skills 目录（如 `~/.claude/skills/`、`~/.codex/skills/`）。

---

## 使用

| 你说 | 天演做 |
|---|---|
| 优化所有 skills | Phase 0–5 全流程，按分数升序优先最低 5–10 个 |
| 优化 xxx 这个 skill | 只对指定 skill 执行 |
| 评估 xxx 的质量 | 只跑 Phase 0–1（校准 + 基线），不进编辑循环 |
| 跑一轮天演 | 对指定/全部技能跑一轮完整进化循环 |

---

## 目录结构

```
tianyan-skill/
├── SKILL.md                  # 主流程
├── references/               # 分机制详解
│   ├── judge-calibration.md  # 判据校准协议
│   ├── evidence-packaging.md # 证据包规范
│   ├── gate-pipeline.md      # 四层门控细节
│   ├── ssl_guidelines.md     # SSL 三层结构规范
│   └── runtime-neutrality.md # 运行时中立性审查
├── scripts/                  # 可执行检查
│   ├── validate_proposal.py
│   ├── check_bloat.py
│   ├── forbidden_terms.py
│   └── validate_ssl_record.py
├── templates/result-card.html
├── wiki/                     # 持久知识层（永不回滚）
└── test-prompts.json
```

---

## 来源与致谢

天演是**多来源机制的系统整合**，其设计吸收了以下工作。特此郑重致谢（按机制来源排序）：

### 论文

- **SkillLens** — *From Raw Experience to Skill Consumption*（arXiv:2605.23899），许可 **CC BY 4.0**。判据校准、meta-rubric 三维度。
- **WikiSkill** — *Compiling Agent Experience into Persistent Knowledge for Skill Evolution*（arXiv:2608.27454），许可 **CC BY 4.0**。持久 wiki、原子提案、执行/知识分离。
- **SkillZip** — *Evaluation-Free Skill Compression for Self-Evolving Agents*（arXiv:2608.11079），许可 **CC BY 4.0**。explain-once-reference-many、Zip-on-Write 防膨胀。
- **Ctx2Skill** — *From Context to Skills*（arXiv:2604.27660），**arXiv 非独占许可**。多角色自博弈、Cross-Time Replay。
- **SkillOpt** — *Executive Strategy for Self-Evolving Agent Skills*（arXiv:2605.23904），**arXiv 非独占许可**。编辑三操作、受保护区。

### 开源项目

- **microsoft/SkillOpt** — 许可 **MIT**。
- **Qwen-Applications/skill-self-play**（Skill-SP）— 许可 **Apache-2.0**。证据包、程序性验证门、禁词。
- **alchaincyf/darwin-skill**（达尔文）— 许可 **MIT**。9 维 rubric、paired 同-judge 盲评、git 棘轮、成果卡片。
- **COOLPKU/SSL** — 本项目的 SSL 三层结构**字段契约**参考自此。该仓库未声明许可证，故本项目的 SSL 校验脚本与规范文档**均为独立重写**（见 `scripts/validate_ssl_record.py` 与 `references/ssl_guidelines.md` 的文件头声明）。

---

## 许可证

本项目采用 [MIT License](LICENSE) 发布。
