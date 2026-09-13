# ecosystem.md

**路径**：`references/ecosystem.md`（加载时机：BOOTSTRAP 阶段 1，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 探测时机

| 时机 | 动作 | 范围 |
| --- | --- | --- |
| BOOTSTRAP 阶段 1 | 首次全量扫描 | 所有已安装 Skill |
| 每轮 TURN 的 VERIFY 步骤 | 增量探测 | 新增/变更的 Skill |
| 用户显式命令 `/ccf skills scan` | 立即全量重扫 | 所有已安装 Skill |
| 任务领域变更时 | 定向重匹配 | 协同池内 Skill + 未匹配 Skill |

## 2. 探测元数据维度

读取每个 Skill 的 manifest 字段用于匹配：

- 基础信息：name、version、description、tags
- 能力声明：capabilities.required、capabilities.optional
- 输入输出：inputs、outputs 格式与类型
- 许可协议：license、license_url
- 调用方式：entry、commands、integrations

## 3. 匹配逻辑

```
输入：任务 scope（领域、产出类型、核心能力需求） + Skill 元数据
步骤：
  1. 产出类型匹配：文档/代码/表格/图片/数据/音频等
  2. 能力标签匹配：语义相似度计算
  3. 输入输出契约匹配：能否接入 CCF 流水线
  4. 许可兼容性校验：见第 6 节
  5. 输出匹配度评分（0-100）与分级
输出：
  - 强匹配：≥80分，能力完全覆盖需求
  - 弱匹配：50-79分，部分能力互补
  - 无关：<50分，不进入推荐
```

## 4. 协同分级与调用编排

### 4.1 协同分级

| 级别 | 触发条件 | 确认方式 | 调用规则 |
| --- | --- | --- | --- |
| 强制联动 | 官方指定（grill-me） | 无需确认，按原规则 | 每轮 VERIFY 步骤自动调用 |
| 推荐协同 | 匹配度≥80 | H1 启动契约一并确认 | 确认后进入协同池，按编排自动调用 |
| 按需协同 | 匹配度 50-79 | 对应任务环节前提示 | 用户选择 invoke / skip，单次生效 |
| 禁用 | 匹配度<50 / 许可冲突 / 用户手动禁用 | — | 不提示、不调用 |

### 4.2 调用时序编排

纳入协同池的 Skill，按能力映射到对应执行节点，输出作为该环节输入：

| Skill 能力类型 | 调用时机 | 对应环节 | 输入 | 输出用途 |
| --- | --- | --- | --- | --- |
| 内容校验类 | GATE 阶段前 | 对应门禁前 | 当前 artifact | 作为该门禁的补充输入 |
| 内容生成类 | EXECUTE 阶段 | Specialist 执行后 | spec、artifact 草稿 | 补充产出产物，由 Specialist 整合 |
| 格式转换类 | INTEGRATE 阶段 | 交付前 | 最终 artifact | 生成目标格式交付物 |
| 分析增强类 | SCOPE 阶段后 | PLAN 阶段前 | scope | 补充拆解维度，输出给 PMO |

### 4.3 统一调用协议

```
CCF::ECOSYSTEM_CALL
target: <skill_id>
run_id: CCF-YYYY-MM-DD-NNN
ticket_id: T-001
artifact_id: A-001
call_point: <执行节点>
input: <当前产物/数据>
acceptance: [...]
expected_output: findings | artifact | data
```

## 5. 生态协同推荐输出

推荐列表在 H1 启动契约时一并确认：

```
YESTEST // ECOSYSTEM // RECOMMENDATIONS
检测到以下已安装 Skill 可协同：
  - <skill_id>（匹配度：92，推荐级）：能力说明
  - <skill_id>（匹配度：65，按需级）：能力说明
是否启用推荐协同？
回复：approve / revise / reject
```

## 6. 许可兼容性校验

1. **强制校验**：所有协同 Skill 必须做许可兼容性检查，不兼容的不得进入推荐协同
2. **兼容性规则**：
   - AGPL-3.0 与 AGPL-3.0、GPL-3.0、MIT、BSD 兼容，可自动联动
   - 与闭源、专有许可不兼容，标记为高风险，需用户手动确认才能启用
   - grill-me 遵循自身许可，保持独立，不构成合并
3. **校验节点**：探测阶段自动校验；G5 合规门复核；用户手动启用时二次提示

AGPL-3.0 兼容矩阵：

| 协同 Skill 许可 | 兼容性 | 处理 |
| --- | --- | --- |
| AGPL-3.0 | 兼容 | 自动联动 |
| GPL-3.0 | 兼容 | 自动联动 |
| MIT | 兼容 | 自动联动 |
| BSD | 兼容 | 自动联动 |
| 闭源 | 不兼容（高风险） | 需用户手动确认才能启用 |
| 专有许可 | 不兼容（高风险） | 需用户手动确认才能启用 |
| grill-me（自持许可） | 独立 | 不构成合并，保持独立 |

## 7. 协同状态管理

### 7.1 ecosystem.json 结构

```
{
  "scan_time": "2026-09-13T10:00:00Z",
  "total_installed": 12,
  "skills": {
    "<skill_id>": {
      "name": "xxx",
      "version": "x.y.z",
      "license": "xxx",
      "match_score": 85,
      "level": "recommended | on_demand | disabled",
      "in_pool": true | false,
      "call_point": "gate_g6",
      "calls": [
        {
          "call_id": "EC-0001",
          "ticket_id": "T-001",
          "timestamp": "2026-09-13T10:05:00Z",
          "result": "ok | failed | skipped",
          "output_ref": "events/events.jsonl#EV-000123"
        }
      ],
      "failed_streak": 0
    }
  }
}
```

### 7.2 失败降级规则

1. 协同 Skill 调用失败不阻塞主流程，记录事件，继续执行
2. 连续 3 次调用失败 → 自动移出协同池，记录事件，本 Run 内不再自动调用
3. 格式转换类调用失败 → 回退到默认交付格式，不影响核心产物交付

## 8. 命令与控制

### 8.1 新增命令

| 命令 | 功能 |
| --- | --- |
| `/ccf skills scan` | 手动全量扫描已安装 Skill，更新推荐列表 |
| `/ccf skills list` | 列出当前协同池、匹配度、状态 |
| `/ccf skills enable <skill_id>` | 手动启用某个 Skill 进入协同池 |
| `/ccf skills disable <skill_id>` | 手动禁用某个 Skill，移出协同池 |
| `/ccf skills auto on/off` | 开启/关闭自动推荐协同功能 |

### 8.2 关闭协同

用户可通过 `/ccf skills auto off` 关闭自动推荐，仅保留 grill-me 强制联动，其余协同不再自动探测和提示。

## 9. 相关事件

| 事件 | 触发 |
| --- | --- |
| ECOSYSTEM_SCANNED | 全量扫描完成 |
| ECOSYSTEM_MATCHED | 匹配完成，生成推荐列表 |
| ECOSYSTEM_CONFIRMED | 用户确认协同池 |
| ECOSYSTEM_CALL_INITIATED | 协同调用发起 |
| ECOSYSTEM_CALL_OK | 协同调用成功 |
| ECOSYSTEM_CALL_FAILED | 协同调用失败 |
| ECOSYSTEM_DISABLED | 协同被禁用 |
| ECOSYSTEM_AUTO_TOGGLED | 自动协同开关切换 |

## 10. 协同分级速查

| 协同级别 | 确认方式 | 调用方式 | 阻塞主流程 |
| --- | --- | --- | --- |
| 强制联动（grill-me） | 无需确认 | 自动调用 | 否 |
| 推荐协同 | H1 确认 | 自动按编排调用 | 否 |
| 按需协同 | 环节前提示 | 用户单次确认 | 否 |
| 禁用 | — | 不调用 | — |

## 11. 相关文件

| 文件 | 内容 |
| --- | --- |
| integration-grill-me.md | 强制联动（grill-me）细则 |
| gates.md | G5 合规门复核、协同输出作为补充输入 |
| persistence.md | ecosystem.json 持久化 |
| license.md | AGPL-3.0 许可兼容性 |

---

YESTEST // ecosystem // V1.3 // G0