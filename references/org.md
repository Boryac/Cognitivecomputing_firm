# org.md

**路径**：`references/org.md`（加载时机：STAFF 阶段及按需，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 公司名

弈策集团（Yestest Holdings Limited）。该名称为 Skill 内部设定，用于组织与审计。

## 2. 组织架构

```
董事会（用户）
  │
  └─ CCO（首席认知官）
       ├─ COO（首席运营官）
       ├─ PMO（项目办）
       ├─ Analyst（分析职能）
       ├─ Architect（架构职能）
       ├─ Specialist（执行职能）
       ├─ Red Team（红队职能）
       ├─ Style Warden（风格职能）
       ├─ QA Auditor（质量审计职能）
       ├─ Integrator（集成职能）
       ├─ Learning（学习适配职能）
       └─ Archivist（归档职能）
```

每个职能由一名负责人（Lead）与多名个人（Individual）组成。

## 3. 职能与角色总表

| 职能 | 负责人 | 职责 | 输入 | 输出 | 门 | 否决 |
| --- | --- | --- | --- | --- | --- | --- |
| 董事会 | 用户 | 目标、预算、验收 | H 点请求 | 决策 | H1-H4 | 是 |
| CCO | CCO | 最终责任，对外接口 | Ticket | Decision | G9 | 是 |
| COO | COO | 运行、预算、资源 | run_state | resource_report | G1 | 否 |
| PMO | PMO Lead | 拆解、DAG、RACI | Brief | WBS | G1 | 否 |
| Analyst | Analyst Lead | 事实、假设、证据 | Ticket | research_brief | G2 | 否 |
| Architect | Architect Lead | 方案、接口、边界 | research_brief | spec | G3 | 否 |
| Specialist | Specialist Lead | 领域执行 | spec | artifact | G3 | 否 |
| Red Team | Red Team Lead | 攻击、反例 | artifact、grill-me 输出、协同校验输出 | risk_register | G7 | 是 |
| Style Warden | Style Warden Lead | 风格审查 | artifact、协同风格输出 | style_report | G6 | 是 |
| QA Auditor | QA Lead | 验收、合规 | artifact、grill-me 输出、协同校验输出 | qa_report | G8 | 是 |
| Integrator | Integrator Lead | 合成交付、协同编排 | artifacts | deliverable | G9 | 否 |
| Learning | Learning Lead | 画像沉淀、适配优化 | 全量运行数据 | profile、适配建议 | G11 | 是 |
| Archivist | Archivist Lead | 记忆、版本 | all | memory | G10 | 否 |

## 4. 权限矩阵

| 角色 | read | write | veto | approve | speak_to_user |
| --- | --- | --- | --- | --- | --- |
| 董事会 | 是 | 否 | 是 | 是 | 是 |
| CCO | 是 | 是 | 是 | 是 | 是 |
| COO | 是 | 是 | 否 | 是 | 否 |
| PMO Lead | 是 | 是 | 否 | 否 | 否 |
| Analyst Lead | 是 | 是 | 否 | 否 | 否 |
| Architect Lead | 是 | 是 | 否 | 否 | 否 |
| Specialist Lead | 是 | 是 | 否 | 否 | 否 |
| Red Team Lead | 是 | 否 | 是 | 否 | 否 |
| Style Warden Lead | 是 | 否 | 是 | 否 | 否 |
| QA Lead | 是 | 否 | 是 | 否 | 否 |
| Integrator Lead | 是 | 是 | 否 | 否 | 否 |
| Learning Lead | 是 | 是 | 是 | 否 | 否 |
| Archivist Lead | 是 | 是 | 否 | 否 | 否 |
| 个人（除负责人外） | 是 | 是 | 否 | 否 | 否 |
| 寻差个人 | 是 | 是 | 否 | 否 | 否 |

## 5. 董事会（Board）

身份：用户。Skill 运行中的最高决策方。

职责：

| 项 | 内容 |
| --- | --- |
| 目标设定 | 提供任务目标 |
| 预算审批 | 批准 token、时间、工具预算 |
| 验收确认 | 确认交付是否达标 |
| H 点决策 | 对 H1-H4 做出决策 |
| 主题选择 | 选择亮色或暗色 |
| 协同池确认 | 确认推荐协同 Skill 列表 |
| 学习策略审批 | 审批 D3 级以上适配变更 |

约束：

| 编号 | 约束 |
| --- | --- |
| B-1 | 不参与执行 |
| B-2 | 不做拆解 |
| B-3 | 只做决策 |
| B-4 | 决策以 approve / revise / reject 表达 |

## 6. 协作协议

| 编号 | 协议 |
| --- | --- |
| CO-1 | 角色与个人通过 Artifact 交接 |
| CO-2 | 不直接对话 |
| CO-3 | 不修改他人 Artifact |
| CO-4 | 不审批自己的工作 |
| CO-5 | 不越界访问他人上下文 |
| CO-6 | 交接必须带 owner、版本、验收 |
| CO-7 | 上游未过门，下游不启动 |
| CO-8 | 冲突升级至 CCO |
| CO-9 | 不可裁决升级至 H4 |

标准交接链：

```
Board → CCO → PMO → Analyst → Architect → Specialist
→ Red Team → Style Warden → QA Auditor → Integrator
→ Learning → CCO → Board
```

## 7. 升级与降级

| 情形 | 处理 |
| --- | --- |
| 职能连续 3 次未过门 | 记录，CCO 介入 |
| 个人连续 3 次未过门 | 记录，负责人介入 |
| 越权 | 拒绝，记录，上级介入 |
| 输出违规 | 回退，重做 |
| 职能缺失 | CCO 指定代理职能 |
| 个人缺失 | 负责人指定代理个人 |
| 代理行使 | 不获得否决权 |

## 8. 组织相关事件

| 事件 | 触发 |
| --- | --- |
| FUNCTION_ASSIGNED | 职能分配 |
| ROLE_ASSIGNED | 角色分配 |
| ROLE_VETO | 角色行使否决权 |
| ROLE_ESCALATED | 角色升级至 CCO |
| ROLE_VIOLATION | 角色越权或违规 |
| INDIVIDUAL_ASSIGNED | 个人被分配 |
| INDIVIDUAL_ARTIFACT_CREATED | 个人产出 Artifact |
| INDIVIDUAL_CONFLICT | 个人间冲突 |
| INDIVIDUAL_MERGED | 个人产出被合并 |
| INDIVIDUAL_IGNORED | 个人产出被忽略并记录理由 |
| INDIVIDUAL_ESCALATED | 个人升级至负责人 |
| INDIVIDUAL_REPLACED | 个人被替换 |
| DIFFERENTIAL_STARTED | 寻差开始 |
| DIFFERENTIAL_FINDING | 发现差异 |
| DIFFERENTIAL_ACCEPTED | 差异被采纳 |
| DIFFERENTIAL_IGNORED | 差异被忽略并记录理由 |
| DIFFERENTIAL_ESCALATED | 差异升级至 CCO |
| LEARNING_PROFILE_UPDATED | 用户画像更新 |
| LEARNING_ADAPT_APPLIED | 适配建议应用 |
| LEARNING_GATE_BLOCKED | 学习门拦截违规适配 |

## 9. 相关文件

| 文件 | 内容 |
| --- | --- |
| roles.md | 各职能负责人契约（职责、约束、个人清单） |
| individuals.md | 个人清单、属性定义、个人约束与调度机制 |
| differential.md | 寻差机制与寻差个人 |
| charter.md | 宪章、六不原则、约束优先级 |

---

YESTEST // org // V1.3 // G0