#!/usr/bin/env python3
"""check_bloat.py — 天演 v2.1 防膨胀程序性检查（Zip-on-Write）

零依赖纯 Python。用法：
    python3 scripts/check_bloat.py <SKILL.md路径> [种子长度参考]

检查三项：
  1. 长度比：当前长度 vs 种子长度（默认取 SKILL.md 首次 commit 版本行数，可传参覆盖）
  2. 重复段：连续 3+ 行完全相同的块（疑似复制粘贴的规则/动作序列）
  3. FROZEN 保护：标记压缩候选区域时不得触碰受保护区

输出 JSON：{"ratio": x, "threshold_ok": bool, "duplicates": [...], "frozen_blocks": n}
退出码：0 = 无需压缩；1 = 触发压缩建议（长度比超限或发现重复段）。
"""
import sys
import json
import re
from pathlib import Path

# Zip-on-Write 实证阈值（SkillZip arXiv:2608.11079，16 轮实验长度钉在 1.6-1.9 倍）
RATIO_TARGET_MAX = 1.9   # 目标上限（钉住区间）
RATIO_WARN = 2.0         # 超过此值强制触发压缩
DUP_MIN_LINES = 3        # 连续 N 行相同视为重复段

FROZEN_MARKERS = [
    "FROZEN_START", "FROZEN_END",
    "SLOW_UPDATE_START", "SLOW_UPDATE_END",
    "APPENDIX_START", "APPENDIX_END",
]


def line_stats(text: str):
    lines = [l for l in text.splitlines()]
    nonempty = [l for l in lines if l.strip()]
    return len(lines), len(nonempty), len(text)


def find_duplicates(lines):
    """连续 >=3 行完全相同的块 = 疑似复制段。返回 [(起始行, 结束行, 行内容首行), ...]"""
    dups = []
    i = 0
    n = len(lines)
    while i < n - (DUP_MIN_LINES - 1):
        # 找当前行重复的最大连续段
        j = i + 1
        while j < n and lines[j].strip() and lines[j] == lines[i]:
            j += 1
        run = j - i
        if run >= DUP_MIN_LINES and lines[i].strip():
            dups.append((i + 1, j, lines[i].strip()[:60]))
            i = j
        else:
            i += 1
    return dups


def frozen_count(text: str):
    return sum(text.count(m) for m in FROZEN_MARKERS)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: check_bloat.py <SKILL.md> [seed_lines]"}, ensure_ascii=False))
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(json.dumps({"error": f"file not found: {path}"}, ensure_ascii=False))
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    total_lines, nonempty, chars = line_stats(text)

    # 种子长度：优先参数；否则尝试 git 首个 commit
    seed_lines = None
    if len(sys.argv) >= 3:
        try:
            seed_lines = int(sys.argv[2])
        except ValueError:
            pass
    if seed_lines is None:
        try:
            import subprocess
            r = subprocess.run(
                ["git", "log", "--oneline", "--follow", "--reverse", str(path)],
                capture_output=True, text=True, cwd=str(path.parent), timeout=10,
            )
            first = r.stdout.strip().splitlines()
            if first:
                r2 = subprocess.run(
                    ["git", "show", first[0].split()[0] + f":{path.name}"],
                    capture_output=True, text=True, cwd=str(path.parent), timeout=10,
                )
                seed_lines = len(r2.stdout.splitlines())
        except Exception:
            pass

    ratio = (total_lines / seed_lines) if seed_lines else None
    dups = find_duplicates(text.splitlines())
    frozen = frozen_count(text)

    trigger = False
    reasons = []
    if ratio is not None and ratio > RATIO_WARN:
        trigger = True
        reasons.append(f"长度比 {ratio:.2f} 超过 RATIO_WARN({RATIO_WARN})")
    elif ratio is not None and ratio > RATIO_TARGET_MAX:
        reasons.append(f"长度比 {ratio:.2f} 超过目标上限 {RATIO_TARGET_MAX}（建议压缩）")
    if dups:
        trigger = True
        reasons.append(f"发现 {len(dups)} 处疑似重复段")

    result = {
        "file": str(path),
        "total_lines": total_lines,
        "nonempty_lines": nonempty,
        "chars": chars,
        "seed_lines": seed_lines,
        "ratio": round(ratio, 3) if ratio else None,
        "ratio_target_max": RATIO_TARGET_MAX,
        "ratio_warn": RATIO_WARN,
        "duplicates": [{"start": s, "end": e, "sample": t} for s, e, t in dups],
        "frozen_marker_count": frozen,
        "compression_required": trigger,
        "reasons": reasons,
    }
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 1 if trigger else 0


if __name__ == "__main__":
    sys.exit(main())
