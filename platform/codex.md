# platform/codex.md — Codex 适配

**适用**：OpenAI Codex（CLI / 桌面应用）
**许可**：AGPL-3.0

本文件把「第一轮主动调用」与「显式命令」落地到 Codex 的机制。Codex 遵循 Agent Skills 开放标准读取 `SKILL.md`，并以 `AGENTS.md` 作为常驻系统提示。

---

## 1. 安装技能

把整个技能目录放到 Codex 的技能目录（按你的 Codex 版本，通常为用户级）：

```
~/.codex/skills/cognitivecomputing-firm/
```

确认该目录下直接存在 `SKILL.md`、`manifest.yaml`、`references/`、`scripts/`、`assets/`、`evals/`、`platform/`。

## 2. 常驻入口（AGENTS.md）

Codex 在会话中加载 `AGENTS.md`。加入以下片段，即可让 CCF 在会话开始时被提示：

```markdown
## CCF（弈策集团 / cognitivecomputing-firm）

已安装 CCF 技能。当用户输入「调用弈策集团」「调用 cognitivecomputing-firm」「调用 CCF」
或「/ccf start」时，加载 ~/.codex/skills/cognitivecomputing-firm/SKILL.md 与
references/runbook.md，并进入 CCF::BOOTSTRAP，按固定职能、角色、个人、流程、
门禁与风格法执行；产出经 G0–G11 门禁与审计后交付。许可：AGPL-3.0。

首次会话可主动提示一次：
  YESTEST // ACTIVATION // REQUEST …（见 SKILL.md 第 2.1 节）
```

## 3. 显式命令

Codex 无与 cc 完全一致的斜杠命令体系；以自然语言入口为主：

```
调用弈策集团
调用 cognitivecomputing-firm
调用 CCF
/ccf start
```

若你的 Codex 版本支持自定义 prompt/命令文件，可将 `.claude/commands/ccf.md` 的内容移植为其命令格式（占位符 `$ARGUMENTS` 语义相近）。

## 4. 执行层

脚本调用与状态目录约定与平台无关，统一见 `references/runbook.md`：

```bash
python3 scripts/ccf_route.py route --input "/ccf start"
python3 scripts/ccf_state.py init
```

---

YESTEST // platform-codex // V1.4 // G0
