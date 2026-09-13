# CCF 契约与权限校验：run.json 完整性、契约字段、权限矩阵（PRD 6.5、10、13）。
# 输出校验报告：passed + problems 列表。
"""CCF 校验：run 完整性、hash、契约与权限矩阵。

权限矩阵见 PRD 6.5；契约字段见 assets/run.template.json 的 contract。
核心规则：角色或个人不得审批自己的工作（P-6 / U-10 / A-20）。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from ccf_state import (compute_hash, load_run, now_iso, verify_hash)

KNOWN_PHASES = ("bootstrap", "locked", "running", "terminated", "failed")
KNOWN_THEMES = ("light", "dark")
KNOWN_LEVELS = ("D0", "D1", "D2", "D3", "D4")

# 权限矩阵（PRD 6.5）：角色 -> 能力集合
PERMISSION_MATRIX = {
    "board":                  {"read", "veto", "approve", "speak_to_user"},
    "CCO":                    {"read", "write", "veto", "approve", "speak_to_user"},
    "COO":                    {"read", "write", "approve"},
    "PMO Lead":               {"read", "write"},
    "Analyst Lead":           {"read", "write"},
    "Architect Lead":         {"read", "write"},
    "Specialist Lead":        {"read", "write"},
    "Red Team Lead":          {"read", "veto"},
    "Style Warden Lead":      {"read", "veto"},
    "QA Lead":                {"read", "veto"},
    "Integrator Lead":        {"read", "write"},
    "Learning Lead":          {"read", "write", "veto"},
    "Archivist Lead":         {"read", "write"},
    "individual":             {"read", "write"},
    "differential_individual": {"read", "write"},
}

ALL_ACTIONS = ("read", "write", "veto", "approve", "speak_to_user")


def normalize_role(role: str) -> str:
    """把角色名归一到权限矩阵的键；个人（非负责人）归到 individual。"""
    if not role:
        return "individual"
    r = role.strip()
    if r in PERMISSION_MATRIX:
        return r
    low = r.lower().replace("_", " ").replace("-", " ")
    if "lead" in low or "负责人" in low or "老板" in low:
        for key in PERMISSION_MATRIX:
            if key.replace("_", " ").lower().split()[0] in low:
                return key
        return "individual"
    if low in ("differential", "differential individual", "寻差"):
        return "differential_individual"
    return "individual"


def validate_permission(role: str, action: str, owner: str | None = None) -> list:
    """校验单次权限操作；返回问题列表。

    - 角色缺少该动作权限 => 越权
    - 动作是 approve 且 owner 与执行角色相同 => 自我审批
    """
    problems = []
    key = normalize_role(role)
    allowed = PERMISSION_MATRIX.get(key, set())
    if action not in ALL_ACTIONS:
        problems.append({
            "rule": "PERM-1",
            "message": "未知动作 %s（合法动作: %s）" % (action, "/".join(ALL_ACTIONS)),
            "severity": "error",
        })
        return problems
    if action not in allowed:
        problems.append({
            "rule": "PERM-2",
            "message": "越权：角色 %s 无 %s 权限" % (role or "individual", action),
            "severity": "error",
        })
    if action == "approve" and owner and normalize_role(owner) == key:
        problems.append({
            "rule": "PERM-3",
            "message": "自我审批：角色 %s 审批自己的工作" % (role or "individual"),
            "severity": "error",
        })
    return problems


def validate_contract(contract: dict, require_acceptance: bool = True) -> list:
    """校验运行契约字段（objective/scope/acceptance/risk/budget/theme）。"""
    problems = []
    if not isinstance(contract, dict):
        return [{"rule": "CT-0", "message": "contract 缺失或非对象", "severity": "error"}]
    objective = contract.get("objective", "")
    scope = contract.get("scope", "")
    acceptance = contract.get("acceptance", [])
    risk = contract.get("risk", [])
    budget = contract.get("budget", {})
    theme = contract.get("theme", "")

    if not isinstance(objective, str) or not objective.strip():
        problems.append({"rule": "CT-1", "message": "契约缺失: objective", "severity": "error"})
    if not isinstance(scope, str) or not scope.strip():
        problems.append({"rule": "CT-2", "message": "契约缺失: scope", "severity": "error"})
    if require_acceptance and (not isinstance(acceptance, list) or len(acceptance) == 0):
        problems.append({"rule": "CT-3", "message": "契约缺失: acceptance（验收条件）", "severity": "error"})
    if not isinstance(risk, list):
        problems.append({"rule": "CT-4", "message": "契约字段类型错误: risk 应为列表", "severity": "warning"})
    if not isinstance(budget, dict) or "tokens" not in budget or "time_minutes" not in budget:
        problems.append({"rule": "CT-5", "message": "契约缺失: budget（tokens/tools/time_minutes）", "severity": "warning"})
    elif not isinstance(budget.get("tokens", 0), (int, float)) or budget.get("tokens", 0) < 0:
        problems.append({"rule": "CT-6", "message": "契约校验失败: budget.tokens 非法", "severity": "warning"})
    if theme not in KNOWN_THEMES:
        problems.append({"rule": "CT-7", "message": "契约主题非法: %s（合法 light/dark）" % theme, "severity": "error"})
    return problems


def validate_run(run: dict, require_contract: bool = True) -> dict:
    """校验 run 完整性、hash 与契约；返回 {passed, problems}。"""
    problems = []
    required = ("run_id", "active", "phase", "theme", "style", "license",
                "contract", "integration", "ecosystem", "learning", "staffing",
                "created_at", "updated_at", "hash")
    for field in required:
        if field not in run:
            problems.append({"rule": "RUN-1", "message": "run 缺失字段: %s" % field,
                             "severity": "error"})
    if "hash" in run and not verify_hash(run):
        problems.append({"rule": "RUN-2", "message": "hash 校验失败：状态被改写",
                         "severity": "error"})
    if run.get("phase") not in KNOWN_PHASES and run.get("phase") not in (None, ""):
        problems.append({"rule": "RUN-3", "message": "未知 phase: %s" % run.get("phase"),
                         "severity": "warning"})
    if run.get("theme") not in KNOWN_THEMES:
        problems.append({"rule": "RUN-4", "message": "未知主题: %s" % run.get("theme"),
                         "severity": "warning"})
    if run.get("license") != "AGPL-3.0":
        problems.append({"rule": "RUN-5", "message": "许可声明异常（应为 AGPL-3.0）",
                         "severity": "error"})
    if require_contract:
        problems.extend(validate_contract(run.get("contract", {})))
    passed = not any(p["severity"] == "error" for p in problems)
    return {"passed": passed, "problems": problems}


def build_report(**kwargs) -> dict:
    report = kwargs
    report["passed"] = not any(p["severity"] == "error" for p in report.get("problems", []))
    report["checked_at"] = now_iso()
    return report


def build_parser():
    p = argparse.ArgumentParser(description="CCF 契约与权限校验工具（PRD 6.5、10）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录")
    p.add_argument("--run", default=None, help="run.json 文件路径（优先于 --state-dir）")
    p.add_argument("--no-contract", action="store_true", help="跳过契约校验")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("contract", help="校验运行契约")
    sub.add_parser("run", help="校验 run 完整性（含 hash 与契约）")
    pp = sub.add_parser("permission", help="校验权限操作")
    pp.add_argument("--role", required=True, help="角色名")
    pp.add_argument("--action", required=True, help="read/write/veto/approve/speak_to_user")
    pp.add_argument("--owner", default=None, help="被审批工作的 owner（用于自我审批检测）")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "permission":
            problems = validate_permission(args.role, args.action, args.owner)
            report = build_report(report="validate-permission", role=args.role,
                                  action=args.action, owner=args.owner, problems=problems)
        elif args.command == "contract":
            run = load_run(args.state_dir, verify=False, auto_restore=False) if args.run is None \
                else json.loads(open(args.run, "r", encoding="utf-8").read())
            problems = validate_contract(run.get("contract", {}),
                                         require_acceptance=not args.no_contract)
            report = build_report(report="validate-contract",
                                  contract=run.get("contract", {}), problems=problems)
        else:  # run
            run = load_run(args.state_dir, verify=False, auto_restore=False) if args.run is None \
                else json.loads(open(args.run, "r", encoding="utf-8").read())
            out = validate_run(run, require_contract=not args.no_contract)
            report = build_report(report="validate-run",
                                  run_id=run.get("run_id", ""),
                                  problems=out["problems"])
    except (OSError, ValueError, FileNotFoundError) as exc:
        report = {"report": "validate-error", "ok": False, "message": str(exc)}
        report["passed"] = False
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("passed", False) else 1


if __name__ == "__main__":
    sys.exit(main())