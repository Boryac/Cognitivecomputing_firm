# integration-grill-me.md

**路径**：`references/integration-grill-me.md`（加载时机：BOOTSTRAP 阶段 1，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 官方联动总表

grill-me 定位为「强制联动级」官方协同，优先级高于通用协同。

| 项 | 内容 |
| --- | --- |
| 联动对象 | grill-me Skill |
| 来源 | mattpocock/skills/grill-me |
| 安装命令 | `npx skills add mattpocock/skills/grill-me` |
| 联动方向 | CCF 主动调用 grill-me |
| 触发时机 | BOOTSTRAP 阶段 1 探测；每次 TURN 的 VERIFY 步骤复查 |
| 探测方式 | 读取平台已安装 Skill 列表 |
| 安装时行为 | 主动调用 grill-me，按第 4 节规则 |
| 未安装时行为 | 提示用户安装，按第 5 节规则 |
| 用户拒绝 | 按第 6 节规则，记录并继续 |
| 调用失败 | 按第 7 节规则，记录并降级 |
| 许可独立性 | grill-me 保留自身许可，与本 Skill 许可相互独立 |

## 2. 探测规则

```
输入：平台已安装 Skill 列表
步骤：
  1. 读取已安装 Skill 列表
  2. 匹配名称：grill-me
  3. 匹配大小写与连字符变体：grill-me, grill_me, GrillMe
  4. 输出 integration.json
输出：
  {
    "grill_me": {
      "installed": true | false,
      "version": "x.y.z" | null,
      "probed_at": "ISO8601"
    }
  }
```

## 3. 探测时机

| 时机 | 动作 |
| --- | --- |
| BOOTSTRAP 阶段 1 | 首次探测 |
| 每轮 TURN 的 VERIFY 步骤 | 复查 |
| 用户显式要求 | 立即探测 |
| 探测结果缓存 | 同一 Run 内有效 |

## 4. 已安装时的调用规则

| 编号 | 规则 |
| --- | --- |
| I-1 | CCF 主动调用 grill-me |
| I-2 | 调用发生在 TURN 的 VERIFY 步骤 |
| I-3 | 调用输入为当前 Artifact 与验收条件 |
| I-4 | 调用结果写入 integration.json 与 events |
| I-5 | grill-me 输出作为 G7 红队门与 G8 QA 门的补充输入 |
| I-6 | grill-me 不替代 Red Team、Style Warden、QA Auditor |
| I-7 | grill-me 无一票否决权 |
| I-8 | 调用失败不阻塞主流程，记录并降级 |

调用格式：

```
CCF::INTEGRATION_CALL
target: grill-me
run_id: CCF-YYYY-MM-DD-NNN
ticket_id: T-001
artifact_id: A-001
acceptance: [...]
expected_output: findings | questions | counterexamples
```

## 5. 未安装时的提示规则

| 编号 | 规则 |
| --- | --- |
| N-1 | CCF 提示用户是否安装 grill-me |
| N-2 | 提示仅出现一次，同一 Run 内不重复，除非用户选择 install |
| N-3 | 用户可选：install、decline、later |
| N-4 | 选择 install 时，展示安装命令并等待执行 |
| N-5 | 选择 decline 时，记录事件，主流程继续 |
| N-6 | 选择 later 时，记录事件，主流程继续，本 Run 不再提示 |
| N-7 | 提示不阻塞主流程 |
| N-8 | 安装命令固定为：`npx skills add mattpocock/skills/grill-me` |

提示格式：

```
YESTEST // INTEGRATION // OPTIONAL
检测到未安装联动 Skill：grill-me
作用：提供额外审查输入，作为 G7、G8 的补充。
安装命令：
  npx skills add mattpocock/skills/grill-me
可选操作：
  A. install   — 执行上述命令安装
  B. decline   — 拒绝，继续主流程
  C. later     — 稍后提醒（本 Run 内不再提示）
回复：install / decline / later
```

用户选择 install 的交互格式：

```
YESTEST // INTEGRATION // INSTALL
请在平台执行：
  npx skills add mattpocock/skills/grill-me
完成后回复：
  done    — 安装完成
  failed  — 安装失败
  skip    — 跳过，继续主流程
```

重探测成功格式：

```
YESTEST // INTEGRATION // READY
grill-me 已检测到。
后续将在 TURN 的 VERIFY 步骤主动调用，
输出作为 G7、G8 的补充输入。
```

重探测失败格式：

```
YESTEST // INTEGRATION // UNCONFIRMED
未检测到 grill-me。
可能原因：
  A. 安装未完成
  B. 平台未刷新 Skill 列表
  C. 名称不匹配
主流程继续。本 Run 内不再提示。
```

## 6. 用户拒绝处理

| 编号 | 规则 |
| --- | --- |
| D-1 | 记录事件 INTEGRATION_DECLINED |
| D-2 | 写入 integration.json |
| D-3 | 同一 Run 内不再提示 |
| D-4 | 主流程继续 |
| D-5 | 门禁不因缺失联动而失效 |

## 7. 调用失败与安装失败处理

| 编号 | 规则 |
| --- | --- |
| F-1 | 调用失败记录事件 INTEGRATION_FAILED |
| F-2 | 写入 integration.json |
| F-3 | 主流程继续 |
| F-4 | 不阻塞门禁 |
| F-5 | 连续 3 次调用失败 → 停止调用，记录 |
| F-6 | 安装失败记录事件 INTEGRATION_INSTALL_FAILED |
| F-7 | 安装失败不重试，本 Run 不再提示 |

## 8. 安装与重探测规则

安装规则：

| 编号 | 规则 |
| --- | --- |
| IN-1 | CCF 输出安装命令 |
| IN-2 | 由用户在平台执行命令 |
| IN-3 | 执行完成后，用户回复 done 或 failed 或 skip |
| IN-4 | 回复 done 则触发重探测 |
| IN-5 | 回复 failed 则记录，主流程继续 |
| IN-6 | 回复 skip 则记录，主流程继续 |
| IN-7 | 用户超时未回复视为 skip |

重探测规则：

| 编号 | 规则 |
| --- | --- |
| RP-1 | 用户回复 done 后立即重探测 |
| RP-2 | 重探测读取平台已安装 Skill 列表 |
| RP-3 | 匹配规则同第 2 节 |
| RP-4 | 探测到 → 写入 integration.json，进入调用模式 |
| RP-5 | 未探测到 → 记录事件 INTEGRATION_INSTALL_UNCONFIRMED，主流程继续 |
| RP-6 | 重探测在同一 Run 内仅执行一次 |
| RP-7 | 重探测结果写入 events 与 integration.json |

## 9. integration.json 结构

结构与 `assets/integration.template.yaml` 一致：

```
{
  "grill_me": {
    "installed": true,
    "version": "1.2.0",
    "license": "see grill-me repository",
    "probed_at": "2026-09-13T10:00:00Z",
    "decision": "installed | declined | later | install_pending | install_failed | unconfirmed | disabled",
    "install": {
      "command": "npx skills add mattpocock/skills/grill-me",
      "prompted_at": "2026-09-13T10:00:00Z",
      "user_reply": "done | failed | skip | null",
      "reprobed": true,
      "reprobe_result": "found | not_found"
    },
    "calls": [
      {
        "call_id": "IG-0001",
        "ticket_id": "T-001",
        "artifact_id": "A-001",
        "timestamp": "2026-09-13T10:05:00Z",
        "result": "ok | failed",
        "findings_ref": "events/events.jsonl#EV-000123"
      }
    ],
    "failed_streak": 0
  }
}
```

## 10. 相关事件

| 事件 | 触发 |
| --- | --- |
| INTEGRATION_PROBED | 探测完成 |
| INTEGRATION_FOUND | 检测到已安装 |
| INTEGRATION_MISSING | 未检测到 |
| INTEGRATION_PROMPTED | 已提示用户 |
| INTEGRATION_INSTALL_STARTED | 用户选择 install |
| INTEGRATION_INSTALLED | 安装完成并重探测成功 |
| INTEGRATION_INSTALL_FAILED | 用户回复 failed |
| INTEGRATION_INSTALL_UNCONFIRMED | 重探测未检测到 |
| INTEGRATION_DECLINED | 用户选择 decline |
| INTEGRATION_LATER | 用户选择 later 或超时 |
| INTEGRATION_CALLED | 调用发起 |
| INTEGRATION_OK | 调用成功 |
| INTEGRATION_FAILED | 调用失败 |
| INTEGRATION_DISABLED | 联动关闭或连续失败后停用 |

## 11. 与门禁的关系

| 门 | 关系 |
| --- | --- |
| G7 红队门 | grill-me 输出作为补充输入，不替代 Red Team |
| G8 QA 门 | grill-me 输出作为补充输入，不替代 QA Auditor |
| 其他门 | 无直接关系 |

## 12. 与角色权限的关系

| 角色 | 与 grill-me 关系 |
| --- | --- |
| Red Team | 接收 grill-me 输出作为参考 |
| QA Auditor | 接收 grill-me 输出作为参考 |
| CCO | 决定是否在交付中引用其发现 |
| 其他角色 | 无直接关系 |

## 13. 关闭联动

用户可通过以下指令关闭联动：

```
/ccf integration off grill-me
```

关闭后：

| 编号 | 规则 |
| --- | --- |
| O-1 | 不再探测 |
| O-2 | 不再提示 |
| O-3 | 不再调用 |
| O-4 | 记录事件 INTEGRATION_DISABLED |
| O-5 | 同一 Run 内有效 |

## 14. 相关文件

| 文件 | 内容 |
| --- | --- |
| ecosystem.md | 通用生态探测与协同编排 |
| gates.md | G7、G8 补充输入规则 |
| persistence.md | integration.json 持久化 |
| license.md | 许可独立性说明 |

---

YESTEST // integration-grill-me // V1.3 // G0