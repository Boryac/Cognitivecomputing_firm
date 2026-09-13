---
description: 激活弈策集团（CCF）公司化多角色工作流
argument-hint: "[start|stop|status|theme light|theme dark|skills list|profile]"
---

用户通过 `/ccf` 触发了 **弈策集团（CCF / cognitivecomputing-firm）**。参数：`$ARGUMENTS`

> 安装：把本文件复制到 `<项目>/.codebuddy/commands/ccf.md` 或 `~/.codebuddy/commands/ccf.md`。

处理步骤：

1. 加载技能包 `SKILL.md` 与 `references/runbook.md`。
2. 参数为空或 `start`：显式激活并进入 `CCF::BOOTSTRAP`
   - `python3 scripts/ccf_route.py route --input "/ccf start"`
   - 按 `references/runbook.md` 第 4 节执行 BOOTSTRAP 阶段 0–5。
3. `stop`：执行 `CCF::TERMINATE`（runbook 第 6 节）。
4. `status`：`python3 scripts/ccf_route.py status` + `python3 scripts/ccf_state.py view`。
5. `theme light|dark`：更新 run 主题。
6. `skills list|scan`：`python3 scripts/ecosystem_scanner.py --skills-dir <平台 skill 目录>`。
7. `profile`：`python3 scripts/ccf_adapt.py view`。

激活后本会话持续运行，每次输入登记为工单，按固定职能、角色、个人、流程、门禁与风格法执行，产出经 G0–G11 门禁与审计后交付。许可：AGPL-3.0。
