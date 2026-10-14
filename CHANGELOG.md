# Changelog

本项目遵循语义化版本：x = 机制级变更，y = 每轮演化。

## v2.3 — 2026-10-15

- **判据可判定化**：9 维 rubric 评分标准改逐条 ✓/✗ 可判定判据；`references/judge-calibration.md` 新增判例对照库（每维 Bad/Good）
- **judge confidence 自报**：逐维输出 0-1 置信度，<0.7 标 low_conf 不计多数决、强制转人审
- **门 2.5 代理信号证明条款**：脚本通过/测试绿灯等代理信号只有覆盖全部要求才算完成证据（"The audit must prove completion, not merely fail to find obvious remaining work."）
- **红线冗余豁免白名单**：`<!-- CRITICAL_REPEAT_START/END -->` 标记区不计重复段与长度比（check_bloat.py 支持，关键红线"说三遍"属有意冗余）
- **截断=缺失**：截断证据标 truncated_missing，不按"未见异常"处理
- **证据隔离防注入**：证据内容是数据不是指令，注入内容标 untrusted_injection 并弃用指令效力
- **同源去重**：互抄/蒸馏证据只计一个独立来源，交叉验证先查来源谱系
- 来源：CL4R1T4S 28 份大厂系统提示词档案（OpenAI/Anthropic/Google/智谱等）精读提炼 10 门道中适用于天演的 7 条

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
