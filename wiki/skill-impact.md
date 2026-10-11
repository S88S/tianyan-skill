# 技能影响追踪（skill-impact.md）

> 由外层循环在每轮验证后**程序化追加**（非 LLM 书写），记录每次提案的元数据、diff、验证分、接受/拒绝。
> 三个用途：① 编辑者（Proposer）的决策参考——避免重复被拒的失败编辑；② 模式健康度统计——驱动 wiki 修剪；③ 完整审计轨迹（ADR 式决策日志）。

## 记录格式

```markdown
### Iteration k · <date>
- proposal: <create|update> <skill-id>
- diff: <统一 diff 摘要或路径>
- validation_score: <R>
- outcome: <Accepted|Rejected>
- rejected_reason: <如 Rejected 填写>
- referenced_patterns: [<pattern-name>, ...]
```

## Impact Log

<!-- 每轮追加一行（程序化）：
| Iter | 提案 | 目标技能 | 验证分 | 结果 | 引用的模式 | 被拒原因 |
|---|---|---|---|---|---|---|
-->

| Iter | 提案 | 目标技能 | 验证分 | 结果 | 引用的模式 | 被拒原因 |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

## 模式健康度（wiki 修剪依据）

> 每轮结束后统计：每个模式被提案引用的次数、促成 Accepted 提案的比例。
> 连续 N 轮（默认 2）未被引用，或引用但从未促成 Accepted → 标记 stale，移入 `patterns/archived/`。

| 模式 | 被引用次数 | 促成 Accepted 次数 | 状态 |
|---|---|---|---|
| — | — | — | active |
