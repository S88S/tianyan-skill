# Changelog

本项目遵循语义化版本：x = 机制级变更，y = 每轮演化。

## v2.2 — 2026-09-01

- 引入 **Skill Registry**：版本化发布管理（Phase 6）
- 新增 `skill.meta.json`、发布记录（版本号 + 评测摘要 + 审批）、回滚命令
- 强化"没有 rollback 的 evolution 是不可控漂移"约束

## v2.1

- 引入 **SkillZip 防膨胀**：Zip-on-Write 每轮内置（`check_bloat.py`），技能只进化不变胖

## v2.0

- 引入 **WikiSkill 持久知识层**：`wiki/` 目录，模式知识永不回滚
- 证据包驱动编辑循环；执行/知识分离

## v1.x

- **多引擎合一**：整合判据校准（SkillLens）、证据驱动编辑（Skill-SP/SkillOpt）、四层门控、git 棘轮（达尔文）、测试集生长（Ctx2Skill）
