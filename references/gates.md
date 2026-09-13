# gates.md

**路径**：`references/gates.md`（加载时机：GATE 阶段，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 门列表

| 门 | 名称 | 检查 | 否决方 |
| --- | --- | --- | --- |
| G0 | 立项门 | 目标、范围、验收 | CCO |
| G1 | 范围门 | WBS、DAG、RACI | PMO Lead |
| G2 | 证据门 | 事实、假设、来源、置信度 | Analyst Lead |
| G3 | 架构门 | 接口、边界、约束 | Architect Lead |
| G4 | 安全门 | 权限、隐私、合规 | QA Lead |
| G5 | 合规门 | 法律、政策、许可、协同许可兼容性 | QA Lead |
| G6 | 风格门 | macOS Vibrancy 合规 | Style Warden Lead |
| G7 | 红队门 | 失败模式、反例、寻差发现、协同校验输出 | Red Team Lead |
| G8 | QA 门 | 验收、可追溯、寻差发现、协同校验输出 | QA Lead |
| G9 | 交付门 | 完整、可执行、表达合规、许可合规、交付格式 | CCO |
| G10 | 归档门 | 记忆、版本、审计 | Archivist Lead |
| G11 | 学习门 | 适配边界、核心规则守护、黑名单校验 | Learning Lead |

## 2. 门规则

| 编号 | 规则 |
| --- | --- |
| GR-1 | 每门有检查清单 |
| GR-2 | 每门有校验流程 |
| GR-3 | 每门有失败回退 |
| GR-4 | 不过门不交付 |
| GR-5 | 一票否决生效 |
| GR-6 | 连续 3 次失败触发 H4 |
| GR-7 | grill-me 输出作为 G7、G8 补充输入 |
| GR-8 | differential_findings 作为 G7、G8 补充输入 |
| GR-9 | G5、G9 检查 AGPL-3.0 许可与来源声明 |
| GR-10 | 协同 Skill 输出仅作为对应门禁的补充输入，不替代原有角色职责，无一票否决权 |
| GR-11 | G11 拦截所有突破核心边界的学习适配 |

## 3. 门禁执行算法

```
输入：artifact, differential_findings, ecosystem_outputs
1. 识别 artifact 类型
2. 确定必经门
3. 逐门执行
4. 每门：跑校验、跑清单、收集否决意见
5. G7、G8 附加读取 grill-me 输出、协同输出与 differential_findings
6. G5、G9 附加读取许可声明与来源声明
7. G11 附加校验学习适配合规性
8. 若否决 → 记录 + 回退
9. 全过 → 下一阶段
```

## 4. 门禁报告结构

结构与 `assets/gate-report.template.yaml` 一致：

```
gate_report_id: GR-001
run_id: CCF-YYYY-MM-DD-NNN
ticket_id: T-001
artifact_id: A-001

gate_id: "G0 | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | G10 | G11"
gate_name: ""
veto_owner: "CCO | PMO Lead | Analyst Lead | Architect Lead | QA Lead | Style Warden Lead | Red Team Lead | Integrator Lead | Archivist Lead | Learning Lead"

checks:
  - check_id: C-001
    description: ""
    required: true
    passed: true
    evidence: ""
    notes: ""

supplementary_inputs:
  integration_outputs: []
  ecosystem_outputs: []
  differential_findings: []

veto:
  cast: false
  by: ""
  reason: ""

result: "pass | fail"
fallback: "none | rollback | re_execute | h2 | h4"
checked_by: ""
checked_at: "ISO8601"
version: 1
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| gate_report_id | 门禁报告编号，格式 GR-001 |
| gate_id / gate_name | 门标识与名称（G0-G11） |
| veto_owner | 当前门的否决方 |
| checks | 检查清单，每项含 check_id、描述、是否必需、是否通过、证据、备注 |
| supplementary_inputs | 补充输入：integration_outputs、ecosystem_outputs、differential_findings |
| veto | 否决记录：是否行使、行使者、理由 |
| result | pass / fail |
| fallback | 失败回退：none / rollback / re_execute / h2 / h4 |
| checked_by / checked_at | 检查人与时间 |
| version | 报告版本 |

## 5. 门与人工干涉的关系

- 门禁连续 3 次失败触发 H4（GR-6）。
- G9 交付门加入表达检查，违规即回退（见 `references/expression.md`）。
- G5、G9 检查 AGPL-3.0 许可与来源声明（见 `references/license.md`）。
- grill-me 与协同输出仅作补充输入，无否决权（GR-7、GR-10）。

## 6. 相关文件

| 文件 | 内容 |
| --- | --- |
| style.md | G6 风格门检查依据 |
| expression.md | G9 表达检查依据 |
| license.md | G5、G9 许可检查依据 |
| differential.md | G7、G8 寻差发现输入 |
| integration-grill-me.md | G7、G8 grill-me 补充输入 |
| ecosystem.md | 协同校验输出在各门的补充输入规则 |

---

YESTEST // gates // V1.3 // G0