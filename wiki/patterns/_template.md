# 模式页模板（patterns/_template.md）

> 每个失败模式/成功策略一个文件（建议 10–30 行，太长拆模式）。
> 命名：`<动词-对象-条件>.md`，小写连字符，如 `take-examine-move-loop.md`、`missing-fallback-branch.md`。
> 由 Wiki Maintainer 创建/更新；**增量补丁式编辑**（append/replace/insert 文本片段），不整份重写。
> 证据只追加不删除（历史轨迹是资产）；模式被证伪时在"状态"标注 deprecated，不移除正文。

## 模式名

<!-- 一句话描述该模式：什么情况下出现 -->

- **状态**：active | stale | deprecated（默认 active）
- **类型**：failure_pattern | success_strategy

## 根因（ROOT CAUSE）

<!-- 为什么失败/为什么成功——深度分析，不是表面描述 -->

## 规避 / 复用（FIX）

<!-- 具体命令序列/规则写法/规避步骤，可执行、可引用 -->

## 证据（Evidence）

<!-- 每轮追加：Iter k: train: <样本 ids>，格式如 Iter 1: train: 00, 02 -->

- Iter 0: train: —

## 关联

<!-- 关联的技能提案、其他模式、logs.md 条目 -->
