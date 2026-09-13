# platform/ — 平台适配层

**许可**：AGPL-3.0

本目录把 CCF 的「第一轮主动调用」与「显式命令」落地到各宿主平台的原生机制。
技能包自身不含平台配置；下列配置需安装到平台侧。

| 平台 | 首轮提示落地 | 显式命令 | 说明文件 |
| --- | --- | --- | --- |
| Claude Code | `SessionStart` hook → `platform/ccf_sessionstart.py` | `.claude/commands/ccf.md` | 本文件第 1 节 |
| WorkBuddy | `SessionStart` hook → `platform/ccf_sessionstart.py` | `.codebuddy/commands/ccf.md` | `platform/workbuddy.md` |
| Codex | `AGENTS.md` 片段 | 自然语言 / 自定义 prompt | `platform/codex.md` |

零配置的等价入口（三平台通用）：`调用弈策集团`、`调用 cognitivecomputing-firm`、`调用 CCF`。

---

## 1. Claude Code 安装步骤

**技能**：把技能目录放到 `~/.claude/skills/cognitivecomputing-firm/`（个人级）或
`<项目>/.claude/skills/cognitivecomputing-firm/`（项目级）。

**斜杠命令**：复制 `.claude/commands/ccf.md` 到：

- 个人级：`~/.claude/commands/ccf.md`
- 项目级：`<项目>/.claude/commands/ccf.md`

**首轮自动提示（可选）**：在 `.claude/settings.json` 加入：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command",
            "command": "python3 \"~/.claude/skills/cognitivecomputing-firm/platform/ccf_sessionstart.py\"" }
        ]
      }
    ]
  }
}
```

## 2. WorkBuddy 安装步骤

见 `platform/workbuddy.md`（含 `settings.json` hook 片段与命令文件放置路径）。

## 3. Codex 安装步骤

见 `platform/codex.md`（技能目录 + `AGENTS.md` 片段）。

---

## 4. 脚本依赖

首轮提示与命令最终都调用技能包内 `scripts/`（Python 3.10+）。状态持久化于
`run_state/`。完整调用清单见 `references/runbook.md`。

---

YESTEST // platform // V1.4 // G0
