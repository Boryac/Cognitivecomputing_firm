#!/usr/bin/env python3
"""CCF SessionStart hook — 会话首轮注入弈策集团（CCF）激活提示。

用途
----
把「第一轮主动调用」落到平台原生 hook 机制上（见 references/runbook.md 第 8 节）。
本脚本在会话开始/恢复时执行，若 CCF 尚未激活，则向 stdout 输出激活请求；
SessionStart hook 的 stdout 会被注入上下文，从而等价实现「首轮主动提示」。

行为
----
- 读取 <技能包>/run_state/state/activation.json；
- 状态为 ACTIVE / DECLINED / TERMINATED 时不重复提示，静默退出；
- 否则输出激活请求，并把状态置为 PROMPTED。

许可：AGPL-3.0
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)  # platform/ 的上一级 = 技能包根目录
STATE_DIR = os.path.join(SKILL_ROOT, "run_state", "state")
ACTIVATION = os.path.join(STATE_DIR, "activation.json")

SKIP_STATES = ("ACTIVE", "DECLINED", "TERMINATED")

PROMPT = """YESTEST // ACTIVATION // REQUEST
弈策集团（cognitivecomputing-firm）可激活。
激活后本会话持续运行，将每次输入作为工单处理，
按固定职能、角色、个人、流程、门禁、风格法执行。
许可：AGPL-3.0
回复：
  activate  — 激活
  decline   — 不激活，本会话不再提示

[系统提示] 若用户回复 activate 或 /ccf start，请加载本技能包 SKILL.md 与
references/runbook.md，并执行 CCF::BOOTSTRAP。若用户回复其他内容，按
decline 处理并继续普通模式。"""


def _read_state() -> str:
    if not os.path.exists(ACTIVATION):
        return "NOT_PROMPTED"
    try:
        with open(ACTIVATION, "r", encoding="utf-8") as fh:
            return json.load(fh).get("state") or "NOT_PROMPTED"
    except (OSError, ValueError):
        return "NOT_PROMPTED"


def _write_prompted() -> None:
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(ACTIVATION, "w", encoding="utf-8") as fh:
            json.dump({
                "state": "PROMPTED",
                "prompted_at": None,
                "user_reply": None,
                "explicit_command": False,
                "resolved_at": None,
            }, fh, ensure_ascii=False, indent=2)
    except OSError:
        pass


def main() -> int:
    if _read_state() in SKIP_STATES:
        return 0
    _write_prompted()
    print(PROMPT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
