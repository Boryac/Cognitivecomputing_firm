# CCF 第一轮激活与命令路由：解析用户输入，维护 state/activation.json（PRD 4、13.3）。
# 路由结果常量与命令解析，供主流程决定进入 BOOTSTRAP / TURN / TERMINATE / 普通模式。
"""CCF 路由：第一轮激活、显式命令、终止与状态查询。

维护 state/activation.json：state / prompted_at / user_reply /
explicit_command / resolved_at（结构见 assets 约定与 PRD 13.3）。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from ccf_state import (append_event, ensure_dir, now_iso, read_json_file,
                       resolve_root, state_file_path, write_json_file)

# 路由结果常量
ROUTE_ACTIVATION_REQUEST = "ROUTE_ACTIVATION_REQUEST"   # 第一轮发出激活请求
ROUTE_ACTIVATE_BOOTSTRAP = "ROUTE_ACTIVATE_BOOTSTRAP"   # 进入 CCF::BOOTSTRAP
ROUTE_ACTIVATE_DECLINE = "ROUTE_ACTIVATE_DECLINE"       # 拒绝激活
ROUTE_TURN = "ROUTE_TURN"                               # 已激活，本轮走 CCF::TURN
ROUTE_TERMINATE = "ROUTE_TERMINATE"                     # 终止
ROUTE_STATUS = "ROUTE_STATUS"                           # 状态查询
ROUTE_COMMAND = "ROUTE_COMMAND"                         # 其余命令（theme/license/skills/profile/...）
ROUTE_NORMAL = "ROUTE_NORMAL"                           # 未激活且无命令，普通模式

ACTIVATION_STATES = ("NOT_PROMPTED", "PROMPTED", "ACTIVE", "DECLINED", "TERMINATED")

EXPLICIT_ACTIVATIONS = (
    "/ccf start",
    "/yestest start",
    "调用弈策集团",
    "调用 Cognitivecomputing_firm",
    "调用 CCF",
)
TERMINATE_COMMANDS = ("/ccf stop", "/yestest stop")
KNOWN_PREFIXES = ("/ccf ", "/yestest ")

ACTIVATION_REQUEST_TEXT = (
    "YESTEST // ACTIVATION // REQUEST\n"
    "弈策集团（Cognitivecomputing_firm）可激活。\n"
    "激活后本会话持续运行，将每次输入作为工单处理，\n"
    "按固定职能、角色、个人、流程、门禁、风格法执行。\n"
    "许可：AGPL-3.0\n"
    "回复：\n"
    "  activate  — 激活\n"
    "  decline   — 不激活，本会话不再提示"
)

LICENSE_TEXT = (
    "YESTEST // LICENSE // AGPL-3.0\n"
    "本 Skill 以 GNU Affero General Public License v3.0 分发。\n"
    "许可全文：见 LICENSE 文件。\n"
    "源代码获取：见 manifest.yaml 中 source_code 字段。\n"
    "修改必须标注，并以相同协议发布。\n"
    "网络服务必须提供源代码。"
)


def activation_path(root: str | None = None) -> str:
    return state_file_path(root, "activation.json")


def default_activation() -> dict:
    return {
        "state": "NOT_PROMPTED",
        "prompted_at": None,
        "user_reply": None,
        "explicit_command": False,
        "resolved_at": None,
    }


def load_activation(root: str | None = None) -> dict:
    """读取激活状态；缺失时返回 NOT_PROMPTED。"""
    data = read_json_file(activation_path(root))
    merged = default_activation()
    merged.update({k: v for k, v in data.items() if k in merged})
    if data.get("state") not in ACTIVATION_STATES:
        merged["state"] = "NOT_PROMPTED"
    return merged


def save_activation(root: str | None, activation: dict) -> dict:
    ensure_dir(os.path.dirname(activation_path(root)))
    write_json_file(activation_path(root), activation)
    return activation


def parse_command(text: str) -> dict:
    """解析 '/ccf ...' 或 '/yestest ...' 形式命令，返回 {command, args}。

    未命中已知前缀返回 None。
    """
    low = text.lower()
    for prefix in KNOWN_PREFIXES:
        if low.startswith(prefix):
            head = text[len(prefix):].strip()
            if not head:
                return {"command": "unknown", "args": []}
            parts = head.split()
            cmd = parts[0].lower()
            args = parts[1:]
            if cmd == "theme" and args and args[0] == "light" and len(args) == 1:
                return {"command": "theme", "args": ["light"]}
            if cmd == "theme" and args and args[0] == "dark" and len(args) == 1:
                return {"command": "theme", "args": ["dark"]}
            if cmd == "integration":
                return {"command": "integration", "args": args}
            if cmd == "skills":
                return {"command": "skills", "args": args}
            if cmd == "profile":
                return {"command": "profile", "args": args}
            if cmd == "license":
                return {"command": "license", "args": []}
            if cmd == "status":
                return {"command": "status", "args": []}
            if cmd == "start":
                return {"command": "start", "args": []}
            if cmd == "stop":
                return {"command": "stop", "args": []}
            return {"command": cmd, "args": args}
    return None


def route_input(text: str, activation: dict, first_turn: bool = False) -> dict:
    """对一次用户输入做路由；返回 {route, command?, args?, explicit_command, message}。"""
    raw = (text or "").strip()
    low = raw.lower()
    result = {"route": None, "explicit_command": False, "message": ""}

    # 显式激活命令
    if raw in EXPLICIT_ACTIVATIONS or low in {a.lower() for a in EXPLICIT_ACTIVATIONS}:
        result.update({
            "route": ROUTE_ACTIVATE_BOOTSTRAP,
            "explicit_command": True,
            "command": "start",
            "message": "显式命令激活，进入 CCF::BOOTSTRAP",
        })
        return result

    # 终止命令
    if raw in TERMINATE_COMMANDS or low in {a.lower() for a in TERMINATE_COMMANDS}:
        result.update({"route": ROUTE_TERMINATE, "command": "stop",
                       "message": "终止 CCF"})
        return result

    # 前缀命令
    parsed = parse_command(raw)
    if parsed is not None:
        cmd = parsed["command"]
        args = parsed["args"]
        if cmd == "stop":
            result.update({"route": ROUTE_TERMINATE, "command": "stop", "args": [],
                           "message": "终止 CCF"})
        elif cmd == "status":
            result.update({"route": ROUTE_STATUS, "command": "status", "args": [],
                           "message": "查询状态"})
        elif cmd == "start":
            result.update({"route": ROUTE_ACTIVATE_BOOTSTRAP, "explicit_command": True,
                           "command": "start", "args": [], "message": "显式激活"})
        else:
            result.update({"route": ROUTE_COMMAND, "command": cmd, "args": args,
                           "message": "/ccf 命令: %s" % cmd})
        return result

    # 第一轮（尚未提示）：发出激活请求
    if first_turn and activation.get("state") == "NOT_PROMPTED":
        result.update({"route": ROUTE_ACTIVATION_REQUEST, "message": "发出激活请求"})
        return result

    # 已提示等待回复：按激活回复处理（PRD 4.2）
    if activation.get("state") == "PROMPTED":
        if low == "activate":
            result.update({"route": ROUTE_ACTIVATE_BOOTSTRAP, "explicit_command": False,
                           "command": "activate", "message": "用户回复 activate"})
        else:
            result.update({"route": ROUTE_ACTIVATE_DECLINE, "explicit_command": False,
                           "command": "decline", "message": "用户回复非 activate，按 decline 处理"})
        return result

    # 已激活：普通输入一律进入 TURN
    if activation.get("state") == "ACTIVE":
        result.update({"route": ROUTE_TURN, "message": "已激活，输入转为工单"})
        return result

    # 其余：普通模式
    result.update({"route": ROUTE_NORMAL, "message": "未激活，普通模式"})
    return result


def first_turn_prompt(root: str | None = None) -> dict:
    """第一轮主动调用：记录 PROMPTED 并返回激活请求文本。"""
    activation = load_activation(root)
    if activation["state"] == "NOT_PROMPTED":
        activation["state"] = "PROMPTED"
        activation["prompted_at"] = now_iso()
        activation["user_reply"] = None
        save_activation(root, activation)
        append_event(root, "ACTIVATION_PROMPTED", {})
    return {"activation": activation, "text": ACTIVATION_REQUEST_TEXT}


def resolve_activation(root: str | None, route: dict) -> dict:
    """按路由结果更新激活状态；返回最新的 activation。"""
    activation = load_activation(root)
    r = route["route"]
    if r == ROUTE_ACTIVATION_REQUEST:
        if activation["state"] == "NOT_PROMPTED":
            activation["state"] = "PROMPTED"
            activation["prompted_at"] = now_iso()
            activation["user_reply"] = None
            save_activation(root, activation)
            append_event(root, "ACTIVATION_PROMPTED", {})
    elif r == ROUTE_ACTIVATE_BOOTSTRAP:
        activation["state"] = "ACTIVE"
        activation["user_reply"] = "activate" if not route.get("explicit_command") else None
        activation["explicit_command"] = bool(route.get("explicit_command"))
        activation["resolved_at"] = now_iso()
        if activation["prompted_at"] is None:
            activation["prompted_at"] = now_iso()
        save_activation(root, activation)
        if route.get("explicit_command"):
            append_event(root, "ACTIVATION_EXPLICIT", {})
        else:
            append_event(root, "ACTIVATION_CONFIRMED", {})
    elif r == ROUTE_ACTIVATE_DECLINE:
        activation["state"] = "DECLINED"
        activation["user_reply"] = "decline"
        activation["resolved_at"] = now_iso()
        save_activation(root, activation)
        append_event(root, "ACTIVATION_DECLINED", {})
    elif r == ROUTE_TERMINATE:
        activation["state"] = "TERMINATED"
        activation["resolved_at"] = now_iso()
        save_activation(root, activation)
        append_event(root, "TERMINATED", {})
    return activation


def build_parser():
    p = argparse.ArgumentParser(description="CCF 激活与命令路由工具（PRD 4）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录")
    sub = p.add_subparsers(dest="command", required=True)
    pr = sub.add_parser("route", help="路由一条用户输入")
    pr.add_argument("--input", required=True, help="用户输入文本")
    pr.add_argument("--first-turn", action="store_true", help="标记为会话第一轮")
    pp = sub.add_parser("prompt", help="第一轮发出激活请求（写入 activation.json）")
    ps = sub.add_parser("status", help="查看激活状态")
    pl = sub.add_parser("license", help="输出许可信息")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prompt":
            out = first_turn_prompt(args.state_dir)
            report = {"report": "route-prompt", "text": out["text"],
                      "activation": out["activation"]}
        elif args.command == "status":
            report = {"report": "route-status", "activation": load_activation(args.state_dir)}
        elif args.command == "license":
            report = {"report": "route-license", "text": LICENSE_TEXT}
        else:  # route
            activation = load_activation(args.state_dir)
            route = route_input(args.input, activation, first_turn=args.first_turn)
            activation = resolve_activation(args.state_dir, route)
            report = {
                "report": "route-result",
                "input": args.input,
                "route": route["route"],
                "command": route.get("command"),
                "args": route.get("args", []),
                "explicit_command": route.get("explicit_command", False),
                "message": route.get("message", ""),
                "activation": activation,
            }
    except (OSError, ValueError) as exc:
        report = {"report": "route-error", "ok": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())