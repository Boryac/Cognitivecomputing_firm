# persistence.md

**路径**：`references/persistence.md`（加载时机：按需，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 文件

| 文件 | 用途 |
| --- | --- |
| state/run.json | 当前状态 |
| events/events.jsonl | 事件日志（append-only） |
| checkpoints/ | 恢复点 |
| state/integration.json | grill-me 联动状态 |
| state/ecosystem.json | Skill 生态与协同状态 |
| state/profile.json | 用户画像与学习数据 |
| state/activation.json | 激活状态 |
| state/individuals.json | 个人分配与产出索引 |
| state/differential.json | 寻差发现索引 |

## 2. run.json 结构

结构与 `assets/run.template.json` 一致：

```
{
  "run_id": "CCF-2026-09-13-001",
  "active": true,
  "phase": "locked",
  "theme": "light",
  "style": "macos-vibrancy-light-v1",
  "license": "AGPL-3.0",
  "contract": {},
  "integration": {
    "grill_me": {
      "installed": true,
      "decision": "installed"
    }
  },
  "ecosystem": {
    "auto_enabled": true,
    "pool_size": 3
  },
  "learning": {
    "profile_version": "P-2",
    "auto_apply": true
  },
  "staffing": {
    "functions": [],
    "individuals": []
  },
  "created_at": "",
  "updated_at": "",
  "hash": ""
}
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| run_id | 运行编号，格式 CCF-YYYY-MM-DD-NNN |
| active | 是否激活 |
| phase | 当前阶段 |
| theme | 主题：light / dark |
| style | 风格标识：macos-vibrancy-light-v1 等 |
| license | 许可：AGPL-3.0 |
| contract | 运行契约（BOOTSTRAP 阶段 2 产物） |
| integration | grill-me 联动摘要 |
| ecosystem | 生态协同摘要 |
| learning | 画像版本与自适配开关 |
| staffing | 职能与个人分配摘要 |
| created_at / updated_at | 创建与更新时间（ISO8601） |
| hash | 状态校验值 |

## 3. activation.json 结构

```
{
  "state": "NOT_PROMPTED | PROMPTED | ACTIVE | DECLINED | TERMINATED",
  "prompted_at": "ISO8601 | null",
  "user_reply": "activate | decline | null",
  "explicit_command": "boolean",
  "resolved_at": "ISO8601 | null"
}
```

## 4. individuals.json 结构

```
{
  "assignments": [
    {
      "microtask_id": "MT-001",
      "function": "analyst",
      "individual": "gamma",
      "artifact_id": "A-001",
      "status": "merged | ignored | replaced",
      "ignore_reason": "string | null"
    }
  ]
}
```

## 5. differential.json 结构

```
{
  "findings": [
    {
      "finding_id": "DF-0001",
      "finder": "gamma",
      "function": "analyst",
      "type": "omitted_difference",
      "severity": "medium",
      "description": "",
      "evidence": "",
      "recommendation": "",
      "status": "accepted | ignored | escalated",
      "ignore_reason": "string | null"
    }
  ]
}
```

## 6. profile.json 结构

结构与 `assets/profile.template.json` 一致；详细语义见 `references/learning.md`。

```
{
  "version": "P-2",
  "created_at": "2026-09-13T10:00:00Z",
  "updated_at": "2026-09-13T12:00:00Z",
  "preferences": {
    "delivery_default_format": "pdf",
    "theme_preference": "light",
    "task_granularity": "standard",
    "individual_weight": {},
    "terminology_preference": []
  },
  "adaptations": [
    {
      "adapt_id": "AD-0001",
      "type": "preference",
      "description": "",
      "applied_at": "",
      "level": "D0",
      "status": "active"
    }
  ],
  "blacklist": [
    "style_law",
    "expression_constraint",
    "license",
    "organization_hierarchy",
    "gate_veto",
    "h_point_structure",
    "security_compliance"
  ]
}
```

## 7. 检查点策略

| 触发 | 动作 |
| --- | --- |
| 激活状态变更 | checkpoint |
| MicroTask 完成 | checkpoint |
| Gate 通过 | checkpoint |
| H 点恢复 | checkpoint |
| 联动状态变更 | checkpoint |
| 协同池变更 | checkpoint |
| 个人分配变更 | checkpoint |
| 寻差发现变更 | checkpoint |
| 画像更新 | checkpoint |
| 每 5 轮 TURN | heartbeat |

## 8. 恢复流程

```
1. 读 state/run.json
2. 不存在则读最近 checkpoint
3. 校验 hash
4. 校验契约
5. 校验风格
6. 校验联动状态
7. 校验协同状态
8. 校验激活状态
9. 校验个人分配
10. 校验寻差发现
11. 校验画像版本
12. 校验许可声明
13. 恢复上下文
14. 进入 RUNNING
```

## 9. 持久化能力分级

按平台能力分为四种情况（PRD 4.5），CCF 按实际情况选择：

| 情况 | 平台能力 | 机制 |
| --- | --- | --- |
| A | 支持跨轮状态 | 每轮读写 state/run.json |
| B | 支持文件读写，不支持状态 | 每轮写文件与 checkpoint |
| C | 仅文本 | 状态块 + 隐藏恢复块 |
| D | 不支持持久化 | CCF::BOOTSTRAP_FAILED，接入外部 checkpointer 或降级 CCF-Lite |

## 10. 事件与审计

- 事件日志 events/events.jsonl 为 append-only（验收标准 A-21）。
- 漂移检测见 `references/workflow.md` 第 11 节（CCF::STATE_DRIFT）。
- 所有状态文件含 hash 校验，恢复前必须校验（第 8 节步骤 3）。

## 11. 相关文件

| 文件 | 内容 |
| --- | --- |
| workflow.md | 持续机制 A/B/C/D、TURN、状态机 |
| integration-grill-me.md | integration.json 的联动语义 |
| ecosystem.md | ecosystem.json 的协同语义 |
| learning.md | profile.json 的画像语义 |
| differential.md | differential.json 的寻差语义 |

---

YESTEST // persistence // V1.3 // G0