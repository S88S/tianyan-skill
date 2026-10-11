"""天演 · 禁词表（FORBIDDEN_LEAKAGE_TERMS）

代码级防泄漏：proposal / 证据包中命中以下词即拒绝。
来源：Skill-SP 仓库 refine_skills.py 硬编码禁词（8 个），保持逐字一致。
"""

FORBIDDEN_LEAKAGE_TERMS = (
    "bfcl",
    "berkeley function calling",
    "api-bank",
    "api bank",
    "benchmark",
    "test set",
    "evaluation set",
    "evaluation suite",
)


def scan_text(text: str) -> list:
    """返回 text 中命中的全部禁词（小写匹配）。"""
    low = text.lower()
    return [t for t in FORBIDDEN_LEAKAGE_TERMS if t in low]


if __name__ == "__main__":
    import sys

    text = sys.stdin.read()
    hits = scan_text(text)
    if hits:
        print("FORBIDDEN_TERMS_HIT:", ", ".join(hits))
        sys.exit(1)
    print("CLEAN")
