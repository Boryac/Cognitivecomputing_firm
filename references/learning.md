# learning.md

**路径**：`references/learning.md`（加载时机：BOOTSTRAP 阶段 4，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 职能设定

Learning（学习适配职能）由 Learning Lead 负责，承担数据沉淀、画像构建、适配建议、边界守护与回滚支持；个人清单见 `references/individuals.md` 第 4.11 节，负责人契约见 `references/roles.md` 第 12 节。

职责：

| 项 | 内容 |
| --- | --- |
| 数据沉淀 | 收集运行数据、用户修正、反馈信号 |
| 画像构建 | 生成并迭代用户 profile |
| 适配建议 | 生成优化建议，按分级应用 |
| G11 学习门 | 学习门否决权，守护核心规则 |
| 回滚支持 | 支持画像版本回滚 |

## 2. 数据沉淀

- 采集来源：全量运行数据、用户修正、反馈信号（每轮 TURN 的 LEARN 步骤）。
- 采集内容：交付格式选择、主题偏好、任务粒度、个人权重、术语偏好、适用范围信号。
- 信号写入 events/events.jsonl，画像沉淀到 state/profile.json（见 `references/persistence.md`）。
- TURN 第 12 步 LEARN 不阻塞主流程。

## 3. 画像构建

profile.json 结构与 `assets/profile.template.json` 一致：

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

字段说明：

| 字段 | 说明 |
| --- | --- |
| version | 画像版本，格式 P-N，版本化可追溯 |
| preferences | 偏好项：默认交付格式、主题、任务粒度、个人权重、术语偏好 |
| adaptations | 适配记录：adapt_id、类型、描述、应用时间、决策等级、状态 |
| blacklist | 黑名单（第 6 节）：核心规则，永不自动修改 |

画像输出格式（`/ccf profile`）：

```
YESTEST // PROFILE // P-2
版本：P-2
更新时间：...
偏好：
  - 默认交付格式：PDF
  - 主题：亮色
  - 任务粒度：标准
适配记录：
  - AD-0001：...
黑名单：核心规则不自动修改
```

## 4. 适配建议与分级应用

适配按决策等级分级应用：

| 等级 | 类型 | 应用方式 |
| --- | --- | --- |
| D0 | 信息、草稿、测试、内部文档 | 按协议执行 |
| D1 | 工具、实现、排期、小预算、学习适配 | 按协议执行 + 抽样审计 |
| D2 | 跨模块、中风险、D2 级适配 | 按协议执行 + 抽样审计 |
| D3 | 不可逆、对外、法律、安全、大预算、D3 级适配 | 人工确认（H2） |
| D4 | 目标、终止、转向、核心规则变更 | 人工决策（H4） |

学习适配应用规则：

- D0、D1 级适配：可自动应用（manifest `auto_apply_d0`、`auto_apply_d1` 默认开启）
- D2 级适配：自动应用 + 抽样审计（约束 L-5：D2 以上适配必须人工确认，按本表执行）
- D3 级适配：H2 人工确认后应用
- D4 级适配：H4 人工决策
- 决策等级判断依据 PRD 9.1 决策分级表与决策树（9.4）

## 5. G11 学习门

| 项 | 内容 |
| --- | --- |
| 否决方 | Learning Lead |
| 检查 | 适配边界、核心规则守护、黑名单校验（GR-11） |
| 拦截 | 所有突破核心边界的学习适配 |
| 事件 | LEARNING_GATE_BLOCKED（学习门拦截违规适配） |

## 6. 黑名单

以下核心规则禁止自动修改（L-4 黑名单内项禁止自动修改；manifest blacklist 声明一致）：

```
style_law
expression_constraint
license
organization_hierarchy
gate_veto
h_point_structure
security_compliance
```

对应约束 L-2：不修改核心协议、风格法、表达约束、许可规则。

## 7. 回滚支持

- 画像版本化（manifest `profile_versioning: true`），支持版本回滚。
- 所有适配变更可追溯、可回滚（L-3）。
- 命令：`/ccf profile rollback` 回滚上一版画像；`/ccf profile reset` 重置画像。

## 8. 用户命令

| 命令 | 功能 |
| --- | --- |
| `/ccf profile` | 查看用户画像 |
| `/ccf profile rollback` | 回滚上一版画像 |
| `/ccf profile reset` | 重置画像 |

## 9. manifest 声明

```yaml
learning:
  enabled: true
  profile_versioning: true
  auto_apply_d0: true
  auto_apply_d1: true
  blacklist: [style_law, expression_constraint, license, organization_hierarchy, gate_veto, h_point_structure, security_compliance]
  rollback_support: true
```

## 10. 相关事件

| 事件 | 触发 |
| --- | --- |
| LEARNING_PROFILE_UPDATED | 用户画像更新 |
| LEARNING_ADAPT_APPLIED | 适配建议应用 |
| LEARNING_GATE_BLOCKED | 学习门拦截违规适配 |

## 11. 边界

- 自升级不修改风格法、表达约束、许可、门禁等核心机制（验收标准 A-60）。
- 黑名单内项禁止自动修改（L-4）；G11 学习门与黑名单双重防护（风险 R-33）。
- 画像数据版本化管理，支持回滚与重置（风险 R-34）。

## 12. 相关文件

| 文件 | 内容 |
| --- | --- |
| persistence.md | profile.json 持久化与检查点 |
| gates.md | G11 学习门 |
| roles.md | Learning 职能契约（L-1..L-5） |
| charter.md | 约束优先级 |

---

YESTEST // learning // V1.3 // G0