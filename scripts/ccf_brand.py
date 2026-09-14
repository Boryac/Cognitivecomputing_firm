# CCF 品牌落地：标识与公司名称的生成、应用与校验（PRD 3.3 / references/brand.md）。
# 供 TURN 步 11（BRAND）生成品牌块，供 G9 交付门校验品牌是否真的落地。
"""CCF 品牌：把品牌从"文档里的规范"变成"执行链里的步骤"。

为什么需要本脚本：品牌此前只存在于 references/brand.md（惰性加载）与若干被动
字段中，运行期既无强制步骤，也无门禁可判定，导致交付物经常遗漏标识与公司名。
本脚本提供三件事：

  block  生成标准品牌块（text / md / latex）；带 --out-dir 时把标识复制为
         ASCII 名 brand-logo.png，规避中文文件名在 LaTeX/DOCX 管线中的坑。
  check  校验交付物文本是否已应用标识与公司名称；返回可判定结论，供 G9 使用。
  logo   校验标识文件（存在性、尺寸、透明底、SHA-256）。

规则：BR-1..BR-6（见 references/brand.md 第 6、7 节）。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys

from ccf_state import now_iso

BRAND_NAME = "弈策集团"
BRAND_LEGAL = "Yestest Holdings Limited"
BRAND_DISPLAY = "%s（%s）" % (BRAND_NAME, BRAND_LEGAL)
SKILL_NAME = "cognitivecomputing-firm"

# 包根展示名（文件系统中的真实文件名）
LOGO_SOURCE = "透明底无字logo.png"
# 交付物内的 ASCII 引用名（复制后使用，规避中文路径问题）
LOGO_REF_NAME = "brand-logo.png"

# 图片标识不适用、以名称标注代替的交付物类型
NAME_ONLY_TYPES = ("code", "data", "other")

MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+\.(?:png|svg|jpg|jpeg|webp))\)", re.IGNORECASE)
HTML_IMG_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+\.(?:png|svg|jpg|jpeg|webp))[\"']", re.IGNORECASE)
TEX_IMG_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")

BRAND_NAME_HINTS = (BRAND_NAME, BRAND_LEGAL, "Yestest")


def skill_root() -> str:
    """本脚本位于 <skill>/scripts/ 下，向上两级即技能包根。"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def logo_source_path(root: str | None = None) -> str:
    return os.path.join(root or skill_root(), LOGO_SOURCE)


def _png_head(path: str) -> dict:
    """读取 PNG 头，返回宽高与颜色类型（不依赖第三方库）。"""
    try:
        with open(path, "rb") as fh:
            head = fh.read(26)
    except OSError:
        return {}
    if len(head) < 26 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return {}
    width = int.from_bytes(head[16:20], "big")
    height = int.from_bytes(head[20:24], "big")
    color_type = head[25]
    return {"width": width, "height": height, "color_type": color_type,
            "has_alpha": color_type in (4, 6)}


def sha256_of(path: str) -> str:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return ""


def logo_report(root: str | None = None) -> dict:
    """校验标识文件；返回 {exists, path, width, height, has_alpha, sha256}。"""
    path = logo_source_path(root)
    info = {"report": "brand-logo", "path": path, "exists": os.path.isfile(path),
            "filename": LOGO_SOURCE, "ref_name": LOGO_REF_NAME}
    if not info["exists"]:
        info["passed"] = False
        info["message"] = "标识文件缺失：%s" % LOGO_SOURCE
        return info
    head = _png_head(path)
    info.update(head)
    info["sha256"] = sha256_of(path)
    info["size_bytes"] = os.path.getsize(path)
    ok = bool(head) and head.get("has_alpha", False) and head.get("width", 0) > 0
    info["passed"] = ok
    info["message"] = ("标识正常（%sx%s，含透明通道）" % (head.get("width"), head.get("height"))
                      if ok else "标识异常：非 PNG 或缺少透明通道")
    return info


def find_brand(text: str) -> dict:
    """在文本中查找公司名称与标识引用。"""
    body = text or ""
    name_found = any(h in body for h in BRAND_NAME_HINTS)
    refs = []
    for rx in (MD_IMG_RE, HTML_IMG_RE, TEX_IMG_RE):
        refs.extend(m.group(1).strip() for m in rx.finditer(body))
    logo_hits = [r for r in refs
                 if "brand-logo" in r.lower() or LOGO_SOURCE in r]
    return {"name_found": name_found, "logo_found": bool(logo_hits),
            "logo_refs": logo_hits, "all_image_refs": refs}


def check_text(text: str, artifact_type: str = "document",
               require_logo: bool | None = None) -> dict:
    """校验文本是否已应用品牌；返回可判定结论（G9 使用）。

    require_logo 为 None 时按类型推导：code/data/other 只要求名称标注。
    """
    if require_logo is None:
        require_logo = artifact_type not in NAME_ONLY_TYPES
    found = find_brand(text)
    violations = []
    if not found["name_found"]:
        violations.append({"rule": "BR-3", "message": "缺少公司名称标注（%s / %s）" % (BRAND_NAME, BRAND_LEGAL)})
    if require_logo and not found["logo_found"]:
        violations.append({"rule": "BR-2", "message": "缺少标识引用（应为 %s 或 %s）" % (LOGO_REF_NAME, LOGO_SOURCE)})
    return {
        "report": "brand-check",
        "artifact_type": artifact_type,
        "require_logo": require_logo,
        "name_found": found["name_found"],
        "logo_found": found["logo_found"],
        "logo_refs": found["logo_refs"],
        "violations": violations,
        "passed": len(violations) == 0,
        "checked_at": now_iso(),
    }


def render_block(fmt: str, logo_ref: str = LOGO_REF_NAME, placed: bool = False) -> str:
    """生成标准品牌块。placed=True 表示标识已就位，可安全引用。"""
    if fmt == "text":
        return "%s · %s" % (BRAND_DISPLAY, SKILL_NAME)
    if fmt == "latex":
        if placed:
            return ("\\includegraphics[width=0.06\\textwidth]{%s}\\\\[2pt]\n"
                    "\\textbf{%s}" % (logo_ref, BRAND_DISPLAY))
        return "\\textbf{%s}" % BRAND_DISPLAY
    # md（默认）
    if placed:
        return "![%s](%s)\n\n**%s** · %s" % (BRAND_NAME, logo_ref, BRAND_DISPLAY, SKILL_NAME)
    return "**%s** · %s" % (BRAND_DISPLAY, SKILL_NAME)


def place_logo(out_dir: str, root: str | None = None) -> dict:
    """把标识复制为 ASCII 名，规避中文文件名在 LaTeX/DOCX 管线中的解析问题。"""
    src = logo_source_path(root)
    if not os.path.isfile(src):
        return {"placed": False, "target": "", "message": "标识源文件缺失：%s" % src}
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, LOGO_REF_NAME)
    try:
        shutil.copyfile(src, dst)
    except OSError as exc:
        return {"placed": False, "target": dst, "message": "复制失败：%s" % exc}
    return {"placed": True, "target": dst, "message": "标识已就位（ASCII 名）"}


def build_parser():
    p = argparse.ArgumentParser(description="CCF 品牌落地工具（PRD 3.3 / brand.md）")
    p.add_argument("--skill-root", default=None, help="技能包根目录（默认自动推断）")
    sub = p.add_subparsers(dest="command", required=True)

    pb = sub.add_parser("block", help="生成标准品牌块")
    pb.add_argument("--format", choices=("text", "md", "latex"), default="md")
    pb.add_argument("--out-dir", default=None, help="交付物所在目录；给出时复制标识为 brand-logo.png")
    pb.add_argument("--logo-ref", default=LOGO_REF_NAME, help="品牌块中引用的标识名")

    pc = sub.add_parser("check", help="校验文本是否已应用品牌（G9 使用）")
    pc.add_argument("--input", default=None, help="待校验文本")
    pc.add_argument("--input-file", default=None, help="待校验文件路径")
    pc.add_argument("--artifact-type", default="document",
                    choices=("document", "spreadsheet", "presentation", "code", "image",
                             "data", "video_audio", "app_service", "mixed", "other"))
    pc.add_argument("--require-logo", dest="require_logo", action="store_true", default=None)
    pc.add_argument("--no-logo", dest="require_logo", action="store_false")

    sub.add_parser("logo", help="校验标识文件（尺寸、透明通道、哈希）")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "block":
            placed = False
            placement = None
            if args.out_dir:
                placement = place_logo(args.out_dir, args.skill_root)
                placed = placement["placed"]
            report = {
                "report": "brand-block",
                "format": args.format,
                "block": render_block(args.format, args.logo_ref, placed=placed),
                "logo_placed": placed,
                "placement": placement,
                "brand": {"name": BRAND_NAME, "legal_name": BRAND_LEGAL,
                          "display": BRAND_DISPLAY, "logo": LOGO_SOURCE,
                          "logo_ref": args.logo_ref},
                "generated_at": now_iso(),
            }
        elif args.command == "check":
            if args.input is not None:
                text = args.input
            elif args.input_file:
                with open(args.input_file, "r", encoding="utf-8") as fh:
                    text = fh.read()
            else:
                text = ""
            report = check_text(text, args.artifact_type, args.require_logo)
        else:  # logo
            report = logo_report(args.skill_root)
    except (OSError, ValueError) as exc:
        report = {"report": "brand-error", "ok": False, "passed": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("passed", report.get("logo_placed", False)) else 1


if __name__ == "__main__":
    sys.exit(main())
