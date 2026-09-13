# CCF 协同池管理与调用编排：池维护、调用时序、协议封装、失败降级（PRD 5.3）。
# 读 state/ecosystem.json，写回调用与失败统计。
"""CCF 协同编排：协同池管理、CCF::ECOSYSTEM_CALL 协议封装与真实调用。

按能力类型映射执行节点（PRD 5.3.2）；调用超时 30s、最大并发 3（manifest）；
连续 3 次失败自动移出协同池（5.5.2）；许可不兼容不入池（5.4）。

真实调用（PRD 5.3.3）：
  1. 若提供 --invoke-cmd（或目标 manifest 声明 invoke），以子进程真实执行并取回结果；
  2. 否则把调用信封写入 run_state/state/outbox.jsonl，交宿主编排层通过原生 Skill 工具
     执行后写回 run_state/state/inbox.jsonl 回执。
两种路径都不再伪造 "ok"。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys

from ccf_state import (append_event, ensure_dir, format_id, now_iso,
                       read_json_file, resolve_root, state_file_path,
                       write_json_file)
from ecosystem_scanner import license_status, scan

CALL_TIMEOUT_SECONDS = 30
MAX_CONCURRENT = 3
PROTOCOL_HEADER = "CCF::ECOSYSTEM_CALL"

# 能力类型 -> 调用节点（PRD 5.3.2）
CAPABILITY_CALL_POINT = {
    "content_check": "gate",
    "content_generation": "execute",
    "format_conversion": "integrate",
    "analysis_enhancement": "scope_plan",
}
CALL_POINT_LABEL = {
    "gate": "GATE 阶段前（对应门禁前）",
    "execute": "EXECUTE 阶段（Specialist 执行后）",
    "integrate": "INTEGRATE 阶段（交付前）",
    "scope_plan": "SCOPE 阶段后（PLAN 阶段前）",
}


def ecosystem_path(root: str | None = None) -> str:
    return state_file_path(root, "ecosystem.json")


def load_pool(root: str | None = None) -> dict:
    data = read_json_file(ecosystem_path(root))
    if not data:
        data = {"scan_time": None, "total_installed": 0, "skills": {}, "auto_enabled": True}
    data.setdefault("skills", {})
    data.setdefault("auto_enabled", True)
    return data


def save_pool(root: str | None, data: dict) -> dict:
    write_json_file(ecosystem_path(root), data)
    return data


def apply_command(root: str | None, command: str, skill_id: str | None = None,
                  auto: str | None = None, scope: dict | None = None,
                  skills_dir: str | None = None, skills_json: str | None = None) -> dict:
    """处理 scan/list/enable/disable/auto/call 命令。"""
    pool = load_pool(root)
    if command == "scan":
        pool = scan(scope or {}, skills_dir, skills_json)
        pool["auto_enabled"] = load_pool(root).get("auto_enabled", True)
        save_pool(root, pool)
        append_event(root, "ECOSYSTEM_SCANNED", {})
        return {"command": "scan", "total": pool.get("total_installed", 0),
                "skills": pool.get("skills", {})}
    if command == "list":
        skills = pool.get("skills", {})
        rows = []
        for sid, info in skills.items():
            rows.append({"skill_id": sid, "match_score": info.get("match_score"),
                         "level": info.get("level"), "in_pool": info.get("in_pool"),
                         "call_point": info.get("call_point")})
        return {"command": "list", "auto_enabled": pool.get("auto_enabled"),
                "pool": rows}
    if command == "enable":
        if not skill_id:
            raise ValueError("enable 需要 --skill-id")
        info = pool["skills"].get(skill_id)
        if not info:
            raise ValueError("未找到 Skill: %s" % skill_id)
        if info.get("license_compat", {}).get("compat") == "high_risk":
            raise ValueError("许可高风险，禁止启用: %s" % skill_id)
        info["in_pool"] = True
        if info.get("level") == "disabled":
            info["level"] = "on_demand"
        save_pool(root, pool)
        append_event(root, "ECOSYSTEM_CONFIRMED", {"skill_id": skill_id})
        return {"command": "enable", "skill_id": skill_id, "skills": info}
    if command == "disable":
        if not skill_id:
            raise ValueError("disable 需要 --skill-id")
        info = pool["skills"].get(skill_id)
        if not info:
            raise ValueError("未找到 Skill: %s" % skill_id)
        info["in_pool"] = False
        info["level"] = "disabled"
        save_pool(root, pool)
        append_event(root, "ECOSYSTEM_DISABLED", {"skill_id": skill_id})
        return {"command": "disable", "skill_id": skill_id, "skills": info}
    if command == "auto":
        if auto not in ("on", "off"):
            raise ValueError("auto 需要 on/off")
        pool["auto_enabled"] = (auto == "on")
        save_pool(root, pool)
        append_event(root, "ECOSYSTEM_AUTO_TOGGLED", {"auto_enabled": pool["auto_enabled"]})
        return {"command": "auto", "auto_enabled": pool["auto_enabled"]}
    raise ValueError("未知命令: %s" % command)


def _invoke_real(root: str | None, envelope: dict, invoke_cmd=None,
                 timeout: int = CALL_TIMEOUT_SECONDS) -> tuple:
    """真实调用目标 Skill；返回 (result, output_ref_hint, detail)。

    result ∈ {ok, failed, dispatched}。
    - invoke_cmd 提供时：子进程真实执行（shell=False），按返回码判定 ok/failed；
    - 未提供时：信封写入 outbox.jsonl，等待宿主编排层执行后回执（dispatched）。
    不使用 shell=True，超时以 CALL_TIMEOUT_SECONDS 截断。
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
                    "stdout:%d" % len(out),
                    "rc=%d; out=%s; err=%s" % (proc.returncode, out[:800], err[:400]))
        except subprocess.TimeoutExpired:
            return ("failed", "", "timeout %ss" % timeout)
        except (OSError, ValueError) as exc:
            return ("failed", "", "invoke error: %s" % exc)
    outbox = state_file_path(root, "outbox.jsonl")
    ensure_dir(os.path.dirname(outbox))
    with open(outbox, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"envelope": envelope, "status": "dispatched",
                             "created_at": now_iso()}, ensure_ascii=False) + "\n")
    return ("dispatched", "outbox.jsonl#%s" % envelope["ticket_id"],
            "awaiting host dispatch via native Skill tool")


def dispatch_calls(pool: dict, root: str | None, ticket_id: str, artifact_id: str,
                   input_text: str = "", acceptance: list | None = None,
                   result_override: str | None = None,
                   invoke_cmd: str | None = None) -> dict:
    """按节点编排协同调用；返回调用记录摘要。

    - 仅 in_pool 的 skill 参与自动调用
    - 并发上限 MAX_CONCURRENT
    - 单次调用超时 CALL_TIMEOUT_SECONDS（真实子进程超时截断）
    - 真实调用：invoke_cmd 子进程执行，或 outbox 派发（见 _invoke_real）
    - 失败不阻塞，连续 3 次移出池；dispatched 不计失败
    """
    acceptance = acceptance or []
    skills = pool.get("skills", {})
    ordered = [info for info in skills.values() if info.get("in_pool")]
    active = ordered[:MAX_CONCURRENT]
    records = []
    for info in active:
        skill_id = [sid for sid, v in skills.items() if v is info][0]
        run_id = pool.get("run_id", "")
        envelope = {
            "protocol": PROTOCOL_HEADER,
            "target": skill_id,
            "run_id": run_id,
            "ticket_id": ticket_id,
            "artifact_id": artifact_id,
            "call_point": info.get("call_point", "verify"),
            "call_point_label": CALL_POINT_LABEL.get(info.get("call_point", "verify"), ""),
            "input": input_text,
            "acceptance": acceptance,
            "expected_output": "findings | artifact | data",
            "timeout_seconds": CALL_TIMEOUT_SECONDS,
            "timestamp": now_iso(),
        }
        # 解析真实调用命令：显式 --invoke-cmd 优先，其次目标 manifest 的 invoke 字段
        cmd = invoke_cmd or (info.get("invoke") if isinstance(info.get("invoke"), str) else None)
        if result_override == "failed":
            result, out_hint, detail = "failed", "", "forced by --result failed"
        else:
            result, out_hint, detail = _invoke_real(root, envelope, cmd)
        call_id = format_id("EC", len(info.get("calls", [])) + 1, 4)
        record = {
            "call_id": call_id,
            "ticket_id": ticket_id,
            "timestamp": now_iso(),
            "result": result,
            "detail": detail,
            "output_ref": "",
        }
        ev = append_event(root, "ECOSYSTEM_CALL_%s" % result.upper(),
                          {"target": skill_id, "call_id": call_id, "detail": detail})
        record["output_ref"] = "events/events.jsonl#%s" % ev["event_id"]
        info.setdefault("calls", []).append(record)
        streak = info.get("failed_streak", 0)
        if result == "failed":
            streak += 1
            info["failed_streak"] = streak
            if streak >= 3:
                info["in_pool"] = False
                append_event(root, "ECOSYSTEM_DISABLED", {"skill_id": skill_id,
                                                          "reason": "连续 3 次失败"})
        else:
            info["failed_streak"] = 0
        records.append({"target": skill_id, "call_point": info.get("call_point"),
                        "call_id": call_id, "result": result, "detail": detail,
                        "envelope": envelope})
    save_pool(root, pool)
    return {"records": records, "active_count": len(active),
            "enqueued_count": max(0, len(ordered) - len(active))}


def build_parser():
    p = argparse.ArgumentParser(description="CCF 协同池编排工具（PRD 5.3）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录")
    p.add_argument("--command", choices=("scan", "list", "enable", "disable", "auto", "call"),
                   required=True)
    p.add_argument("--skill-id", default=None)
    p.add_argument("--auto", choices=("on", "off"), default=None)
    p.add_argument("--skills-dir", default=None)
    p.add_argument("--skills-json", default=None)
    p.add_argument("--scope-json", default=None)
    p.add_argument("--ticket-id", default="T-001")
    p.add_argument("--artifact-id", default="A-001")
    p.add_argument("--input", default="")
    p.add_argument("--result", choices=("ok", "failed"), default=None)
    p.add_argument("--invoke-cmd", default=None,
                   help="真实调用命令模板，如 'python /path/to/target/entry.py'；缺省则走 outbox 派发")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "call":
            pool = load_pool(args.state_dir)
            report = {"report": "orchestrator-call",
                      "summary": dispatch_calls(pool, args.state_dir, args.ticket_id,
                                                args.artifact_id, args.input,
                                                result_override=args.result,
                                                invoke_cmd=args.invoke_cmd)}
        else:
            scope = json.loads(args.scope_json) if args.scope_json else {}
            out = apply_command(args.state_dir, args.command, args.skill_id, args.auto,
                                scope, args.skills_dir, args.skills_json)
            report = {"report": "orchestrator-command", **out}
    except (OSError, ValueError) as exc:
        report = {"report": "orchestrator-error", "ok": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())