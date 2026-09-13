# CCF 按 MicroTask 分配职能/个人：专长匹配、认知风格补齐、寻差调度（PRD 6.21）。
# 写 state/individuals.json（结构 per PRD 13.4）。
"""CCF 个人路由：按 MicroTask 选择职能与个人。

选择算法见 PRD 6.21；默认调度表见 6.21（简单 1 人/一般 2-3 人/复杂全部/高寻差必调寻差个人）；
寻差个人映射表见 6.22。用户画像 individual_weight 调整优先级（6.21 步骤 6）。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from ccf_state import (format_id, now_iso, read_json_file, resolve_root,
                       state_file_path, write_json_file)

# 职能 -> 个人清单（PRD 6.7-6.18、manifest organization）
FUNCTION_INDIVIDUALS = {
    "cco": ["staff-chief", "adjudicator"],
    "coo": ["budget-keeper", "resource-planner", "sla-watcher"],
    "pmo": ["decomposer", "dag-builder", "raci-mapper"],
    "analyst": ["alpha", "beta", "gamma", "delta"],
    "architect": ["alpha", "beta", "gamma", "delta"],
    "specialist": ["alpha", "beta", "gamma", "delta"],
    "red_team": ["attacker", "breaker", "boundary", "differential"],
    "style_warden": ["enforcer", "terminology", "accessibility", "differential"],
    "qa": ["acceptance", "compliance", "trace", "differential"],
    "integrator": ["merger", "consistency", "source-keeper", "ecosystem"],
    "learning": ["observer", "pattern-miner", "proposer", "guardrail"],
    "archivist": ["memory-keeper", "version-keeper", "retro-writer", "differential"],
}

# 个人专长关键词（用于步骤 3 按任务特征匹配）
EXPERTISE = {
    "alpha": ["数据", "量化", "系统", "整体", "稳健", "成熟路径", "quant", "data", "system", "stable"],
    "beta": ["定性", "叙事", "接口", "契约", "创新", "探索", "新路径", "qualitative", "interface", "creative"],
    "gamma": ["反直觉", "逆向", "约束", "边界", "精炼", "迭代", "被忽略", "counterintuitive", "constraint"],
    "delta": ["溯源", "考古", "替代", "发散", "重构", "解构", "provenance", "alternative", "refactor"],
    "attacker": ["攻击", "对抗", "弱点", "attack", "weakness"],
    "breaker": ["破坏", "极端", "崩溃点", "break", "extreme"],
    "boundary": ["边界", "边缘", "边界条件", "boundary"],
    "differential": ["寻差", "差异", "比较", "不一致", "漂移", "differential", "diff"],
    "enforcer": ["规则", "严格", "执行", "rule", "strict"],
    "terminology": ["术语", "一致", "统一", "terminology"],
    "accessibility": ["无障碍", "包容", "wcag", "accessibility"],
    "acceptance": ["验收", "核对", "acceptance"],
    "compliance": ["合规", "保守", "不越线", "compliance"],
    "trace": ["追溯", "追根", "trace", "audit"],
    "merger": ["合并", "合成", "merge", "combine"],
    "consistency": ["一致", "校验", "术语", "consistency"],
    "source-keeper": ["来源", "标注", "source", "attribution"],
    "ecosystem": ["协同", "编排", "能力", "ecosystem", "orchestrate"],
    "observer": ["观测", "归纳", "采集", "observe"],
    "pattern-miner": ["模式", "挖掘", "规律", "pattern"],
    "proposer": ["适配", "建议", "优化", "propose", "optimize"],
    "guardrail": ["边界守护", "保守", "防护", "guardrail"],
    "memory-keeper": ["记忆", "累积", "记录", "memory"],
    "version-keeper": ["版本", "严格", "清晰", "version"],
    "retro-writer": ["复盘", "反思", "改进点", "retro"],
    "staff-chief": ["协调", "对齐", "协调各职能", "coordinate"],
    "adjudicator": ["裁决", "冲突", "证据", "adjudicate"],
    "budget-keeper": ["预算", "冗余", "budget"],
    "resource-planner": ["资源", "并行", "优化", "resource"],
    "sla-watcher": ["时限", "预警", "sla", "deadline"],
    "decomposer": ["拆解", "拆", "微任务", "decompose"],
    "dag-builder": ["编排", "图", "并行", "dag"],
    "raci-mapper": ["责任", "矩阵", "raci"],
}

COGNITIVE_STYLE = {
    "staff-chief": "结构化", "adjudicator": "权衡",
    "budget-keeper": "保守", "resource-planner": "优化", "sla-watcher": "敏感",
    "decomposer": "分解", "dag-builder": "图论", "raci-mapper": "矩阵",
    "alpha": "量化", "beta": "叙事", "gamma": "逆向", "delta": "考古",
    "architect-alpha": "整体", "architect-beta": "契约", "architect-gamma": "边界", "architect-delta": "发散",
    "specialist-alpha": "保守", "specialist-beta": "探索", "specialist-gamma": "迭代", "specialist-delta": "解构",
    "attacker": "对抗", "breaker": "极端", "boundary": "边缘",
    "differential": "比较",
    "enforcer": "严格", "terminology": "一致", "accessibility": "包容",
    "acceptance": "核对", "compliance": "保守", "trace": "考古",
    "merger": "整体", "consistency": "检查", "source-keeper": "考古", "ecosystem": "系统",
    "observer": "归纳", "pattern-miner": "分析", "proposer": "优化", "guardrail": "保守",
    "memory-keeper": "累积", "version-keeper": "严格", "retro-writer": "反思",
}

# 寻差个人映射表（PRD 6.22）：职能 -> 寻差个人
DIFFERENTIAL_MAP = {
    "analyst": "gamma",
    "architect": "delta",
    "specialist": "beta",
    "red_team": "differential",
    "style_warden": "differential",
    "qa": "differential",
    "archivist": "differential",
}

# 按复杂度调度人数（PRD 6.21）：simple 1 / medium 2-3 / complex 全部
HEADCOUNT = {"simple": 1, "medium": 3, "complex": None}  # None = 全部

# 最小调度（PRD 6.23）
MIN_STAFF = {"red_team": 2, "style_warden": 2, "qa": 2}

GATE_FUNCTION = {
    "G0": "cco", "G1": "pmo", "G2": "analyst", "G3": "architect",
    "G4": "qa", "G5": "qa", "G6": "style_warden", "G7": "red_team",
    "G8": "qa", "G9": "cco", "G10": "archivist", "G11": "learning",
}


def individuals_path(root: str | None = None) -> str:
    return state_file_path(root, "individuals.json")


def load_assignments(root: str | None = None) -> dict:
    data = read_json_file(individuals_path(root))
    if not data:
        data = {"assignments": []}
    data.setdefault("assignments", [])
    return data


def next_assignment_artifact(root: str | None) -> str:
    data = load_assignments(root)
    last = 0
    for a in data.get("assignments", []):
        aid = a.get("artifact_id", "A-000")
        if aid.startswith("A-") and aid[2:].isdigit():
            last = max(last, int(aid[2:]))
    return format_id("A", last + 1, 3)


def infer_function(microtask: dict) -> str | None:
    if microtask.get("function"):
        return microtask["function"]
    gate = microtask.get("gate", "")
    return GATE_FUNCTION.get(gate)


def infer_complexity(microtask: dict) -> str:
    """自动判断复杂度：验收>=3 / objective>=100 字 / 高寻差需求 -> complex。"""
    acceptance = microtask.get("acceptance", []) or []
    objective = microtask.get("objective", "") or ""
    if microtask.get("differential_required") is True or len(acceptance) >= 3 or len(objective) >= 100:
        return "complex"
    if len(acceptance) >= 2 or len(objective) >= 40:
        return "medium"
    return "simple"


def expertise_score(individual: str, objective: str) -> int:
    kws = EXPERTISE.get(individual, [])
    return sum(1 for k in kws if k in objective)


def select_individuals(function: str, microtask: dict, complexity: str,
                       profile: dict | None = None,
                       roster_override: list | None = None) -> dict:
    """按 PRD 6.21 算法选择个人。"""
    if roster_override is not None:
        roster = list(roster_override)
    else:
        roster = list(FUNCTION_INDIVIDUALS.get(function, []))
    if not roster:
        raise ValueError("职能 %s 无个人清单" % function)
    objective = microtask.get("objective", "") or ""
    differential_required = bool(microtask.get("differential_required", False))
    diff_individual = DIFFERENTIAL_MAP.get(function)

    # 人数：复杂度 -> 人数（复杂=全部）
    count = HEADCOUNT[complexity]
    if count is None:
        count = len(roster)
    count = max(count, MIN_STAFF.get(function, 1))
    count = min(count, len(roster))

    results = []          # {individual, reason, score}
    seen_styles = set()

    def add(ind, reason, score):
        if ind in [r["individual"] for r in results]:
            return
        results.append({"individual": ind, "reason": reason, "score": score})

    # 1. 寻差需求必调寻差个人（DD-1）
    if differential_required and diff_individual and diff_individual in roster:
        add(diff_individual, "寻差需求必调（DD-1）", 100)

    # 2. 按专长匹配排序
    scored = sorted(
        ((i, expertise_score(i, objective)) for i in roster),
        key=lambda x: x[1], reverse=True,
    )

    # 3. 按认知风格补齐视角 + 4. 用户画像权重调整
    weights = {}
    if profile:
        weights = (profile.get("preferences", {}) or {}).get("individual_weight", {}) or {}
    for ind, base in scored:
        if len(results) >= count:
            break
        if ind in [r["individual"] for r in results]:
            continue
        style = COGNITIVE_STYLE.get(ind, "")
        weight = int(weights.get(ind, 0) or 0)
        effective = base + weight
        if style and style in seen_styles and complexity != "complex":
            continue  # 认知风格补齐：复杂任务不限制
        seen_styles.add(style)
        add(ind, "专长匹配 + 认知风格补齐", effective)

    return {"function": function, "complexity": complexity, "count": len(results),
            "chosen": results, "differential_required": differential_required,
            "differential_individual": diff_individual if differential_required else None}


def assign(microtask: dict, complexity: str | None = None, profile: dict | None = None,
           roster_override: list | None = None,
           artifact_id: str | None = None, root: str | None = None) -> dict:
    """对单个 MicroTask 完成分配并写入 state/individuals.json。"""
    function = infer_function(microtask)
    if not function:
        raise ValueError("无法确定职能：microtask 缺 function 且 gate 无法推断")
    if complexity == "auto" or complexity is None:
        complexity = infer_complexity(microtask)
    selection = select_individuals(function, microtask, complexity, profile, roster_override)

    assignments = load_assignments(root)
    new_assignments = []
    for c in selection["chosen"]:
        aid = artifact_id or next_assignment_artifact(root)
        a = {
            "microtask_id": microtask.get("microtask_id", "MT-000"),
            "function": function,
            "individual": c["individual"],
            "artifact_id": aid,
            "status": "assigned",
            "ignore_reason": None,
        }
        assignments["assignments"].append(a)
        new_assignments.append(a)
    write_json_file(individuals_path(root), assignments)
    return {"microtask_id": microtask.get("microtask_id", "MT-000"),
            "function": function, "complexity": complexity,
            "selection": selection, "assignments": new_assignments,
            "assignments_total": len(assignments["assignments"])}


def build_parser():
    p = argparse.ArgumentParser(description="CCF 个人路由工具（PRD 6.21）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录")
    p.add_argument("--microtask", default=None, help="microtask JSON 文件路径")
    p.add_argument("--microtask-json", default=None, help="microtask JSON 字符串")
    p.add_argument("--complexity", default="auto", choices=("auto", "simple", "medium", "complex"))
    p.add_argument("--profile", default=None, help="profile JSON 文件路径（权重调整）")
    p.add_argument("--artifact-id", default=None, help="指定首个 artifact_id")
    p.add_argument("--roster", default=None, help="职能个人清单覆盖（JSON 数组）")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.microtask:
            microtask = read_json_file(args.microtask)
        elif args.microtask_json:
            microtask = json.loads(args.microtask_json)
        else:
            raise ValueError("需要 --microtask 或 --microtask-json")
        profile = read_json_file(args.profile) if args.profile else None
        roster = json.loads(args.roster) if args.roster else None
        report = assign(microtask, args.complexity, profile, roster,
                        args.artifact_id, args.state_dir)
        report["report"] = "individual-router"
    except (OSError, ValueError) as exc:
        report = {"report": "individual-error", "ok": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())