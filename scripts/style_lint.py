# CCF 风格检查（macOS Vibrancy）：禁止 class 模式、必须模式、主题 token（PRD 11）。
# 输出 JSON 报告：passed / violations[{rule_id,pattern,line,severity}] / checked_at。
"""CCF 风格 lint：针对 macOS Vibrancy 风格法做规则检查。

禁止项与必须项见 PRD 11.6-11.8，亮/暗 token 见 11.3-11.4。
另提供表达约束扫描（PRD 12），供 G6/G9 门复用。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from ccf_state import now_iso

# ---- 禁止 class 模式（PRD 11.7 + 11.6）----
FORBIDDEN_PATTERNS = [
    ("F-1",  re.compile(r"^bg-gradient"), "渐变背景"),
    ("F-2",  re.compile(r"^shadow-(lg|xl|2xl|3xl)$"), "阴影过重"),
    ("F-3",  re.compile(r"^shadow-\[[^\]]*(10px|12px|15px|20px|24px|30px)[^\]]*\]$"), "阴影 spread 超过 2px"),
    ("F-4",  re.compile(r"^animate-"), "装饰动画"),
    ("F-5",  re.compile(r"^rounded-(2xl|3xl|4xl|5xl|6xl)$"), "圆角超过 rounded-xl"),
    ("F-6",  re.compile(r"^rounded-full$"), "全圆角"),
    ("F-8",  re.compile(r"^border-[2-9]$"), "边框超过 1px"),
    ("F-8b", re.compile(r"^border-\[\d+px\]$"), "边框指定超过 1px"),
    ("F-10", re.compile(r"^border-(t|r|b|l|top|right|bottom|left)-[2-9]$"), "单侧粗边框"),
    ("F-10b", re.compile(r"^border-(x|y)-[2-9]$"), "粗边框"),
    ("F-11", re.compile(r"^text-(yellow|pink|green|purple)-[0-9]+$"), "禁止彩色文字"),
    ("F-7",  re.compile(r"^bg-\[#0a84ff\]$"), "强调色用作背景"),
    ("F-9",  re.compile(r"^bg-clip-text$"), "渐变文字"),
]

# 必须模式（PRD 11.8）
BUTTON_REQUIRED = (("R-BTN", "rounded-lg"), ("R-BTN", "transition-colors"), ("R-BTN", "duration-200"))
CARD_REQUIRED = (("R-CARD", "border"), ("R-CARD", "rounded-xl"))
INPUT_REQUIRED = (("R-INP", "border"), ("R-INP", "rounded-lg"), ("R-INP", "focus:border-"), ("R-INP", "placeholder-"))

# 主题 token 校验（PRD 11.3 / 11.4）
LIGHT_PALETTE = {"#e8e8ed", "#f5f5f7", "#ffffff", "#000000", "#0a84ff"}
DARK_PALETTE = {"#1c1c1e", "#2c2c2e", "#3a3a3c", "#ffffff", "#000000", "#0a84ff"}
COLORED_BG_PREFIX = r"^(bg-(red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-[0-9]+)"
GRAY_TEXT_PREFIX = r"^text-(gray|grey|zinc|stone|neutral)-"

CLASS_ATTR_RE = re.compile(r'class\s*=\s*"([^"]*)"')
CLASS_ATTR2_RE = re.compile(r"class\s*=\s*'([^']*)'")
STYLE_ATTR_RE = re.compile(r'style\s*=\s*"([^"]*)"')
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
GRADIENT_STYLE_RE = re.compile(r"(linear|radial|conic)-gradient", re.IGNORECASE)
TAG_RE = re.compile(r"<([a-zA-Z][\w-]*)((?:\"[^\"]*\"|'[^']*'|[^\"'>])*)>")
SELF_CLOSING_RE = re.compile(r"/\s*>")


def class_tokens_in_line(line: str) -> list:
    tokens = []
    for m in CLASS_ATTR_RE.finditer(line):
        tokens.extend(m.group(1).split())
    for m in CLASS_ATTR2_RE.finditer(line):
        tokens.extend(m.group(1).split())
    return tokens


def theme_palette(theme: str) -> set:
    return DARK_PALETTE if theme == "dark" else LIGHT_PALETTE


def check_token(token: str, theme: str, violations: list, line_no: int) -> None:
    """对单个 class token 跑禁止模式与主题 token 校验。"""
    for rule_id, pattern, desc in FORBIDDEN_PATTERNS:
        if pattern.match(token):
            violations.append({
                "rule_id": rule_id, "pattern": pattern.pattern,
                "line": line_no, "severity": "error", "details": "禁止项 %s: %s" % (rule_id, desc),
            })
    # 过渡仅颜色（11.2：transition-colors duration-200 ease-out）
    if token in ("transition-all", "transition"):
        violations.append({
            "rule_id": "T-4", "pattern": token, "line": line_no,
            "severity": "error", "details": "过渡必须仅作用于颜色",
        })
    if re.match(r"^duration-(300|500|700|1000)$", token):
        violations.append({
            "rule_id": "T-4", "pattern": token, "line": line_no,
            "severity": "warning", "details": "过渡时长必须为 duration-200",
        })
    if token.startswith("ease-out") is False and re.match(r"^ease-(in|in-out|linear)$", token):
        violations.append({
            "rule_id": "T-4", "pattern": token, "line": line_no,
            "severity": "warning", "details": "缓动必须为 ease-out",
        })
    # 调色板外颜色
    hex_attr = re.match(r"^(bg|text|border)-\[(#[0-9a-fA-F]{3,8})", token)
    if hex_attr:
        hexval = hex_attr.group(2).lower()
        if hexval not in theme_palette(theme):
            violations.append({
                "rule_id": "T-2", "pattern": token, "line": line_no,
                "severity": "warning", "details": "颜色不在主题 token 调色板内",
            })
    # 彩色背景 + 灰字（F-13）
    if re.match(COLORED_BG_PREFIX, token):
        pass  # 组合判断在调用方完成，见 check_combination


def check_combination(tokens: list, line_no: int, violations: list) -> None:
    """跨 token 的组合型检查：彩色背景灰字、eyebrow、渐变文字。"""
    has_colored_bg = any(re.match(COLORED_BG_PREFIX, t) for t in tokens)
    has_colored_bg_hex = any(
        re.match(r"^bg-\[#[0-9a-fA-F]{6}\]", t) and t not in ("bg-[#f5f5f7]", "bg-[#e8e8ed]", "bg-[#1c1c1e]", "bg-[#2c2c2e]", "bg-[#3a3a3c]", "bg-[#ffffff]", "bg-[#ffffff]", "bg-[#0a84ff]")
        for t in tokens)
    has_gray_text = any(re.match(GRAY_TEXT_PREFIX, t) for t in tokens)
    if (has_colored_bg or has_colored_bg_hex) and has_gray_text:
        violations.append({
            "rule_id": "F-13", "pattern": "彩色背景+灰字", "line": line_no,
            "severity": "error", "details": "彩色背景灰字违反 WCAG AA",
        })
    tiny = re.compile(r"^(text-\[1[0-4]px\]|text-xs)$")
    if any(tiny.match(t) for t in tokens) and "uppercase" in tokens and \
            any(t.startswith("tracking-wid") for t in tokens):
        violations.append({
            "rule_id": "F-11b", "pattern": "tiny uppercase eyebrow", "line": line_no,
            "severity": "error", "details": "tiny uppercase eyebrow 禁止",
        })
    if any(t == "bg-clip-text" for t in tokens):
        if any(g.startswith("bg-gradient") for g in tokens) or any(
                g.startswith("bg-[") and g not in ("bg-[#0a84ff]",) for g in tokens):
            pass  # F-9 已在上方按 token 记录


def check_element(line: str, line_no: int, violations: list) -> None:
    """按元素检查必须模式（button/card/input）。"""
    for m in TAG_RE.finditer(line):
        tag, attrs = m.group(1).lower(), m.group(2)
        if SELF_CLOSING_RE.search(attrs):
            continue
        tokens = class_tokens_in_line("class=" + attrs) if 'class' in attrs else []
        if not tokens:
            continue
        if tag == "button":
            for rule_id, req in BUTTON_REQUIRED:
                if req not in tokens:
                    violations.append({
                        "rule_id": rule_id, "pattern": "button 缺少 %s" % req, "line": line_no,
                        "severity": "error", "details": "按钮必须含 %s" % req,
                    })
        elif tag in ("input", "textarea"):
            missing = [req for rule_id, req in INPUT_REQUIRED
                       if not _has_prefix_or_exact(tokens, req)]
            for req in missing:
                violations.append({
                    "rule_id": "R-INP", "pattern": "input 缺少 %s" % req, "line": line_no,
                    "severity": "error", "details": "输入框必须含 %s" % req,
                })
        if "rounded-xl" in tokens:
            if "border" not in tokens:
                violations.append({
                    "rule_id": "R-CARD", "pattern": "card 缺少 border", "line": line_no,
                    "severity": "error", "details": "卡片必须含 border",
                })


def _has_prefix_or_exact(tokens: list, req: str) -> bool:
    if req in tokens:
        return True
    if req.endswith("-"):
        return any(t.startswith(req) for t in tokens)
    return any(t.startswith(req + "-") for t in tokens)


def check_nested_cards(text: str, violations: list) -> None:
    """扫描整个文本，检测嵌套卡片（rounded-xl 的 div 出现嵌套）。"""
    stack = []
    for m in TAG_RE.finditer(text):
        tag, attrs = m.group(1).lower(), m.group(2)
        line_no = text.count("\n", 0, m.start()) + 1
        if SELF_CLOSING_RE.search(attrs):
            continue
        tokens = class_tokens_in_line("class=" + attrs) if 'class' in attrs else []
        is_card = tag == "div" and "rounded-xl" in tokens
        if is_card:
            depth = sum(1 for s in stack if s)
            stack.append(True)
            if depth >= 1:
                violations.append({
                    "rule_id": "F-12", "pattern": "嵌套卡片", "line": line_no,
                    "severity": "error", "details": "卡片嵌套超过一层",
                })
        else:
            stack.append(False)
        closing = "</%s>" % tag
        if closing in text[m.end():m.end() + 32]:
            if stack:
                stack.pop()
    # 平衡残余（不处理跨行闭合的边界情况）


def lint_text(text: str, theme: str = "light", with_expression: bool = False) -> dict:
    """对文本执行风格检查；返回 JSON 报告。"""
    violations = []
    for idx, line in enumerate(text.splitlines(), start=1):
        tokens = class_tokens_in_line(line)
        for token in tokens:
            check_token(token, theme, violations, idx)
        check_combination(tokens, idx, violations)
        check_element(line, idx, violations)
        for sm in STYLE_ATTR_RE.finditer(line):
            style = sm.group(1)
            if GRADIENT_STYLE_RE.search(style):
                violations.append({
                    "rule_id": "F-1", "pattern": "style 内渐变", "line": idx,
                    "severity": "error", "details": "渐变禁止",
                })
            for hm in HEX_RE.finditer(style):
                if hm.group(0).lower() not in theme_palette(theme):
                    violations.append({
                        "rule_id": "T-2", "pattern": hm.group(0), "line": idx,
                        "severity": "warning", "details": "颜色不在主题 token 调色板内",
                    })
    check_nested_cards(text, violations)
    if with_expression:
        for ev in find_expression_violations(text):
            violations.append({
                "rule_id": ev["rule"], "pattern": ev["word"], "line": ev["line"],
                "severity": "error", "details": "表达约束违规",
            })
    errors = [v for v in violations if v["severity"] == "error"]
    return {
        "report": "style-lint",
        "theme": theme,
        "passed": len(errors) == 0,
        "violations": violations,
        "summary": {"total": len(violations), "errors": len(errors),
                    "warnings": sum(1 for v in violations if v["severity"] == "warning")},
        "checked_at": now_iso(),
    }


# ---- 表达约束扫描（PRD 12），供 G9 交付门复用 ----
def find_expression_violations(text: str) -> list:
    """扫描表达约束禁止字眼；返回 [{rule, word, line}]。"""
    banned = ("辅助生成", "自动生成", "暗示生成", "虚拟")
    hits = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for word in banned:
            if word in line:
                hits.append({"rule": "E-%d" % (banned.index(word) + 1),
                             "word": word, "line": idx})
    return hits


def build_parser():
    p = argparse.ArgumentParser(description="CCF 风格检查工具（macOS Vibrancy，PRD 11）")
    p.add_argument("--input", default=None, help="待检查文本")
    p.add_argument("--input-file", default=None, help="待检查文件路径")
    p.add_argument("--theme", choices=("light", "dark"), default="light", help="目标主题")
    p.add_argument("--expression", action="store_true", help="附带表达约束扫描")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.input is not None:
        text = args.input
    elif args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = ""
    report = lint_text(text, theme=args.theme, with_expression=args.expression)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())