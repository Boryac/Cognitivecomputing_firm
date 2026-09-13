# platform/workbuddy.md — WorkBuddy 适配

**适用**：WorkBuddy（CodeBuddy 内核）
**许可**：AGPL-3.0

本文件把「第一轮主动调用」与「斜杠命令」落地到 WorkBuddy 原生机制。**技能包本身不注册 hook / 命令**——需把下列配置安装到平台侧（用户级或项目级）。

---

## 1. 会话首轮自动提示（SessionStart hook）

WorkBuddy 的 hook 由 `settings.json` 的 `hooks` 字段配置，事件含 `SessionStart`、`UserPromptSubmit` 等；Windows 上 hook 命令以 Git Bash 执行，Python 脚本需显式 `python3` 调用。

在 `settings.json` 中加入：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"<技能包>/platform/ccf_sessionstart.py\""
          }
        ]
      }
    ]
  }
}
```

将 `<技能包>` 替换为实际安装路径，例如：

- 用户级：`C:/Users/<你>/.workbuddy/skills/cognitivecomputing-firm`
- 项目级：`<项目>/.workbuddy/skills/cognitivecomputing-firm`

效果：会话开始/恢复时，若 CCF 未激活，hook 输出激活请求并注入上下文（等价于「首轮主动提示」）；状态为 ACTIVE/DECLINED/TERMINATED 时静默。

> 官方文档：WorkBuddy「Hook 参考指南」https://www.workbuddy.cn/docs/cli/hooks
> 注意：hook 在 Windows 上强制使用 Git Bash，命令需兼容 bash 语法；`python3` 需在 PATH 中。

## 2. 显式斜杠命令（可选）

WorkBuddy 会把诊断的技能暴露为 `/名称` 快捷方式；若需 `start/stop/status` 子命令，可把命令文件放到平台命令目录：

- 项目级：`<项目>/.codebuddy/commands/ccf.md`
- 用户级：`~/.codebuddy/commands/ccf.md`

命令文件内容见同目录 `workbuddy-ccf-command.md`（复制并重命名为 `ccf.md`）。

## 3. 等价自然语言入口（零配置）

无需任何适配即可激活：

```
调用弈策集团
调用 cognitivecomputing-firm
调用 CCF
```

## 4. 目录映射

| WorkBuddy 能力 | 路径 |
| --- | --- |
| 用户级技能 | `~/.workbuddy/skills/cognitivecomputing-firm/` |
| 项目级技能 | `<项目>/.workbuddy/skills/cognitivecomputing-firm/` |
| 用户级 hook / 设置 | `~/.workbuddy/settings.json`（以本机实际为准） |
| 用户级命令 | `~/.codebuddy/commands/` |
| 项目级命令 | `<项目>/.codebuddy/commands/` |

---

YESTEST // platform-workbuddy // V1.4 // G0
