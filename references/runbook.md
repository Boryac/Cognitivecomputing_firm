# runbook.md

**路径**：`references/runbook.md`（加载时机：BOOTSTRAP 阶段 0，见 PRD 3.3）
**版本**：V1.4
**许可**：AGPL-3.0

---

## 1. 目的

本文件是 CCF 的**执行层接线手册**：把 `SKILL.md` 描述的抽象阶段（BOOTSTRAP / TURN / TERMINATE）逐一映射到 `scripts/` 下可运行的具体命令，并规定状态文件的读写顺序。模型负责编排与产出内容，脚本负责状态、门禁、风格、协同与交付的确定性。

## 2. 前置条件

| 项 | 要求 |
| --- | --- |
| Python | 3.10+（脚本使用 `from __future__ import annotations` 与 `X | None` 注解） |
| 工作目录 | Skill 包根目录（含 `SKILL.md`、`scripts/`、`assets/`、`run_state/`） |
| 状态目录 | 默认 `<skill_root>/run_state`，内含 `state/`、`events/`、`checkpoints/` |
| 权限 | 需要文件读写；脚本以子进程运行时需要执行权限 |

调用约定：命令中的 `<skill_root>` 指包根目录。所有脚本均为独立 CLI，运行形式为 `python scripts/<name>.py …`；脚本之间通过 `from ccf_state import …` 复用基础工具，因此必须保持 `scripts/` 为同一目录。

## 3. 状态目录与文件

| 路径 | 用途 |
| --- | --- |
| `run_state/state/run.json` | 当前 run 状态（含 hash 校验） |
| `run_state/state/activation.json` | 激活状态机 |
| `run_state/state/profile.json` | 用户画像 |
| `run_state/state/profile_history.json` | 画像历史（回滚用） |
| `run_state/state/ecosystem.json` | 协同池 |
| `run_state/state/integration.json` | grill-me 联动状态 |
| `run_state/state/individuals.json` | 个人分配索引 |
| `run_state/state/gate_reports.json` | 门禁报告累积 |
| `run_state/state/gate_failures.json` | 门禁连续失败计数 |
| `run_state/state/deliveries.json` | 交付记录 |
| `run_state/state/outbox.jsonl` | 协同调用派发队列（宿主回执） |
| `run_state/events/events.jsonl` | 事件日志（append-only） |
| `run_state/checkpoints/CK-NNN.json` | 检查点 |

## 4. BOOTSTRAP 脚本序列

```bash
# 阶段 0 激活确认（用户回复 activate 或显式命令）
python scripts/ccf_route.py route --input "activate"

# 阶段 1 生态与联动探测
python scripts/ecosystem_scanner.py --skills-dir <平台 skill 目录> \
    --scope-json '{"domain":["<领域>"],"output_type":"<类型>","core_capabilities":["<能力>"]}'
python scripts/integration_probe.py probe --skills-dir <平台 skill 目录>

# 阶段 2 运行契约（产出 contract 后校验）
python scripts/ccf_state.py init
python scripts/ccf_validate.py contract --no-contract   # 契约字段校验（先写入再校验）

# 阶段 3 实例化（写 run.json + 事件）
python scripts/ccf_state.py init

# 阶段 4 试运行与画像加载
python scripts/ccf_adapt.py view
# …最小工单试跑（走一次第 5 节步骤 1–9）…

# 阶段 5 锁定
python scripts/ccf_state.py checkpoint --reason lock
```

## 5. CCF::TURN 脚本序列

```bash
# 1 RESUME
python scripts/ccf_state.py view

# 2 VERIFY
python scripts/ccf_validate.py run
python scripts/integration_probe.py probe --skills-dir <dir>
python scripts/ecosystem_scanner.py --skills-dir <dir> --scope-json '{…}'

# 3 TRIAGE
python scripts/ccf_route.py route --input "<用户本轮输入>"

# 4 SCOPE / 5 PLAN  —— 上下文内产出 scope / WBS / DAG / RACI

# 6 STAFF
python scripts/individual_router.py \
    --microtask-json '{"microtask_id":"MT-001","objective":"…","acceptance":["…"],"function":"analyst"}' \
    --profile run_state/state/profile.json

# 7 EXECUTE —— 各职能产出 artifacts 与 differential_findings

# 8 VERIFY（风格 + 表达）
python scripts/style_lint.py --input-file <artifact 文件> --theme light --expression

# 9 GATE
python scripts/gate_runner.py --state-dir run_state --artifact <artifact.json> \
    --artifact-type deliverable --save

# 10 INTEGRATE —— 上下文内合并

# 11 DELIVER
python scripts/ccf_deliver.py --describe "<产物描述>" --run-id <RUN-ID> \
    --ticket-id T-001 --artifact-ids A-001 --save

# 12 LEARN
python scripts/ccf_adapt.py add --type preference --description "…" --level D1 \
    --set theme_preference=dark

# 13 COMMIT
python scripts/ccf_state.py checkpoint --reason commit
python scripts/ccf_state.py event --name TURN_COMMITTED
```

## 6. TERMINATE 脚本序列

```bash
python scripts/ccf_state.py event --name TERMINATED
python scripts/ccf_state.py checkpoint --reason terminate
python scripts/ccf_route.py route --input "/ccf stop"
# 产出结项报告、决策日志、工件索引、审计摘要
```

## 7. 脚本清单

| 脚本 | 职责 | 主要子命令/参数 |
| --- | --- | --- |
| `ccf_state.py` | 状态、事件、检查点、hash | `init`/`view`/`event`/`checkpoint`/`list`/`restore`/`hash` |
| `ccf_route.py` | 激活与命令路由 | `route --input`/`prompt`/`status`/`license` |
| `ccf_validate.py` | 契约与权限校验 | `contract`/`run`/`permission --role --action` |
| `ccf_adapt.py` | 画像与适配 | `view`/`add`/`rollback`/`reset` |
| `ccf_deliver.py` | 交付分类与管线 | `--describe`/`--type`/`--confirm`/`--save` |
| `gate_runner.py` | G0–G11 门禁 | `--artifact`/`--gates`/`--veto`/`--save` |
| `style_lint.py` | 风格与表达检查 | `--input-file`/`--theme`/`--expression` |
| `ecosystem_scanner.py` | 生态扫描 | `--skills-dir`/`--scope-json` |
| `skill_orchestrator.py` | 协同池与真实调用 | `--command scan/list/enable/disable/auto/call` |
| `integration_probe.py` | grill-me 联动 | `probe`/`decide`/`install-reply`/`call`/`disable` |
| `individual_router.py` | 个人路由 | `--microtask-json`/`--complexity`/`--profile` |

## 8. 平台落地（首轮主动提示）

宿主平台不允许技能在会话首轮自行运行，故「第一轮主动调用」通过平台适配层落地（不改变产品意图）：

| 平台 | 落地方式 | 文件 |
| --- | --- | --- |
| Claude Code | 斜杠命令 + user-invokable | `.claude/commands/ccf.md` |
| WorkBuddy | SessionStart / UserPromptSubmit hook 或 automation | `platform/workbuddy-hook.md` |
| Codex | AGENTS.md 引用 | `platform/codex.md` |

三者的等价触发入口：`/ccf start`、`/yestest start`、`调用弈策集团`、`调用 cognitivecomputing-firm`。

## 9. 恢复与漂移处理

```bash
python scripts/ccf_state.py view            # 校验 hash（默认）
python scripts/ccf_state.py hash            # 只算不写
python scripts/ccf_state.py list            # 列检查点
python scripts/ccf_state.py restore --id CK-003   # 或省略 --id 恢复最近
```

判定 `STATE_DRIFT` 时：停止执行 → 读最近检查点 → 校验 hash → 校验契约 → 校验风格 → 恢复上下文 → 记录事件 → 恢复 RUNNING（见 `references/workflow.md` 第 11 节）。

## 10. 故障排查

| 症状 | 排查 |
| --- | --- |
| `未找到 run 状态` | 先执行 `ccf_state.py init`；或显式激活 |
| `hash 校验失败` | 状态被外部改写；`restore` 最近检查点 |
| 脚本 `ModuleNotFoundError: ccf_state` | 确认在包根目录执行、且 `scripts/` 完整 |
| 协同调用一直 `dispatched` | 宿主未回执 outbox；由编排模型通过原生 Skill 工具执行并写回 |
| 门禁连续 3 次失败 | 触发 H4，等待人工决策（GR-6） |

---

YESTEST // runbook // V1.4 // G0
