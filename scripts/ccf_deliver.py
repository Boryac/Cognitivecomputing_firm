# CCF 交付分类与管线：类型识别、默认格式、文档管线、回退（PRD 7.4）。
# 写 delivery 记录（结构 per assets/delivery.template.yaml）。
"""CCF 交付：按产物类型路由交付管线（PRD 7.4）。

类型表见 7.4.1；文档管线 md -> 确认(H3) -> latex -> pdf（Word 需显式请求）；
格式转换失败回退默认格式（D-3）；许可声明与来源标注保留（D-4）。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from ccf_state import (format_id, load_template, now_iso, read_json_file,
                       resolve_root, state_file_path, write_json_file)

TYPES = ("document", "spreadsheet", "presentation", "code", "image", "data",
         "video_audio", "app_service", "mixed", "other")

DEFAULT_FORMATS = {
    "document": "pdf", "spreadsheet": "excel", "presentation": "pdf",
    "code": "source", "image": "png", "data": "json",
    "video_audio": "source", "app_service": "deploy",
    "mixed": "archive", "other": "default",
}

PIPELINES = {
    "document": "md -> confirm (H3) -> latex -> pdf",
    "document_word": "md -> confirm (H3) -> latex -> pdf + docx",
    "spreadsheet": "structure -> workbook -> excel",
    "presentation": "outline -> slides -> pdf",
    "code": "source -> build check -> source",
    "image": "source -> export check -> png",
    "data": "dataset -> wrap -> json",
    "video_audio": "assets -> packaging check -> source",
    "app_service": "build output -> deploy package",
    "mixed": "per-type pipelines -> archive",
    "other": "per contract",
}

CONFIRM_OPTIONS = ("approve", "approve+word", "revise", "reject")

TYPE_KEYWORDS = [
    ("document", ("文档", "报告", "文章", "论文", "markdown", "md ", "md源稿", "doc", "文档类")),
    ("spreadsheet", ("表格", "excel", "csv", "spreadsheet", "xlsx")),
    ("presentation", ("演示", "ppt", "slides", "幻灯片", "presentation", "deck")),
    ("code", ("代码", "程序", "script", "源码", "code", "软件", "库")),
    ("image", ("图片", "图像", "png", "svg", "jpg", "海报", "图")),
    ("data", ("数据", "dataset", "json", "数据集")),
    ("video_audio", ("视频", "音频", "video", "audio", "mp4", "mp3")),
    ("app_service", ("应用", "服务", "部署", "app", "service", "镜像", "deploy")),
    ("mixed", ("混合", "打包", "归档包", "mixed", "bundle")),
]


def classify_type(description: str, hint: str | None = None) -> dict:
    """识别交付物类型；有歧义（无法命中）时返回 other 并提示询问（D-5）。"""
    if hint and hint in TYPES:
        return {"type": hint, "classified": True, "ask_user": False}
    low = (description or "").lower()
    hits = []
    for t, kws in TYPE_KEYWORDS:
        if any(kw in low for kw in kws):
            hits.append(t)
    unique = sorted(set(hits))
    if len(unique) == 1:
        return {"type": unique[0], "classified": True, "ask_user": False}
    if len(unique) > 1:
        return {"type": unique[0], "classified": True, "ask_user": True,
                "note": "多类型命中 %s，默认取 %s，可显式指定" % ("/".join(unique), unique[0])}
    return {"type": "other", "classified": False, "ask_user": True,
            "note": "无法识别类型，需询问用户（PRD D-5）"}


def default_format(artifact_type: str) -> str:
    return DEFAULT_FORMATS.get(artifact_type, "default")


def pipeline_text(artifact_type: str, word: bool = False) -> str:
    if artifact_type == "document" and word:
        return PIPELINES["document_word"]
    return PIPELINES.get(artifact_type, PIPELINES["other"])


def check_license_notice(notice: str) -> dict:
    """保留许可声明检查（PRD D-4 / LS-1..LS-5）。"""
    low = notice or ""
    passed = "AGPL-3.0" in low and any(k in low for k in ("来源", "许可", "LICENSE", "license"))
    return {"passed": passed,
            "message": "许可声明与来源标注保留" if passed else "缺少 AGPL-3.0 声明或来源标注"}


def delivery_template() -> dict:
    return load_template("delivery.template.yaml")


def make_delivery(artifact_type: str, run_id: str, ticket_id: str,
                  artifact_ids: list, opts: dict) -> dict:
    """按类型与管线产出 delivery 记录。"""
    tpl = delivery_template()
    rec = {
        "delivery_id": opts.get("delivery_id") or format_id("DL", opts.get("seq", 1), 3),
        "run_id": run_id,
        "ticket_id": ticket_id,
        "artifact_ids": artifact_ids,
        "artifact_type": artifact_type,
        "default_format": default_format(artifact_type),
        "selected_format": opts.get("selected_format") or default_format(artifact_type),
        "pipeline": pipeline_text(artifact_type, word=opts.get("word", False)),
        "document_pipeline": {
            "source_ref": opts.get("source_md", ""),
            "confirm": opts.get("confirm") or ("approve" if artifact_type != "document" else ""),
            "confirm_at": None,
            "latex_ref": opts.get("latex", ""),
            "pdf_ref": opts.get("pdf", ""),
            "word_ref": opts.get("word", ""),
        },
        "format_conversion": {
            "used_skill": opts.get("used_skill", ""),
            "status": "ok",
            "fallback_to": "",
            "note": "",
        },
        "license_notice": "AGPL-3.0 — 见 LICENSE；来源与许可声明保留",
        "brand_logo": "透明底无字logo.png",
        "delivered_at": None,
        "version": 1,
    }

    # 许可声明检查
    lic = check_license_notice(opts.get("license_notice", rec["license_notice"]))
    rec["license_ok"] = lic["passed"]
    rec["license_message"] = lic["message"]

    # 文档类管线：md -> 确认 -> latex -> pdf（PRD 7.4.2 / D-5）
    if artifact_type == "document":
        confirm = opts.get("confirm", "")
        if confirm in CONFIRM_OPTIONS:
            rec["document_pipeline"]["confirm"] = confirm
            rec["document_pipeline"]["confirm_at"] = now_iso()
            if confirm in ("approve", "approve+word"):
                rec["document_pipeline"]["latex_ref"] = opts.get("latex", "latex 产物")
                rec["document_pipeline"]["pdf_ref"] = opts.get("pdf", "pdf 产物")
                if confirm == "approve+word":
                    rec["document_pipeline"]["word_ref"] = opts.get("word", "docx 产物")
                rec["selected_format"] = "pdf"
                rec["delivered_at"] = now_iso()
            elif confirm == "revise":
                rec["document_pipeline"]["pdf_ref"] = ""
                # revise：回退到 Specialist 环节修改
                rec["format_conversion"]["note"] = "revise：返回修改内容"
                rec["selected_format"] = ""
            elif confirm == "reject":
                # reject：回退到 SCOPE 阶段
                rec["format_conversion"]["note"] = "reject：回退到 SCOPE 阶段"
                rec["selected_format"] = ""
        else:
            rec["document_pipeline"]["confirm"] = ""
            rec["format_conversion"]["note"] = "等待格式确认（H3）"

    # 格式转换失败回退默认格式（PRD D-3 / R-32）
    conv = opts.get("conversion_status", "ok")
    if conv == "failed":
        rec["format_conversion"]["status"] = "failed"
        rec["format_conversion"]["fallback_to"] = default_format(artifact_type)
        rec["format_conversion"]["note"] = "转换失败，回退默认格式 %s" % rec["format_conversion"]["fallback_to"]
        rec["selected_format"] = default_format(artifact_type)
        rec["delivered_at"] = now_iso()
    elif conv == "fallback":
        rec["format_conversion"]["status"] = "fallback"
        rec["format_conversion"]["fallback_to"] = default_format(artifact_type)
        rec["format_conversion"]["note"] = "已回退默认格式"
    else:
        rec["format_conversion"]["status"] = "ok"

    if rec.get("delivered_at") is None and artifact_type != "document":
        rec["delivered_at"] = now_iso()
    return rec


def build_parser():
    p = argparse.ArgumentParser(description="CCF 交付路由工具（PRD 7.4）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录")
    p.add_argument("--type", default=None, choices=TYPES, help="显式产物类型")
    p.add_argument("--describe", default=None, help="产物描述（用于类型识别）")
    p.add_argument("--run-id", default="CCF-YYYY-MM-DD-NNN")
    p.add_argument("--ticket-id", default="T-001")
    p.add_argument("--artifact-ids", default="A-001", help="逗号分隔的 artifact 列表")
    p.add_argument("--confirm", default=None, choices=CONFIRM_OPTIONS, help="文档格式确认")
    p.add_argument("--source-md", default="", help="MD 源稿引用")
    p.add_argument("--latex", default="", help="LaTeX 产物引用")
    p.add_argument("--pdf", default="", help="PDF 产物引用")
    p.add_argument("--word", default="", help="Word 产物引用")
    p.add_argument("--used-skill", default="", help="格式转换协同 Skill")
    p.add_argument("--conversion-status", default="ok", choices=("ok", "failed", "fallback"),
                   help="格式转换结果")
    p.add_argument("--license-notice", default=None, help="许可声明文本（校验用）")
    p.add_argument("--delivery-id", default=None)
    p.add_argument("--save", action="store_true", help="写 state/deliveries.json")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cls = classify_type(args.describe or "", args.type)
        if cls["ask_user"] and args.type is None:
            pass  # 类型识别结果继续，note 中提示询问（D-5）
        artifact_ids = [s.strip() for s in args.artifact_ids.split(",") if s.strip()]
        seq = 1
        if args.save and args.state_dir:
            prev = read_json_file(state_file_path(args.state_dir, "deliveries.json"))
            seq = (len(prev) if isinstance(prev, list) else 0) + 1
        rec = make_delivery(cls["type"], args.run_id, args.ticket_id, artifact_ids, {
            "seq": seq, "confirm": args.confirm, "source_md": args.source_md,
            "latex": args.latex, "pdf": args.pdf, "word": args.word,
            "used_skill": args.used_skill, "conversion_status": args.conversion_status,
            "license_notice": args.license_notice, "delivery_id": args.delivery_id,
        })
        if args.save:
            records = read_json_file(state_file_path(args.state_dir, "deliveries.json"))
            if not isinstance(records, list):
                records = []
            records.append(rec)
            write_json_file(state_file_path(args.state_dir, "deliveries.json"), records)
        report = {"report": "delivery", "classification": cls, "delivery": rec,
                  "saved": args.save}
    except (OSError, ValueError) as exc:
        report = {"report": "delivery-error", "ok": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())