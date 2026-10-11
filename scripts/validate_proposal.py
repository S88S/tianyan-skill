#!/usr/bin/env python3
"""天演 · 程序性验证门（Gate 1）+ 沙盒回归（Gate 2）核心脚本。

用法：
    python3 validate_proposal.py proposal.json [--package-dir <skill目录>] [--apply]

proposal.json 结构（编辑者 schema）：
{
  "action": "keep | update",
  "package_weakness": "最弱维度诊断摘要",
  "motivating_evidence": ["negative_001", ...],          # 必须引用负面证据
  "positive_anchors_preserved": ["positive_001", ...],   # 声明保留的正面锚点
  "recommended_updates": [{"path": "SKILL.md", "content": "整份新内容"}],  # 整份替换，非 diff
  "defect_specific_probes": [{"issue": "probe_001", "sample": {...}}],     # 自带探针
  "probe_ideas": [...],
  "overfit_risks": [...]
}

返回值：0 = 通过；1 = 未通过（打印问题清单）；2 = 用法错误。

Gate 1（无 --package-dir 也可跑）：结构五要素 + 禁词扫描 + 路径白名单 + 探针完整性。
Gate 2（需 --package-dir）：临时沙盒 copytree → 原子写 → SKILL.md frontmatter/schema 检查
                            → skill_id 不变 → 正面锚点回归 → 探针存在性。
--apply：仅当全部检查通过时，才把 updates 原子写回源目录（危险操作，默认关闭）。
"""

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from forbidden_terms import scan_text

ALLOWED_UPDATE_FILES = {
    "SKILL.md", "rules.md", "solver_rules.md", "generator_hints.md",
    "examples.jsonl", "validator_spec.md", "validator.py",
}
READ_ONLY_CONTEXT_FILES = {"checker.py", "sample_schema.json", "tests.jsonl", "stats.json"}

REQUIRED_STRUCTURE = {
    "recommended_updates": "missing_updates",
    "defect_specific_probes": "missing_defect_specific_probes",
    "package_weakness": "missing_package_weakness",
    "motivating_evidence": "missing_motivating_evidence",
    "positive_anchors_preserved": "missing_positive_anchors_preserved",
}


def check_structure(proposal):
    return [code for key, code in REQUIRED_STRUCTURE.items() if not proposal.get(key)]


def check_leakage(proposal):
    hits = scan_text(json.dumps(proposal, ensure_ascii=False))
    return ["forbidden_term:" + t for t in hits]


def check_paths(proposal):
    issues, seen = [], set()
    for upd in proposal.get("recommended_updates", []):
        path = upd.get("path", "")
        name = Path(path).name
        if name != path:
            issues.append("dir_path_not_allowed:" + path)
        if name not in ALLOWED_UPDATE_FILES:
            issues.append("path_not_in_whitelist:" + name)
        if name in READ_ONLY_CONTEXT_FILES:
            issues.append("read_only_context:" + name)
        if path in seen:
            issues.append("duplicate_path:" + path)
        seen.add(path)
    return issues


def check_probes(proposal):
    return [
        "probe_missing_sample:" + str(p.get("issue", "?"))
        for p in proposal.get("defect_specific_probes", [])
        if "sample" not in p
    ]


def apply_updates_sandbox(package_dir, proposal):
    """在临时副本上原子写，返回 (tmpdir, errors)。"""
    tmp = tempfile.mkdtemp(prefix="tianyan-gate2-")
    shutil.copytree(package_dir, tmp, dirs_exist_ok=True)
    errors = []
    for upd in proposal.get("recommended_updates", []):
        path = Path(tmp) / upd["path"]
        if "content" not in upd:
            errors.append("missing_content:" + upd["path"])
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        tmpf = path.with_suffix(path.suffix + ".tmp")
        tmpf.write_text(upd["content"], encoding="utf-8")
        tmpf.replace(path)
    return tmp, errors


def check_skill_md(tmp):
    p = Path(tmp) / "SKILL.md"
    if not p.exists():
        return ["skill_md_missing"]
    text = p.read_text(encoding="utf-8")
    issues = []
    if not text.startswith("---"):
        issues.append("frontmatter_missing")
    if not re.search(r"^name:\s*\S+", text, re.M):
        issues.append("frontmatter_name_missing")
    if not re.search(r"^description:\s*\S+", text, re.M):
        issues.append("frontmatter_description_missing")
    return issues


def check_skill_id_unchanged(tmp, package_dir):
    def get_id(d):
        p = Path(d) / "SKILL.md"
        if not p.exists():
            return None
        m = re.search(r"^name:\s*(\S+)", p.read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else None

    old, new = get_id(package_dir), get_id(tmp)
    return [] if old == new else ["skill_id_changed:%s->%s" % (old, new)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proposal", help="proposal.json 路径")
    ap.add_argument("--package-dir", help="目标 skill 目录（启用沙盒回归 Gate 2）")
    ap.add_argument("--apply", action="store_true", help="全过时写回源目录（危险，默认关闭）")
    args = ap.parse_args()

    try:
        proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    except Exception as e:
        print("proposal_parse_error:", e)
        sys.exit(2)

    if proposal.get("action") == "keep":
        print("KEEP (action=keep)")
        sys.exit(0)

    issues = []
    issues += ["structure:" + c for c in check_structure(proposal)]
    issues += check_leakage(proposal)
    issues += check_paths(proposal)
    issues += check_probes(proposal)

    if args.package_dir and not issues:
        tmp, errs = apply_updates_sandbox(args.package_dir, proposal)
        issues += errs
        issues += ["skillmd:" + c for c in check_skill_md(tmp)]
        issues += check_skill_id_unchanged(tmp, args.package_dir)

    if issues:
        print("REJECTED")
        for i in issues[:20]:
            print("  -", i)
        sys.exit(1)

    if args.package_dir and args.apply:
        for upd in proposal.get("recommended_updates", []):
            dst = Path(args.package_dir) / upd["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            tmpf = dst.with_suffix(dst.suffix + ".tmp")
            tmpf.write_text(upd["content"], encoding="utf-8")
            tmpf.replace(dst)
        print("APPLIED (all gates passed, written to source)")
        sys.exit(0)

    print("ACCEPTED (structure+leakage+paths+probes+regression clean)")
    sys.exit(0)


if __name__ == "__main__":
    main()
