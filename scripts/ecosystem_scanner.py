# CCF Skill 生态扫描：遍历已安装 Skill、提取清单、计算匹配度（PRD 5.1、5.5）。
# 写 state/ecosystem.json（结构 per PRD 5.5.1）。
"""CCF 生态扫描：读取已安装 Skill 清单，按任务 scope 计算匹配度与分级。

匹配规则见 PRD 5.1.3（产出类型 + 能力标签 + 许可兼容性），
分级：>=80 recommended / 50-79 on_demand / <50 disabled（5.3.1）。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from ccf_state import (now_iso, parse_simple_yaml, read_json_file, state_file_path,
                       write_json_file)

COMPATIBLE_LICENSES = ("agpl-3.0", "agpl", "gpl-3.0", "gpl", "mit", "bsd")


def _clean(item: str) -> str:
    return (item or "").strip().lower()


def license_status(license_text: str) -> dict:
    """AGPL-3.0 兼容性判定（PRD 5.4）。"""
    low = _clean(license_text)
    if not low:
        return {"compat": "review", "note": "未声明许可，需人工复核"}
    if any(marker in low for marker in ("proprietary", "closed-source", "commercial",
                                        "all rights reserved", "arr")):
        return {"compat": "high_risk", "note": "闭源/专有许可，禁止自动纳入协同池"}
    if low.startswith(COMPATIBLE_LICENSES):
        return {"compat": "compatible", "note": "与 AGPL-3.0 兼容，可自动联动"}
    if "apache" in low or "cc-by" in low or "cc0" in low:
        return {"compat": "review", "note": "非明确兼容，需人工复核"}
    return {"compat": "review", "note": "许可待复核"}


def read_manifest(manifest_path: str) -> dict:
    """读取 skill 的 manifest.yaml；缺失时回退为空字典。"""
    if not os.path.exists(manifest_path):
        return {}
    with open(manifest_path, "r", encoding="utf-8") as fh:
        return parse_simple_yaml(fh.read())


def load_skills(skills_dir: str | None = None, skills_json: str | None = None) -> list:
    """产出 [{id, path, manifest}] 列表。"""
    skills = []
    if skills_json:
        items = json.loads(skills_json)
        for it in items:
            if isinstance(it, str):
                p = it
                m = read_manifest(p) if os.path.isfile(p) else {}
                sid = (m.get("name") or os.path.basename(os.path.dirname(p) or p) or "skill")
                skills.append({"id": sid, "path": p, "manifest": m})
            elif isinstance(it, dict):
                m = dict(it.get("manifest", {}))
                sid = it.get("id") or m.get("name") or "skill"
                skills.append({"id": sid, "path": it.get("path", ""), "manifest": m})
        return skills
    if skills_dir and os.path.isdir(skills_dir):
        for name in sorted(os.listdir(skills_dir)):
            sub = os.path.join(skills_dir, name)
            if not os.path.isdir(sub):
                continue
            manifest_path = os.path.join(sub, "manifest.yaml")
            if not os.path.exists(manifest_path):
                manifest_path = os.path.join(sub, "manifest.yml")
            manifest = read_manifest(manifest_path) if os.path.exists(manifest_path) else {}
            sid = manifest.get("name") or name
            skills.append({"id": sid, "path": sub, "manifest": manifest})
    return skills


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [v.strip() for v in value.replace("，", ",").split(",") if v.strip()]
    if isinstance(value, dict):
        out = []
        for sub in value.values():
            out.extend(_as_list(sub))
        return out
    return []


def describe_skill(manifest: dict) -> str:
    """把 manifest 的标签与描述拼成文本串，用于关键词匹配。"""
    parts = [manifest.get("description", "")]
    parts.extend(_as_list(manifest.get("tags")))
    caps = manifest.get("capabilities", {})
    parts.extend(_as_list(caps.get("required", [])) if isinstance(caps, dict) else _as_list(caps))
    parts.extend(_as_list(manifest.get("inputs", [])))
    parts.extend(_as_list(manifest.get("outputs", [])))
    return " ".join(str(p) for p in parts if p)


def match_score(scope: dict, manifest: dict) -> int:
    """按 PRD 5.1.3 计算匹配度（0-100）。"""
    domain = [str(k) for k in _as_list(scope.get("domain", []))]
    capabilities = [str(k) for k in _as_list(scope.get("core_capabilities", []))]
    output_type = str(scope.get("output_type", "") or "").lower()
    text = describe_skill(manifest).lower()

    score = 0.0
    # 1. 领域/标签重叠（0-60）
    if domain:
        hits = sum(1 for k in domain if k.lower() in text)
        score += 60.0 * (hits / len(domain))
    # 2. 核心能力重叠（0-25）
    if capabilities:
        hits = sum(1 for k in capabilities if k.lower() in text)
        score += 25.0 * (hits / len(capabilities))
    # 3. 产出类型匹配（0-15）
    if output_type and output_type in text:
        score += 15.0
    return int(round(score))


def level_of(score: int) -> str:
    if score >= 80:
        return "recommended"
    if score >= 50:
        return "on_demand"
    return "disabled"


def call_point_of(manifest: dict, default: str = "verify") -> str:
    """按能力关键字映射调用节点（PRD 5.3.2）。"""
    text = describe_skill(manifest).lower()
    if any(k in text for k in ("校验", "检查", "lint", "review", "validate", "check")):
        return "gate"
    if any(k in text for k in ("格式", "转换", "convert", "format", "pdf", "excel")):
        return "integrate"
    if any(k in text for k in ("分析", "拆解", "analy", "research", "enhance")):
        return "scope_plan"
    if any(k in text for k in ("内容", "写作", "write", "create", "draft")):
        return "execute"
    return default


def scan(scope: dict, skills_dir: str | None = None, skills_json: str | None = None) -> dict:
    """全量扫描并输出 ecosystem.json 结构。"""
    skills = load_skills(skills_dir, skills_json)
    result = {"scan_time": now_iso(), "total_installed": len(skills), "skills": {}}
    for skill in skills:
        manifest = skill.get("manifest", {}) or {}
        sid = skill["id"]
        lic = license_status(manifest.get("license", ""))
        score = match_score(scope, manifest)
        level = level_of(score)
        if lic["compat"] == "high_risk" and level == "recommended":
            level = "disabled"
        in_pool = level == "recommended" and lic["compat"] == "compatible"
        result["skills"][sid] = {
            "name": manifest.get("name", sid),
            "version": manifest.get("version"),
            "license": manifest.get("license", ""),
            "license_compat": lic,
            "match_score": score,
            "level": level,
            "in_pool": in_pool,
            "call_point": call_point_of(manifest),
            "calls": [],
            "failed_streak": 0,
        }
    return result


def save_ecosystem(root: str | None, data: dict) -> dict:
    write_json_file(state_file_path(root, "ecosystem.json"), data)
    return data


def build_parser():
    p = argparse.ArgumentParser(description="CCF Skill 生态扫描工具（PRD 5.1）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录")
    p.add_argument("--skills-dir", default=None, help="已安装 Skill 目录")
    p.add_argument("--skills-json", default=None, help="Skill manifest 路径/对象列表（JSON）")
    p.add_argument("--scope-json", default=None,
                   help="任务 scope（JSON: domain/output_type/core_capabilities）")
    p.add_argument("--scope-file", default=None, help="scope JSON 文件路径")
    p.add_argument("--no-save", action="store_true", help="不写 state/ecosystem.json")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        scope = {}
        if args.scope_file:
            scope = read_json_file(args.scope_file)
        if args.scope_json:
            scope = json.loads(args.scope_json)
        data = scan(scope, args.skills_dir, args.skills_json)
        if not args.no_save:
            save_ecosystem(args.state_dir, data)
        report = {"report": "ecosystem-scan", "scope": scope,
                  "scan_time": data["scan_time"], "total_installed": data["total_installed"],
                  "skills": data["skills"], "saved": not args.no_save}
    except (OSError, ValueError) as exc:
        report = {"report": "ecosystem-error", "ok": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())