#!/usr/bin/env python3
"""SSL 记录校验器 —— 天演自研实现。

检查一份（或多份）SSL（Scheduling-Structural-Logical）技能记录是否满足
三层结构的字段完整性与取值约束，供天演 Phase 3「程序门」调用。

输入：单个 JSON 记录，或 JSONL（每行一条，可带 ssl_record 包裹层）。
用法：python3 validate_ssl_record.py <path> [--heads N]
退出码：0 = 全部合规；1 = 存在不合规记录或读取失败。

说明：字段名与受控取值属于 SSL 接口契约，为兼容既有记录而保留；
本文件的实现、结构与措辞为天演独立编写。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# —— 三层结构受控词表（接口契约，取值固定）——
SCENE_KINDS = ("PREPARE", "ACQUIRE", "REASON", "ACT", "VERIFY", "RECOVER", "FINALIZE")
STEP_KINDS = (
    "READ", "SELECT", "COMPARE", "VALIDATE", "INFER", "WRITE",
    "UPDATE_STATE", "CALL_TOOL", "REQUEST", "TRANSFER", "NOTIFY", "TERMINATE",
)
RESOURCE_SCOPES = (
    "MEMORY", "LOCAL_FS", "CODEBASE", "PROCESS",
    "USER_DATA", "CREDENTIALS", "NETWORK", "OTHER",
)
SCENE_END = ("END_SUCCESS", "END_FAIL")
STEP_END = ("YIELD_SUCCESS", "YIELD_FAIL")

REQUIRED_TOP = ("skill", "scenes", "logic_steps")


def _repeat_flags(seq):
    """找出序列里重复出现的元素。"""
    seen, dup = set(), []
    for x in seq:
        if x in seen:
            dup.append(x)
        seen.add(x)
    return dup


def _rule_targets(rules):
    """从规则列表里抽取所有 target。"""
    if not isinstance(rules, list):
        return []
    return [r.get("target") for r in rules if isinstance(r, dict)]


def check_record(record: dict) -> list[str]:
    """逐层校验一条记录，返回问题清单（列表为空即合规）。"""
    missing = [f for f in REQUIRED_TOP if f not in record]
    if missing:
        return [f"缺少顶层字段：{', '.join(missing)}"]

    skill = record.get("skill")
    scenes = record.get("scenes")
    steps = record.get("logic_steps")

    problems: list[str] = []
    if not isinstance(skill, dict):
        problems.append("skill 必须是对象")
        skill = {}
    if not isinstance(scenes, list) or not scenes:
        problems.append("scenes 必须是非空列表")
    if not isinstance(steps, list) or not steps:
        problems.append("logic_steps 必须是非空列表")
    if problems:
        return problems

    scene_ids = [s.get("scene_id") for s in scenes if isinstance(s, dict)]
    step_ids = [s.get("logic_step_id") for s in steps if isinstance(s, dict)]
    scene_set, step_set = set(scene_ids), set(step_ids)
    for d in _repeat_flags(scene_ids):
        problems.append(f"scene_id 重复：{d}")
    for d in _repeat_flags(step_ids):
        problems.append(f"logic_step_id 重复：{d}")

    entry = skill.get("entry_scene_id")
    if entry not in scene_set:
        problems.append(f"entry_scene_id 未指向已有场景：{entry}")
    for sub in skill.get("subscenes") or []:
        if sub not in scene_set:
            problems.append(f"subscenes 引用了不存在的场景：{sub}")

    # —— 结构层：逐场景校验 ——
    for sc in scenes:
        if not isinstance(sc, dict):
            problems.append("scenes 的元素必须是对象")
            continue
        sid = sc.get("scene_id")
        if sc.get("scene_type") not in SCENE_KINDS:
            problems.append(f"{sid}: scene_type 非法取值（{sc.get('scene_type')}）")
        owned = sc.get("contained_logic_steps")
        owned = owned if isinstance(owned, list) else []
        if sc.get("entry_logic_step_id") not in owned:
            problems.append(f"{sid}: entry_logic_step_id 不在 contained_logic_steps 内")
        for lid in owned:
            if lid not in step_set:
                problems.append(f"{sid}: contained_logic_steps 引用了不存在的步骤 {lid}")
        for tgt in _rule_targets(sc.get("next_scene_rules")):
            if tgt not in scene_set and tgt not in step_set and tgt not in SCENE_END:
                problems.append(f"{sid}: next_scene_rules 目标非法（{tgt}）")

    # —— 逻辑层：逐步骤校验 ——
    for st in steps:
        if not isinstance(st, dict):
            problems.append("logic_steps 的元素必须是对象")
            continue
        lid = st.get("logic_step_id")
        if st.get("act_type") not in STEP_KINDS:
            problems.append(f"{lid}: act_type 非法取值（{st.get('act_type')}）")
        if st.get("resource_scope") not in RESOURCE_SCOPES:
            problems.append(f"{lid}: resource_scope 非法取值（{st.get('resource_scope')}）")
        for tgt in _rule_targets(st.get("next_step_rules")):
            if tgt not in step_set and tgt not in STEP_END:
                problems.append(f"{lid}: next_step_rules 目标非法（{tgt}）")

    return problems


def load_records(path: Path):
    """读取文件，产出 (标签, 记录) 序列；支持 .json 与 .jsonl。"""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            record = row.get("ssl_record", row) if isinstance(row, dict) else row
            yield f"{path}:{line_no}", record
    else:
        obj = json.loads(text)
        if isinstance(obj, dict) and "ssl_record" in obj:
            obj = obj["ssl_record"]
        yield str(path), obj


def main() -> int:
    parser = argparse.ArgumentParser(
        description="校验 SSL 技能记录（天演自研实现）",
    )
    parser.add_argument("path", help="JSON 记录文件或 JSONL 记录文件")
    parser.add_argument("--heads", type=int, default=20,
                        help="最多展示多少条失败记录（默认 20）")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        records = list(load_records(path))
    except Exception as exc:  # 文件缺失、JSON 解析错误等
        print(f"FAIL: {path}（无法读取：{exc}）")
        return 1

    failures: list[tuple[str, list[str]]] = []
    total = 0
    for label, record in records:
        total += 1
        if not isinstance(record, dict):
            failures.append((label, ["记录必须是 JSON 对象"]))
            continue
        errs = check_record(record)
        if errs:
            failures.append((label, errs))

    if failures:
        print(f"FAIL: {path}")
        for label, errs in failures[: args.heads]:
            print(f"- {label}")
            for e in errs:
                print(f"  - {e}")
        if len(failures) > args.heads:
            print(f"- ... 另有 {len(failures) - args.heads} 条不合规记录")
        return 1

    print(f"OK: {path} ({total} record(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
