# differential.md

**路径**：`references/differential.md`（加载时机：STAFF 阶段与寻差需求触发时，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 定义

寻差（Differential Discovery）：主动寻找被忽略的差异、边界、反例、假设、替代。

寻差由专职个人执行，贯穿分析、架构、执行与各审查职能。寻差个人产出无否决权，但必须被记录。

## 2. 寻差个人清单

| 职能 | 寻差个人 | 职责 |
| --- | --- | --- |
| Analyst | gamma | 找被忽略项 |
| Architect | delta | 找替代方案 |
| Specialist | beta | 找新路径 |
| Red Team | differential | 交叉对比 |
| Style Warden | differential | 风格漂移检测 |
| QA | differential | 声明与实现差异 |
| Archivist | differential | 前后差异归档 |

## 3. 寻差产出结构

```
finder: gamma
function: analyst
findings:
  - type: omitted_difference | default_assumption | merged_boundary | ignored_counterexample | alternative_path | drift | spec_impl_gap
    description: ...
    severity: low | medium | high
    evidence: ...
    recommendation: ...
```

## 4. 寻差强制规则

| 编号 | 规则 |
| --- | --- |
| DD-1 | 高寻差需求任务必须调用寻差个人 |
| DD-2 | 寻差个人产出必须写入 differential_findings |
| DD-3 | differential_findings 必须作为 G7、G8 的输入 |
| DD-4 | 寻差个人不因进度压力跳过 |
| DD-5 | 寻差个人产出无否决权，但必须被记录 |
| DD-6 | 寻差个人产出被忽略时必须记录理由 |

## 5. 寻差发现输出格式

```
YESTEST // DIFFERENTIAL // FINDING
finder: gamma
function: analyst
type: omitted_difference
severity: medium
description: ...
evidence: ...
recommendation: ...
status: accepted | ignored | escalated
```

## 6. differential.json 结构

寻差发现的持久化结构（与 `references/persistence.md` 第 4.5 节一致，模板见 `assets/` 对应契约）：

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

## 7. 与门禁的关系

| 门 | 关系 |
| --- | --- |
| G7 红队门 | differential_findings 作为补充输入（DD-3） |
| G8 QA 门 | differential_findings 作为补充输入（DD-3） |
| 其他门 | 无直接关系 |

寻差发现分级处理：仅高严重度 finding 强制处理；其余按负责人判断采纳或忽略（依据 PRD 22 风险 R-18）。

## 8. 寻差事件

| 事件 | 触发 |
| --- | --- |
| DIFFERENTIAL_STARTED | 寻差开始 |
| DIFFERENTIAL_FINDING | 发现差异 |
| DIFFERENTIAL_ACCEPTED | 差异被采纳 |
| DIFFERENTIAL_IGNORED | 差异被忽略并记录理由 |
| DIFFERENTIAL_ESCALATED | 差异升级至 CCO |

## 9. 与组织机制的关系

- 寻差个人属个人体系，受个人通用约束 IP-1..IP-10 约束（`references/individuals.md`）。
- 寻差个人无否决权（下表），不替代任何审查职能：

| 角色 | 是否有否决权 |
| --- | --- |
| 寻差个人 | 否（DD-5） |
| Red Team Lead | 是（G7） |
| Style Warden Lead | 是（G6） |
| QA Lead | 是（G8） |

---

YESTEST // differential // V1.3 // G0