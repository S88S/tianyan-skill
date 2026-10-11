# 四层门控细节（Phase 3）— 每层的判据、判据来源、失败处理

SKILL.md 的「Phase 3: 四层门控」引用本文件。

## 门 1: 程序门（零成本，代码级）— Skill-SP

执行：`python3 scripts/validate_proposal.py proposal.json`

| 检查 | 判据 | 失败处理 |
|---|---|---|
| 结构五要素 | updates / defect_specific_probes / package_weakness / motivating_evidence / positive_anchors_preserved 非空 | 拒绝，回编辑者补全 |
| 禁词扫描 | 全文 JSON dump 查 FORBIDDEN_LEAKAGE_TERMS 8 词 | 拒绝（代码级防泄漏，不靠自觉） |
| 路径白名单 | 只允许 ALLOWED_UPDATE_FILES；禁目录路径、禁重复、禁只读文件 | 拒绝 |
| 探针完整性 | 每个 probe 必须有 sample 字段 | 拒绝 |

性质：**确定性检查，零评估成本**——先挡住格式/泄漏类错误，再花成本上分数门。

## 门 2: 沙盒回归 + 探针（代码级）— Skill-SP

执行：`python3 scripts/validate_proposal.py proposal.json --package-dir <skill目录>`

流程：tempfile 临时目录 copytree 源包 → 逐 update **原子写**（tmp+os.replace）→ 校验：
1. 包 schema 完整（本技能场景：SKILL.md frontmatter 的 name/description 存在）
2. **skill_id 不得变**
3. SKILL.md / examples / schema / tests 逐项存在
4. 正面锚点回归测试全过（issue 前缀 positive_anchor_，用验证锚点池）
5. 提案自带探针全过（前缀 probe_）

全过且 `--apply` 才写回源目录。**门 2 不看效果，只看"改了没改坏"。**

## 门 3: 分数门（held-out 严格更优）— SkillOpt

- 数据划分：split_ratio **2:1:7**（train : selection : test），split_seed 固定可复现
- 判据：**选择集（selection）上分数严格更优才替换；平手拒绝**
- 质量指标四件套：validation score / test score / skill 长度 token 数 / candidate acceptance rate（门控记录要记全）

**soft gate 例外（社区 PR #25，非论文默认）**：
- 触发条件：自定义环境、selection split 极小（≤10）、奖励连续（F1/BLEU）
- 症状：候选提升 soft 分但永不翻转离散 hard 结果 → hard gate 拒掉一切 → **训练停滞**
- 解法：gate_metric 三选一——hard（默认）/ soft（per-item partial credit）/ **mixed**（加权 (1−w)·hard + w·soft，w 默认 0.5）
- 教训：**严格不等于僵化**，门控指标必须与奖励形态匹配

## 门 4: 配对盲评门（paired 同-judge + 奇数 N 多数决）— 达尔文 v2.1

- spawn **2 个新 judge**，本轮不复用上轮评委（防锚定效应）
- 每个 judge **内部配对比较**：同一 judge 分别看 V1 和 V2，给出 within-judge 差值
- 为什么：跨 judge 绝对分噪音 **±8 分**，大于保守编辑的真实增益 → false-revert；within-judge 比较消除"换尺污染"
- 决策：奇数 N 多数决；N=2 平手 → 保守处理（可加第 3 评委或判不通过）
- 绝对分数全程只作 triage（排序找短板），不作保留判据

## 人审 🔴（每轮必停）

展示：diff + 四层门控记录 + 分数变化 + wiki 增量（新模式/更新模式）。用户有权否决任何一层结果——**机器判不了的最后裁决**。

## 棘轮与 wiki 保留（v2.0 规则）

- **revert 只作用于技能文件**（SKILL.md 等被提案改动的文件）；`wiki/` 目录任何情况下不 revert、不回退
- 每轮验证后（无论接受/拒绝），程序化追加 `wiki/skill-impact.md`：提案元数据 + diff + 验证分 + 接受/拒绝 + 引用的模式
- 被拒提案的根因分析仍留在 wiki——编辑者下轮可通过 skill-impact.md 查询"哪些改动被拒过、为什么"，避免重复失败编辑（实证：Iteration 0 被拒提案直接促成 Iteration 1 被接受的提案）
- **执行与知识分离**：门控回归（门 2 探针、门 3 分数）的执行 agent 不注入 wiki 内容；wiki 只供 Phase 2 编辑者按需检索

## results.tsv 行格式（paired 行）

```
skill  round  score_before  score_after  judge1_delta  judge2_delta  gate1  gate2  gate3  gate4  human  dry_run  note
```

## 早停 / 触顶 / 告警阈值

| 信号 | 阈值 | 动作 |
|---|---|---|
| 早停 | 单轮涨幅 < 1 分 | break |
| 触顶 | 连续 2 轮 Δ < 2 | break（禁止为凑满轮次 keep 边际改动） |
| 评估失效 | dry_run 比例 > 30% | 告警并标注评估不可信 |
| 最大轮数 | MAX_ROUNDS = 4（由证据包数决定） | 硬上限 |
