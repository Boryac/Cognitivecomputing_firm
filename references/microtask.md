# microtask.md

**路径**：`references/microtask.md`（加载时机：按需，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 任务层级

| 层 | 定义 | 数量范围 |
| --- | --- | --- |
| Intent | 用户意图 | 1 |
| Epic | 可独立验收目标 | 1-5 |
| Workstream | 连续工作流 | 2-10 |
| Workcell | 独立执行上下文 | 3-30 |
| MicroTask | 最小可交付 | 10-200 |

## 2. MicroTask 属性

| 属性 | 要求 |
| --- | --- |
| 目标 | 单一 |
| 产物 | 单一 |
| 责任人 | 单一 |
| 验收 | 单一 |
| 回滚 | 支持 |
| 上下文 | 独立 |
| 预算 | 有限 |
| 依赖 | 明确 |
| 个人 | 明确指定 |

## 3. 粒度阈值

满足任一条件，强制拆分：

| 条件 | 阈值 |
| --- | --- |
| 上下文窗口 | 1 |
| 步骤数 | 3 |
| 主产物数 | 1 |
| 验收条件数 | 3 |
| 角色数 | 1 |
| 依赖数 | 3 |
| 预估耗时 | 1 轮 TURN |

## 4. MicroTask 模板

结构与 `assets/microtask.template.yaml` 一致：

```
microtask_id: MT-001
parent: WC-001
objective: ...
function: analyst
individual: gamma
inputs: []
outputs: []
acceptance: []
budget: { tokens: ..., tools: ... }
rollback: ...
status: pending
gate: G2
integration_inputs: []
ecosystem_inputs: []
differential_required: true | false
learning_weight: default
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| microtask_id | 微任务编号，格式 MT-001 |
| parent | 所属 Workcell 编号，格式 WC-001 |
| objective | 单一目标 |
| function | 承担职能：cco / coo / pmo / analyst / architect / specialist / red_team / style_warden / qa / integrator / learning / archivist |
| individual | 明确指定的个人代号 |
| inputs / outputs | 输入与产物清单 |
| acceptance | 单一验收条件 |
| budget | 有限预算（tokens、tools） |
| rollback | 回滚路径 |
| status | pending / executing / passing / failed / committed / checkpointed |
| gate | 目标门禁：G0-G11 |
| integration_inputs | grill-me 补充输入引用 |
| ecosystem_inputs | 协同 Skill 补充输入引用 |
| differential_required | 是否需寻差 |
| learning_weight | 学习权重：default / high / low |

## 5. 执行循环

```
执行 → 验证 → 通过 → 提交 → 检查点 → 解锁下游
失败 → 回滚 → Bug Report → 重新拆解
连续 3 次失败 → H4
```

## 6. 拆分算法

```
输入：Epic
1. 提取目标、验收、约束
2. 列出主产物
3. 主产物 → Workstream
4. Workstream → Workcell
5. Workcell → MicroTask
6. 检查粒度阈值
7. 超阈值继续拆
8. 分配职能与个人
9. 标注是否需寻差
10. 建立依赖边
11. 拓扑排序
12. 输出 DAG
```

## 7. 相关文件

| 文件 | 内容 |
| --- | --- |
| roles.md | 职能与负责人，个人分配依据 |
| individuals.md | 个人清单与调度机制 |
| differential.md | 寻差需求（differential_required）触发规则 |
| persistence.md | MicroTask 检查点与状态持久化 |

---

YESTEST // microtask // V1.3 // G0