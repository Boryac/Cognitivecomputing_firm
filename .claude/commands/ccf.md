---
description: 激活弈策集团（CCF）公司化多角色工作流
argument-hint: "[start|stop|status|theme light|theme dark|skills list|profile]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

用户通过斜杠命令触发了 **CCF（弈策集团 / cognitivecomputing-firm）**。

命令参数：`$ARGUMENTS`

请按以下步骤处理：

1. 读取并遵循本技能包内 `SKILL.md`（入口协议）与 `references/runbook.md`（执行层接线）。
2. 若参数为空或为 `start`：执行显式激活，进入 `CCF::BOOTSTRAP`
   - `python scripts/ccf_route.py route --input "/ccf start"`
   - 随后按 `references/runbook.md` 第 4 节依次执行 BOOTSTRAP 阶段 0–5。
3. 若为 `stop`：执行 `CCF::TERMINATE`（见 runbook 第 6 节）。
4. 若为 `status`：`python scripts/ccf_route.py status` 与 `python scripts/ccf_state.py view`，回报激活状态与 run 状态。
5. 若为 `theme light|dark`：更新 run 状态主题并回报。
6. 若为 `skills list|scan`：`python scripts/ecosystem_scanner.py --skills-dir <平台 skill 目录>` 后回报分级结果。
7. 若为 `profile`：`python scripts/ccf_adapt.py view` 并回报画像。

激活后本会话持续运行：每次输入登记为工单，按固定职能、角色、个人、流程、门禁与风格法执行；产出经 G0–G11 门禁与审计后交付。许可：AGPL-3.0。

> 说明：本命令是「第一轮主动调用」在 Claude Code 上的落地方式之一。若需真正的会话首轮自动提示，可在 `.claude/settings.json` 配置 `SessionStart` hook 指向 `platform/ccf-sessionstart.sh`。
