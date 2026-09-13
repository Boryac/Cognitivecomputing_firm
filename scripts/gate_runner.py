# CCF 门禁执行器：G0-G11 门列表、检查项、否决与回退（PRD 10）。
# 读 assets/gate-report.template.yaml 约定结构，输出 gate_reports 数组。
"""CCF 门禁：G0-G11 逐门执行，检查项 + 否决 + 回退 + 连续三次失败提示 H4。

门列表与否决方见 PRD 10.1，执行算法见 10.3。
补充输入：G7/G8 读 grill-me 输出、协同输出与寻差发现；G5/G9 读许可声明。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from ccf_state import (append_event, load_template, now_iso, read_json_file,
                       state_file_path, write_json_file)
from style_lint import find_expression_violations, lint_text

GATES = [
    {"id": "G0", "name": "立项门", "veto_owner": "CCO", "fallback": "re_execute",
     "checks": ["目标已定义", "范围已定义", "验收条件已定义"]},
    {"id": "G1", "name": "范围门", "veto_owner": "PMO Lead", "fallback": "rollback",
     "checks": ["WBS 已产出", "DAG 已产出", "RACI 已产出"]},
    {"id": "G2", "name": "证据门", "veto_owner": "Analyst Lead", "fallback": "re_execute",
     "checks": ["事实与假设分离", "来源标注完整", "置信度标注完整"]},
    {"id": "G3", "name": "架构门", "veto_owner": "Architect Lead", "fallback": "re_execute",
     "checks": ["接口已定义", "边界已划定", "约束已标注"]},
    {"id": "G4", "name": "安全门", "veto_owner": "QA Lead", "fallback": "rollback",
     "checks": ["权限合规", "隐私合规", "合规要求已核对"]},
    {"id": "G5", "name": "合规门", "veto_owner": "QA Lead", "fallback": "rollback",
     "checks": ["法律合规", "政策合规", "许可合规", "协同许可兼容性已复核"]},
    {"id": "G6", "name": "风格门", "veto_owner": "Style Warden Lead", "fallback": "rollback",
     "checks": ["macOS Vibrancy 合规", "禁止项无命中", "必须模式满足"]},
    {"id": "G7", "name": "红队门", "veto_owner": "Red Team Lead", "fallback": "re_execute",
     "checks": ["失败模式已列出", "反例已构造", "寻差发现已读取", "协同校验输出已读取"]},
    {"id": "G8", "name": "QA 门", "veto_owner": "QA Lead", "fallback": "re_execute",
     "checks": ["验收逐条核对", "追溯链完整", "寻差发现已读取", "协同校验输出已读取"]},
    {"id": "G9", "name": "交付门", "veto_owner": "CCO", "fallback": "re_execute",
     "checks": ["产物完整", "可执行性已确认", "表达合规", "许可合规", "交付格式已确认"]},
    {"id": "G10", "name": "归档门", "veto_owner": "Archivist Lead", "fallback": "re_execute",
     "checks": ["记忆已写入", "版本已标注", "审计包已产出"]},
    {"id": "G11", "name": "学习门", "veto_owner": "Learning Lead", "fallback": "rollback",
     "checks": ["适配边界合规", "核心规则守护", "黑名单校验通过"]},
]

# artifact.type -> 必经门（PRD 10.3 步骤 2）
TYPE_GATES = {
    "research_brief": ["G0", "G2"],
    "spec": ["G0", "G1", "G2", "G3"],
    "artifact": ["G0", "G3", "G6", "G7", "G8"],
    "risk_register": ["G7"],
    "style_report": ["G6"],
    "qa_report": ["G8"],
    "deliverable": ["G0", "G5", "G6", "G7", "G8", "G9", "G10"],
    "memory": ["G10"],
    "audit_package": ["G10"],
    "default": ["G0", "G3", "G6", "G7", "G8", "G9"],
}

FALLBACK_OPTIONS = ("none", "rollback", "re_execute", "h2", "h4")


def gate_by_id(gate_id: str) -> dict | None:
    for g in GATES:
        if g["id"] == gate_id:
            return g
    return None


def gate_report_template() -> dict:
    """gate-report 结构骨架（字段名与 assets/gate-report.template.yaml 一致）。"""
    return load_template("gate-report.template.yaml")


def _auto_check(gate_id: str, description: str, artifact: dict) -> dict | None:
    """按检查描述关键字对 artifact 字段做自动判定；无法判定返回 None。"""
    body = artifact.get("body", "") or ""
    notice = artifact.get("license_notice", "") or ""
    scope = artifact.get("scope", {}) or {}
    if not isinstance(scope, dict):
        scope = {}
    if "许可" in description:
        ok = isinstance(notice, str) and "AGPL-3.0" in notice
        return {"passed": ok, "evidence": "license_notice 含 AGPL-3.0" if ok else "缺少 AGPL-3.0 许可声明"}
    if "表达" in description:
        hits = find_expression_violations(body)
        return {"passed": len(hits) == 0,
                "evidence": "表达约束 0 违规" if not hits else "违规: %s" % json.dumps(hits, ensure_ascii=False)}
    if "风格" in description or "禁止项" in description or "必须模式" in description:
        rep = lint_text(body, theme=artifact.get("theme", "light"))
        return {"passed": rep["passed"],
                "evidence": "style_lint: %d error / %d warning" % (rep["summary"]["errors"], rep["summary"]["warnings"])}
    if "目标" in description:
        ok = bool((scope.get("objective") or artifact.get("objective") or "").strip())
        return {"passed": ok, "evidence": "objective 已定义" if ok else "objective 缺失"}
    if "范围" in description:
        ok = bool((scope.get("scope") or "").strip()) or bool(artifact.get("scope_text", ""))
        return {"passed": ok, "evidence": "scope 已定义" if ok else "scope 缺失"}
    if "验收" in description:
        acc = scope.get("acceptance") or artifact.get("acceptance") or []
        ok = isinstance(acc, list) and len(acc) > 0
        return {"passed": ok, "evidence": "acceptance %d 条" % len(acc) if isinstance(acc, list) else "acceptance 缺失"}
    if "寻差" in description:
        findings = artifact.get("differential_findings", []) or []
        ok = len(findings) > 0
        return {"passed": ok, "evidence": "differential_findings %d 条" % len(findings)}
    if "协同" in description:
        eco = artifact.get("ecosystem_outputs", []) or []
        integ = artifact.get("integration_outputs", []) or []
        ok = len(eco) > 0 or len(integ) > 0
        return {"passed": ok, "evidence": "协同输出 %d 条 / 联动输出 %d 条" % (len(eco), len(integ))}
    if "完整" in description:
        ok = bool(body.strip())
        return {"passed": ok, "evidence": "body 非空" if ok else "body 为空"}
    return None


def run_gate(gate_id: str, artifact: dict, opts: dict) -> dict:
    """执行单个门；返回 gate-report 结构（以 assets/gate-report.template.yaml 为骨架）。"""
    gate = gate_by_id(gate_id)
    if gate is None:
        raise ValueError("未知门禁: %s" % gate_id)
    report = dict(gate_report_template())
    report.update({
        "gate_report_id": opts.get("report_id", report.get("gate_report_id", "GR-001")),
        "run_id": opts.get("run_id", ""),
        "ticket_id": opts.get("ticket_id", ""),
        "artifact_id": artifact.get("artifact_id", opts.get("artifact_id", "")),
        "gate_id": gate["id"],
        "gate_name": gate["name"],
        "veto_owner": gate["veto_owner"],
        "checks": [],
        "supplementary_inputs": {
            "integration_outputs": artifact.get("integration_outputs", []) or [],
            "ecosystem_outputs": artifact.get("ecosystem_outputs", []) or [],
            "differential_findings": artifact.get("differential_findings", []) or [],
        },
        "veto": {"cast": False, "by": "", "reason": ""},
        "result": "fail",
        "fallback": opts.get("fallback_override") or gate["fallback"],
        "checked_by": opts.get("checked_by", "gate_runner"),
        "checked_at": now_iso(),
        "version": 1,
    })

    override_map = opts.get("checks_override", {}).get(gate_id, {})
    fail_this = gate_id in opts.get("fail_gates", [])
    all_pass = opts.get("all_pass", False)
    strict = opts.get("strict", False)
    for idx, desc in enumerate(gate["checks"], start=1):
        check_id = "C-%03d" % idx
        o = override_map.get(check_id)
        if o is not None:
            passed, evidence, note = bool(o.get("passed", False)), o.get("evidence", ""), o.get("notes", "")
        elif fail_this:
            passed, evidence, note = False, "模拟失败", ""
        elif all_pass:
            passed, evidence, note = True, "人为放行", ""
        else:
            auto = _auto_check(gate_id, desc, artifact)
            if auto is not None:
                passed, evidence, note = auto["passed"], auto["evidence"], ""
            elif strict:
                passed, evidence, note = False, "未提供证据（严格模式）", ""
            else:
                passed, evidence, note = True, "默认通过（无反证）", ""
        report["checks"].append({
            "check_id": check_id, "description": desc,
            "required": True, "passed": passed, "evidence": evidence, "notes": note,
        })

    veto_own = opts.get("veto_by_gate", {}).get(gate_id)
    if veto_own:
        report["veto"] = {"cast": True, "by": veto_own.get("by", ""), "reason": veto_own.get("reason", "")}
        report["result"] = "fail"
        return report
    all_passed = all(c["passed"] for c in report["checks"])
    report["result"] = "pass" if all_passed else "fail"
    return report


def determine_gates(artifact_type: str) -> list:
    return list(TYPE_GATES.get(artifact_type, TYPE_GATES["default"]))


def load_gate_failures(root: str | None) -> dict:
    return read_json_file(state_file_path(root, "gate_failures.json"))


def save_gate_failures(root: str | None, data: dict) -> None:
    write_json_file(state_file_path(root, "gate_failures.json"), data)


def run_all(artifact: dict, opts: dict) -> dict:
    """按 PRD 10.3 执行必经门序列，记录连续失败并提示 H4。"""
    root = opts.get("state_dir")
    gate_ids = opts.get("gates") or determine_gates(artifact.get("type", "default"))
    failures = load_gate_failures(root)
    reports = []
    h4 = False
    for gate_id in gate_ids:
        opts["report_id"] = "GR-%03d" % (len(reports) + 1)
        rep = run_gate(gate_id, artifact, opts)
        reports.append(rep)
        if rep["result"] == "fail":
            streak = failures.get(gate_id, 0) + 1
        else:
            streak = 0
        failures[gate_id] = streak
        if streak >= 3:
            h4 = True
            rep["fallback"] = "h4"
    if root:
        save_gate_failures(root, failures)
        append_event(root, "GATES_RUN", {"gate_ids": gate_ids, "h4": h4})
    passed = all(r["result"] == "pass" for r in reports)
    return {"report": "gate-runner", "gates": reports, "passed": passed,
            "h4_triggered": h4, "checked_at": now_iso()}


def _parse_veto(spec: str) -> dict:
    """解析 'G6:Style Warden Lead:理由' 形式的否决声明。"""
    parts = spec.split(":", 2)
    if len(parts) < 2:
        raise ValueError("否决格式应为 gate:by:reason")
    return {"gate": parts[0].strip(), "by": parts[1].strip(),
            "reason": parts[2].strip() if len(parts) > 2 else ""}


def build_parser():
    p = argparse.ArgumentParser(description="CCF 门禁执行器（PRD 10）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录（记录连续失败）")
    p.add_argument("--artifact", default=None, help="artifact JSON 文件路径")
    p.add_argument("--artifact-type", default="deliverable", help="artifact 类型（决定必经门）")
    p.add_argument("--artifact-body", default=None, help="artifact 正文（用于自动检查）")
    p.add_argument("--license-notice", default=None, help="许可声明文本")
    p.add_argument("--gates", default=None, help="显式门列表，如 G0,G6,G9")
    p.add_argument("--ticket-id", default="T-001")
    p.add_argument("--run-id", default="")
    p.add_argument("--checked-by", default="gate_runner")
    p.add_argument("--veto", default=None, action="append", help="否决声明 gate:by:reason，可多次")
    p.add_argument("--fail-gate", default=None, action="append", help="强制失败的门，可多次")
    p.add_argument("--all-pass", action="store_true", help="人为放行全部检查")
    p.add_argument("--strict", action="store_true", help="无证据的检查按失败处理")
    p.add_argument("--fallback", default=None, choices=FALLBACK_OPTIONS, help="覆盖回退策略")
    p.add_argument("--save", action="store_true", help="把报告合并写入 state/gate_reports.json")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        artifact = {}
        if args.artifact:
            artifact = read_json_file(args.artifact)
        artifact.setdefault("type", args.artifact_type)
        if args.artifact_body is not None:
            artifact["body"] = args.artifact_body
        if args.license_notice is not None:
            artifact["license_notice"] = args.license_notice
        veto = {}
        veto_by_gate = {}
        if args.veto:
            for spec in args.veto:
                v = _parse_veto(spec)
                if v["gate"].startswith("G"):
                    veto_by_gate[v["gate"]] = {"by": v["by"], "reason": v["reason"]}
                else:
                    veto = {"cast": True, "by": v["by"], "reason": v["reason"]}
        gates = args.gates.split(",") if args.gates else None
        opts = {
            "state_dir": args.state_dir,
            "gates": gates,
            "ticket_id": args.ticket_id,
            "run_id": args.run_id,
            "checked_by": args.checked_by,
            "veto": veto,
            "veto_by_gate": veto_by_gate,
            "fail_gates": args.fail_gate or [],
            "all_pass": args.all_pass,
            "strict": args.strict,
            "fallback_override": args.fallback,
        }
        report = run_all(artifact, opts)
        if args.save:
            all_reports = read_json_file(state_file_path(args.state_dir, "gate_reports.json"))
            if not isinstance(all_reports, list):
                all_reports = []
            all_reports.extend(report["gates"])
            write_json_file(state_file_path(args.state_dir, "gate_reports.json"), all_reports)
    except (OSError, ValueError, FileNotFoundError) as exc:
        report = {"report": "gate-error", "ok": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("passed", False) else 1


if __name__ == "__main__":
    sys.exit(main())