# CCF grill-me 联动探测与记录：探测、决策状态机、调用记录（PRD 5.2）。
# 写 state/integration.json（结构 per assets/integration.template.yaml）。
"""CCF grill-me 联动：探测、安装提示、真实调用与失败降级。

决策状态机：installed / declined / later / install_pending /
install_failed / unconfirmed / disabled；连续 3 次失败自动停用（PRD F-5）。

真实调用（PRD 5.2.4）：提供 --invoke-cmd 时以子进程真实执行 grill-me 并取回结果；
否则把调用信封写入 run_state/state/outbox.jsonl，交宿主编排层通过原生 Skill 工具
执行后回执。不再伪造 "ok"。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys

from ccf_state import (append_event, ensure_dir, format_id, load_template,
                       now_iso, read_json_file, resolve_root, state_file_path,
                       write_json_file)

INSTALL_COMMAND = "npx skills add mattpocock/skills/grill-me"
TARGET = "grill_me"
NAME_VARIANTS = ("grill-me", "grill_me", "GrillMe")

DECISIONS = ("null", "installed", "declined", "later", "install_pending",
             "install_failed", "unconfirmed", "disabled")


def integration_path(root: str | None = None) -> str:
    return state_file_path(root, "integration.json")


def integration_template() -> dict:
    return load_template("integration.template.yaml")


def load_integration(root: str | None = None) -> dict:
    """读取联动状态；缺失时按模板结构返回初始值。"""
    data = read_json_file(integration_path(root))
    tpl = integration_template()
    entry = tpl.get(TARGET, {})
    if TARGET in data and isinstance(data[TARGET], dict):
        entry = data[TARGET]
    merged = dict(entry)
    merged.setdefault("install", entry.get("install", {}))
    merged.setdefault("calls", entry.get("calls", []))
    merged.setdefault("failed_streak", entry.get("failed_streak", 0))
    # 模板中的取值说明行不被当作合法状态值
    if merged.get("decision") not in DECISIONS:
        merged["decision"] = "null"
    inst = merged["install"]
    if inst.get("user_reply") not in ("done", "failed", "skip", "null", None):
        inst["user_reply"] = None
    if inst.get("reprobe_result") not in ("found", "not_found", "null", None):
        inst["reprobe_result"] = None
    return {TARGET: merged}


def save_integration(root: str | None, data: dict) -> dict:
    write_json_file(integration_path(root), data)
    return data


def normalize_name(name: str) -> str:
    return re.sub(r"[-_ ]", "", (name or "").lower())


def detect_grill_me(items: list) -> dict | None:
    """在已安装 Skill 列表中匹配 grill-me（含大小写与连字符变体）。"""
    target = normalize_name("grill-me")
    for item in items:
        if isinstance(item, dict):
            name = item.get("name", "") or item.get("id", "")
            version = item.get("version")
            entry = item.get("manifest", {}) or {}
            entry_name = entry.get("name", "")
            if normalize_name(name) == target or normalize_name(entry_name) == target:
                return {"installed": True, "version": version or entry.get("version") or None,
                        "id": item.get("id") or name}
        elif isinstance(item, str):
            if normalize_name(item) == target:
                return {"installed": True, "version": None, "id": item}
    return None


def scan_skills_dir(skills_dir: str) -> list:
    """扫描目录下子目录，提取 skill 名（读 manifest.yaml 或目录名）。"""
    out = []
    if not os.path.isdir(skills_dir):
        return out
    for name in sorted(os.listdir(skills_dir)):
        sub = os.path.join(skills_dir, name)
        if not os.path.isdir(sub):
            continue
        entry = {"id": name, "name": name}
        for manifest_name in ("manifest.yaml", "manifest.yml", "SKILL.md"):
            p = os.path.join(sub, manifest_name)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as fh:
                    text = fh.read()
                m = re.search(r"^\s*name:\s*(.+)$", text, re.MULTILINE)
                if m:
                    entry["name"] = m.group(1).strip().strip('"').strip("'")
                v = re.search(r"^\s*version:\s*(.+)$", text, re.MULTILINE)
                if v:
                    entry["version"] = v.group(1).strip().strip('"').strip("'")
                break
        out.append(entry)
    return out


def probe(root: str | None, skills: list, probed_at: str | None = None) -> dict:
    """执行探测；匹配成功进入 installed，失败保持待提示状态。"""
    data = load_integration(root)
    entry = data[TARGET]
    entry["probed_at"] = probed_at or now_iso()
    hit = detect_grill_me(skills)
    if hit:
        entry["installed"] = True
        entry["version"] = hit.get("version")
        entry["license"] = entry.get("license", "see grill-me repository")
        if entry.get("decision") in (None, "null", "unconfirmed", "install_failed", "declined", "later"):
            entry["decision"] = "installed"
        append_event(root, "INTEGRATION_FOUND", {"version": entry.get("version")})
    else:
        entry["installed"] = False
        entry["version"] = None
        append_event(root, "INTEGRATION_MISSING", {})
    save_integration(root, data)
    append_event(root, "INTEGRATION_PROBED", {"installed": entry["installed"]})
    return data


def decide(root: str | None, choice: str) -> dict:
    """处理用户对安装提示的回复：install / decline / later。"""
    data = load_integration(root)
    entry = data[TARGET]
    entry.setdefault("install", {})
    entry["install"]["command"] = INSTALL_COMMAND
    if choice == "install":
        entry["decision"] = "install_pending"
        entry["install"]["prompted_at"] = entry["install"].get("prompted_at") or now_iso()
        append_event(root, "INTEGRATION_INSTALL_STARTED", {})
    elif choice == "decline":
        entry["decision"] = "declined"
        append_event(root, "INTEGRATION_DECLINED", {})
    elif choice == "later":
        entry["decision"] = "later"
        append_event(root, "INTEGRATION_LATER", {})
    else:
        raise ValueError("choice 仅支持 install / decline / later")
    save_integration(root, data)
    return data


def apply_install_reply(root: str | None, reply: str, skills: list | None = None) -> dict:
    """处理安装命令执行后的回复：done / failed / skip。"""
    if reply not in ("done", "failed", "skip"):
        raise ValueError("reply 仅支持 done / failed / skip")
    data = load_integration(root)
    entry = data[TARGET]
    entry.setdefault("install", {})
    entry["install"]["command"] = INSTALL_COMMAND
    entry["install"]["user_reply"] = reply
    if reply == "done":
        entry["install"]["reprobed"] = True
        hit = detect_grill_me(skills or [])
        if hit:
            entry["installed"] = True
            entry["version"] = hit.get("version")
            entry["decision"] = "installed"
            entry["install"]["reprobe_result"] = "found"
            append_event(root, "INTEGRATION_INSTALLED", {"version": entry.get("version")})
        else:
            entry["decision"] = "unconfirmed"
            entry["install"]["reprobe_result"] = "not_found"
            append_event(root, "INTEGRATION_INSTALL_UNCONFIRMED", {})
    elif reply == "failed":
        entry["decision"] = "install_failed"
        entry["install"]["reprobe_result"] = entry["install"].get("reprobe_result")
        append_event(root, "INTEGRATION_INSTALL_FAILED", {})
    else:  # skip
        entry["install"]["reprobe_result"] = entry["install"].get("reprobe_result")
        if entry.get("decision") in ("install_pending", "null"):
            entry["decision"] = "unconfirmed"
        append_event(root, "INTEGRATION_LATER", {"reason": "skip"})
    save_integration(root, data)
    return data


def _invoke_real(root: str | None, envelope: dict, invoke_cmd=None,
                 timeout: int = 30) -> tuple:
    """真实调用 grill-me；返回 (result, detail)。result ∈ {ok, failed, dispatched}。

    - invoke_cmd 提供时：子进程真实执行（shell=False），按返回码判定；
    - 未提供时：写入 outbox.jsonl，交宿主回执（dispatched）。
    """
    if invoke_cmd:
        argv = shlex.split(invoke_cmd) if isinstance(invoke_cmd, str) else list(invoke_cmd)
        try:
            proc = subprocess.run(argv, shell=False, capture_output=True, text=True,
                                  timeout=timeout)
            out = (proc.stdout or "").strip()
            err = (proc.stderr or "").strip()
            ok = proc.returncode == 0
            return ("ok" if ok else "failed",
                    "rc=%d; out=%s; err=%s" % (proc.returncode, out[:800], err[:400]))
        except subprocess.TimeoutExpired:
            return ("failed", "timeout %ss" % timeout)
        except (OSError, ValueError) as exc:
            return ("failed", "invoke error: %s" % exc)
    outbox = state_file_path(root, "outbox.jsonl")
    ensure_dir(os.path.dirname(outbox))
    with open(outbox, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"envelope": envelope, "status": "dispatched",
                             "created_at": now_iso()}, ensure_ascii=False) + "\n")
    return ("dispatched", "awaiting host dispatch via native Skill tool")


def invoke(root: str | None, ticket_id: str, artifact_id: str,
           input_text: str = "", acceptance: list | None = None,
           invoke_cmd: str | None = None) -> dict:
    """发起一次真实的 grill-me 调用并记录结果；未安装则报错。"""
    data = load_integration(root)
    entry = data[TARGET]
    if not entry.get("installed"):
        raise ValueError("grill-me 未安装，无法调用")
    envelope = {
        "protocol": "CCF::INTEGRATION_CALL",
        "target": TARGET,
        "run_id": entry.get("run_id", ""),
        "ticket_id": ticket_id,
        "artifact_id": artifact_id,
        "input": input_text,
        "acceptance": acceptance or [],
        "expected_output": "findings",
        "timestamp": now_iso(),
    }
    result, detail = _invoke_real(root, envelope, invoke_cmd)
    call_id = format_id("IG", len(entry.get("calls", [])) + 1, 4)
    call = {
        "call_id": call_id,
        "ticket_id": ticket_id,
        "artifact_id": artifact_id,
        "timestamp": now_iso(),
        "result": result,
        "detail": detail,
        "findings_ref": "",
    }
    entry.setdefault("calls", []).append(call)
    ev = append_event(root, "INTEGRATION_CALL_%s" % result.upper(),
                      {"call_id": call_id, "detail": detail})
    call["findings_ref"] = "events/events.jsonl#%s" % ev["event_id"]
    streak = entry.get("failed_streak", 0)
    if result == "failed":
        streak += 1
        if streak >= 3:
            entry["decision"] = "disabled"
            append_event(root, "INTEGRATION_DISABLED", {"reason": "连续 3 次失败"})
    else:
        streak = 0
    entry["failed_streak"] = streak
    save_integration(root, data)
    return {"call": call, "result": result, "detail": detail}


def record_call(root: str | None, ticket_id: str, artifact_id: str, result: str,
                findings_event_id: str | None = None) -> dict:
    """记录一次联动调用；结果 ok/failed，连续失败统计。"""
    if result not in ("ok", "failed"):
        raise ValueError("result 仅支持 ok / failed")
    data = load_integration(root)
    entry = data[TARGET]
    call_id = format_id("IG", len(entry.get("calls", [])) + 1, 4)
    call = {
        "call_id": call_id,
        "ticket_id": ticket_id,
        "artifact_id": artifact_id,
        "timestamp": now_iso(),
        "result": result,
        "findings_ref": "events/events.jsonl#%s" % findings_event_id if findings_event_id else "",
    }
    entry.setdefault("calls", []).append(call)
    streak = entry.get("failed_streak", 0)
    if result == "ok":
        streak = 0
        append_event(root, "INTEGRATION_OK", {"call_id": call_id})
    else:
        streak += 1
        append_event(root, "INTEGRATION_FAILED", {"call_id": call_id})
        if streak >= 3:
            entry["decision"] = "disabled"
            append_event(root, "INTEGRATION_DISABLED", {"reason": "连续 3 次失败"})
    entry["failed_streak"] = streak
    save_integration(root, data)
    return data


def disable(root: str | None) -> dict:
    """关闭联动（/ccf integration off grill-me）。"""
    data = load_integration(root)
    data[TARGET]["decision"] = "disabled"
    save_integration(root, data)
    append_event(root, "INTEGRATION_DISABLED", {"reason": "用户指令关闭"})
    return data


def build_parser():
    p = argparse.ArgumentParser(description="CCF grill-me 联动探测工具（PRD 5.2）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录")
    p.add_argument("--skills-dir", default=None, help="已安装 Skill 目录（扫描探测）")
    p.add_argument("--skills-json", default=None, help="已安装 Skill 名称/对象列表（JSON）")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("probe", help="执行探测")
    pd = sub.add_parser("decide", help="处理安装提示回复")
    pd.add_argument("--choice", choices=("install", "decline", "later"), required=True)
    pr = sub.add_parser("install-reply", help="处理安装命令执行回复")
    pr.add_argument("--reply", choices=("done", "failed", "skip"), required=True)
    pc = sub.add_parser("call", help="发起真实联动调用（或 --result 强制结果）")
    pc.add_argument("--ticket-id", required=True)
    pc.add_argument("--artifact-id", required=True)
    pc.add_argument("--input", default="")
    pc.add_argument("--invoke-cmd", default=None,
                    help="真实调用命令模板；缺省则走 outbox 派发")
    pc.add_argument("--result", choices=("ok", "failed"), default=None,
                    help="强制指定结果（仅用于 eval）")
    pc.add_argument("--findings-event", default=None)
    sub.add_parser("disable", help="关闭联动")
    sub.add_parser("status", help="查看联动状态")
    return p


def _load_skills(args) -> list:
    if args.skills_json:
        items = json.loads(args.skills_json)
        return items if isinstance(items, list) else [items]
    if args.skills_dir:
        return scan_skills_dir(args.skills_dir)
    return []


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "probe":
            report = {"report": "integration-probe", "data": probe(args.state_dir, _load_skills(args))}
        elif args.command == "decide":
            report = {"report": "integration-decide", "choice": args.choice,
                      "data": decide(args.state_dir, args.choice)}
        elif args.command == "install-reply":
            report = {"report": "integration-install-reply", "reply": args.reply,
                      "data": apply_install_reply(args.state_dir, args.reply, _load_skills(args))}
        elif args.command == "call":
            if args.result:
                report = {"report": "integration-call",
                          "data": record_call(args.state_dir, args.ticket_id,
                                              args.artifact_id, args.result,
                                              args.findings_event)}
            else:
                report = {"report": "integration-call",
                          **invoke(args.state_dir, args.ticket_id, args.artifact_id,
                                   args.input, None, args.invoke_cmd)}
        elif args.command == "disable":
            report = {"report": "integration-disable", "data": disable(args.state_dir)}
        else:
            report = {"report": "integration-status", "data": load_integration(args.state_dir)}
    except (OSError, ValueError) as exc:
        report = {"report": "integration-error", "ok": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())