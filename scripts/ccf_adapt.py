# CCF 画像更新与适配：读 state/profile.json，分级应用适配、回滚、重置（PRD 13.6、15）。
# 黑名单拦截：style_law 等核心规则永不自动修改（PRD L-4、G11）。
"""CCF 学习适配：用户画像版本管理、D0-D4 分级应用与黑名单拦截。

D0-D1 自动应用；D2 自动应用+审计；D3 需人工确认；D4 需人工决策（PRD 9.1、15）。
历史快照存 state/profile_history.json 支持 --rollback。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import re

from ccf_state import (append_event, format_id, now_iso, profile_template,
                       read_json_file, resolve_root, state_file_path, write_json_file)

BLACKLIST = (
    "style_law", "expression_constraint", "license",
    "organization_hierarchy", "gate_veto", "h_point_structure",
    "security_compliance",
)
BLACKLIST_CN = ("风格法", "表达约束", "许可", "组织架构", "否决权", "人工干涉点", "安全合规")

LEVELS = ("D0", "D1", "D2", "D3", "D4")


def profile_path(root: str | None = None) -> str:
    return state_file_path(root, "profile.json")


def history_path(root: str | None = None) -> str:
    return state_file_path(root, "profile_history.json")


def load_profile(root: str | None = None) -> dict:
    data = read_json_file(profile_path(root))
    if not data:
        data = profile_template()
        data["version"] = "P-0"
        data["created_at"] = now_iso()
        data["updated_at"] = now_iso()
        data["adaptations"] = []
        write_json_file(profile_path(root), data)
    data.setdefault("preferences", profile_template().get("preferences", {}))
    data.setdefault("adaptations", [])
    data.setdefault("blacklist", list(BLACKLIST))
    return data


def save_profile(root: str | None, profile: dict, snapshot: bool = False) -> dict:
    profile["updated_at"] = now_iso()
    if snapshot:
        _push_history(root, profile)
    write_json_file(profile_path(root), profile)
    return profile


def _push_history(root: str | None, profile: dict) -> None:
    """把变更前的画像快照写入历史（用于回滚到上一版本）。"""
    history = read_json_file(history_path(root))
    if not isinstance(history, list):
        history = []
    history.append({"version": profile.get("version", "P-0"), "saved_at": now_iso(),
                    "profile": json.loads(json.dumps(profile, ensure_ascii=False))})
    write_json_file(history_path(root), history)


def next_version(version: str) -> str:
    m = re.match(r"^P-(\d+)$", version or "P-0")
    n = int(m.group(1)) if m else 0
    return "P-%d" % (n + 1)


def blacklisted(mtype: str, description: str) -> str | None:
    """判断适配是否触碰黑名单；命中返回黑名单项。"""
    low = (mtype or "") + " " + (description or "")
    low_en = low.lower()
    for item in BLACKLIST:
        if item in low_en:
            return item
    for item in BLACKLIST_CN:
        if item in low:
            return item
    return None


def add_adaptation(root: str | None, mtype: str, description: str, level: str,
                   confirm: str | None = None, decision: str | None = None,
                   change: dict | None = None) -> dict:
    """追加一条适配并按决策级应用；返回更新后的 profile 与适配记录。"""
    if level not in LEVELS:
        raise ValueError("level 仅支持 D0-D4")
    profile = load_profile(root)
    blocked = blacklisted(mtype, description)
    adapt_id = format_id("AD", len(profile.get("adaptations", [])) + 1, 4)
    entry = {
        "adapt_id": adapt_id,
        "type": mtype,
        "description": description,
        "applied_at": None,
        "level": level,
        "status": "blocked" if blocked else "pending",
        "blocked_by": blocked,
    }

    if blocked:
        entry["status"] = "blocked"
        entry["note"] = "黑名单项 %s：核心规则永不自动修改" % blocked
        profile.setdefault("adaptations", []).append(entry)
        save_profile(root, profile)
        append_event(root, "LEARNING_GATE_BLOCKED", {"adapt_id": adapt_id, "blocked_by": blocked})
        return {"profile": profile, "adaptation": entry}

    if level in ("D0", "D1"):
        _push_history(root, profile)  # 变更前快照
        entry["status"] = "active"
        entry["applied_at"] = now_iso()
        _apply_change(profile, change)
        profile["version"] = next_version(profile.get("version", "P-0"))
    elif level == "D2":
        _push_history(root, profile)
        entry["status"] = "active"
        entry["applied_at"] = now_iso()
        entry["audit_required"] = True
        _apply_change(profile, change)
        profile["version"] = next_version(profile.get("version", "P-0"))
    elif level == "D3":
        if confirm == "approve":
            _push_history(root, profile)
            entry["status"] = "active"
            entry["applied_at"] = now_iso()
            _apply_change(profile, change)
            profile["version"] = next_version(profile.get("version", "P-0"))
        else:
            entry["status"] = "pending_confirmation"
            entry["note"] = "D3 需人工确认（H2）"
    else:  # D4
        if decision == "approve":
            _push_history(root, profile)
            entry["status"] = "active"
            entry["applied_at"] = now_iso()
            _apply_change(profile, change)
            profile["version"] = next_version(profile.get("version", "P-0"))
        else:
            entry["status"] = "pending_decision"
            entry["note"] = "D4 需人工决策（H4）"

    profile.setdefault("adaptations", []).append(entry)
    save_profile(root, profile)
    if entry["status"] == "active":
        append_event(root, "LEARNING_ADAPT_APPLIED", {"adapt_id": adapt_id, "level": level})
    return {"profile": profile, "adaptation": entry}


def _apply_change(profile: dict, change: dict | None) -> None:
    """把适配变更落地到 preferences（generic set）。"""
    if not change:
        return
    prefs = profile.setdefault("preferences", {})
    for key, value in change.items():
        if key in ("delivery_default_format", "theme_preference", "task_granularity"):
            prefs[key] = value
        elif key == "individual_weight":
            w = prefs.setdefault("individual_weight", {})
            if isinstance(value, dict):
                for code, wv in value.items():
                    w[code] = wv
            elif isinstance(value, list):
                for code in value:
                    w.setdefault(code, 1)
        elif key == "terminology_preference":
            term = prefs.setdefault("terminology_preference", [])
            if isinstance(value, list):
                for t in value:
                    if t not in term:
                        term.append(t)
        else:
            prefs[key] = value


def rollback(root: str | None = None) -> dict:
    """回滚到上一版本画像；恢复最近一次变更前的快照。"""
    history = read_json_file(history_path(root))
    if not isinstance(history, list) or not history:
        current = load_profile(root)
        return {"rolled_back": False, "message": "历史为空，无法回滚",
                "profile": current}
    prev = history[-1]  # 变更前快照（version 为上一版本）
    profile = json.loads(json.dumps(prev["profile"], ensure_ascii=False))
    write_json_file(profile_path(root), profile)
    write_json_file(history_path(root), history[:-1])
    append_event(root, "LEARNING_PROFILE_ROLLED_BACK", {"version": profile.get("version")})
    return {"rolled_back": True, "version": profile.get("version"), "profile": profile}


def reset(root: str | None = None) -> dict:
    """重置画像到 P-0（模板结构）。"""
    profile = profile_template()
    profile["version"] = "P-0"
    profile["created_at"] = now_iso()
    profile["updated_at"] = now_iso()
    profile["adaptations"] = []
    write_json_file(profile_path(root), profile)
    write_json_file(history_path(root), [])
    append_event(root, "LEARNING_PROFILE_RESET", {})
    return {"reset": True, "profile": profile}


def build_parser():
    p = argparse.ArgumentParser(description="CCF 画像更新与适配工具（PRD 13.6、15）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录")
    sub = p.add_subparsers(dest="command", required=True)
    pv = sub.add_parser("view", help="查看画像")
    pa = sub.add_parser("add", help="追加适配")
    pa.add_argument("--type", required=True, help="适配类型")
    pa.add_argument("--description", required=True, help="适配描述")
    pa.add_argument("--level", required=True, choices=LEVELS, help="决策级")
    pa.add_argument("--confirm", default=None, choices=("approve",), help="D3 人工确认")
    pa.add_argument("--decision", default=None, choices=("approve",), help="D4 人工决策")
    pa.add_argument("--set", default=None, action="append", help="适配变更 key=value，可多次")
    pr = sub.add_parser("rollback", help="回滚上一版本")
    pn = sub.add_parser("reset", help="重置画像")
    return p


def _parse_sets(items) -> dict:
    change = {}
    for raw in items or []:
        if "=" not in raw:
            raise ValueError("--set 格式应为 key=value")
        k, v = raw.split("=", 1)
        if v.startswith("[") or v.startswith("{"):
            v = json.loads(v)
        try:
            change[k] = int(v)
        except (TypeError, ValueError):
            change[k] = v
    return change


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "view":
            report = {"report": "profile-view", "profile": load_profile(args.state_dir)}
        elif args.command == "add":
            out = add_adaptation(args.state_dir, args.type, args.description, args.level,
                                 args.confirm, args.decision, _parse_sets(args.set))
            report = {"report": "profile-add", "adaptation": out["adaptation"],
                      "version": out["profile"].get("version")}
        elif args.command == "rollback":
            out = rollback(args.state_dir)
            report = {"report": "profile-rollback", **out}
        else:  # reset
            out = reset(args.state_dir)
            report = {"report": "profile-reset", **out}
    except (OSError, ValueError) as exc:
        report = {"report": "profile-error", "ok": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())