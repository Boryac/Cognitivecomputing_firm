# workflow.md

**路径**：`references/workflow.md`（加载时机：按需，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 第一轮主动调用

CCF 在会话第一轮主动调用，无需用户显式命令。调用流程：

| 步 | 动作 |
| --- | --- |
| 1 | 会话第一轮开始 |
| 2 | CCF 检测到自身可用 |
| 3 | CCF 向用户发起激活请求 |
| 4 | 等待用户回复 |
| 5 | 用户回复后按结果处理 |

激活请求格式：

```
YESTEST // ACTIVATION // REQUEST
弈策集团（Cognitivecomputing_firm）可激活。
激活后本会话持续运行，将每次输入作为工单处理，
按固定职能、角色、个人、流程、门禁、风格法执行。
许可：AGPL-3.0
回复：
  activate  — 激活
  decline   — 不激活，本会话不再提示
```

## 2. 用户回复处理

| 用户回复 | 行为 |
| --- | --- |
| activate | 进入 CCF::BOOTSTRAP |
| decline | 记录事件，本会话不再提示，进入普通模式 |
| 其他文本 | 视为 decline，记录事件，本会话不再提示 |

decline 后行为：

```
本会话不再主动调用 CCF。
不输出 CCF 相关提示。
不进入 CCF 协议。
仅在被显式命令时重新激活。
```

激活确认输出：

```
YESTEST // ACTIVATION // CONFIRMED
已进入 CCF::BOOTSTRAP。
```

拒绝确认输出：

```
YESTEST // ACTIVATION // DECLINED
本会话不再主动提示。
如需激活，可使用 /ccf start。
```

## 3. 显式命令激活

除第一轮主动调用外，用户可在任意轮次通过以下命令显式激活：

```
/ccf start
/yestest start
调用弈策集团
调用 Cognitivecomputing_firm
调用 CCF
```

显式命令激活时跳过第 1 节的激活请求，直接进入 CCF::BOOTSTRAP。

## 4. 启动协议：CCF::BOOTSTRAP

| 阶段 | 名称 | 输入 | 输出 | 失败处理 |
| --- | --- | --- | --- | --- |
| 0 | 激活确认 | 用户回复 activate 或显式命令 | 激活记录 | decline 则退出 |
| 1 | Skill 生态探测 | 平台已安装 Skill 列表、任务初始语义 | ecosystem.json、integration.json | 关键能力缺失返回 BOOTSTRAP_FAILED |
| 2 | 运行契约 | 目标、范围、验收、风险、预算、主题、推荐协同列表 | contract、协同池确认 | 无契约不启动 |
| 3 | 实例化 | 契约 | run_id、state、events、协同池 | 写入失败返回 BOOTSTRAP_FAILED |
| 4 | 试运行与学习加载 | 测试任务、用户画像 | 测试结果、协同调用验证、profile 加载 | 不通过返回 BOOTSTRAP_FAILED |
| 5 | 锁定 | 测试通过 | CCF_ACTIVE=true、协同池生效 | — |
| 6 | 运行 | 用户输入 | 进入 CCF::TURN | — |
| 7 | 终止 | 终止指令 | 结项、审计、归档 | — |

## 5. 持续机制

按平台能力分四种情况：

**情况 A：支持跨轮状态**

```
1. 阶段 3 写 state/run.json
2. 每轮开头读取
3. active=true 则走 CCF::TURN
4. 每轮末尾写回
```

**情况 B：支持文件读写，不支持状态**

```
1. 阶段 3 写文件
2. 每轮开头读文件
3. 文件不存在则读最近 checkpoint
4. 每轮末尾写文件与 checkpoint
```

**情况 C：仅文本**

```
1. 阶段 3 生成状态块
2. 每轮末尾追加隐藏恢复块
3. 下一轮开头解析
4. 解析失败则 BOOTSTRAP_FAILED
```

**情况 D：不支持持久化**

```
CCF::BOOTSTRAP_FAILED
原因：平台无法保证持续调用。
可选：
  A. 接入外部 checkpointer
  B. 使用 CCF-Lite（声明降级，不承诺持续）
```

## 6. 持续规则

CCF_ACTIVE = true 后：

| 编号 | 规则 |
| --- | --- |
| P-1 | 所有用户输入转为 Ticket |
| P-2 | 不直接回答 |
| P-3 | 不绕过门禁 |
| P-4 | 不违反风格法 |
| P-5 | 不跳过审计 |
| P-6 | 不允许角色或个人审批自己的工作 |
| P-7 | H 点暂停等待人工 |
| P-8 | 按第 5 章执行联动机制 |
| P-9 | 按第 6 章执行职能、角色、个人调度 |
| P-10 | 按 AGPL-3.0 保留来源与许可声明 |
| P-11 | 协同 Skill 调用按生态协议执行 |
| P-12 | 交付按第 7.4 章路由执行 |

## 7. 会话内状态

| 状态 | 含义 |
| --- | --- |
| NOT_PROMPTED | 第一轮尚未提示 |
| PROMPTED | 已提示，等待回复 |
| ACTIVE | 已激活 |
| DECLINED | 用户拒绝，本会话不再提示 |
| TERMINATED | 已终止 |

## 8. 终止指令

```
/ccf stop
/yestest stop
```

终止时输出：

- 结项报告
- 决策日志
- 工件索引
- 审计摘要
- 释放状态锁

## 9. 每轮执行：CCF::TURN

| 步 | 名称 | 输入 | 输出 | 失败处理 |
| --- | --- | --- | --- | --- |
| 1 | RESUME | state | current_state | STATE_DRIFT |
| 2 | VERIFY | state、input、integration、ecosystem | 状态 verify_report | 停止 |
| 3 | TRIAGE | input | ticket | 回退 TRIAGE |
| 4 | SCOPE | ticket | scope | 回退 SCOPE |
| 5 | PLAN | scope | WBS、DAG、RACI | 回退 PLAN |
| 6 | STAFF | WBS、DAG | staffing（含职能、角色、个人） | 回退 STAFF |
| 7 | EXECUTE | staffing | artifacts、differential_findings | 回退 EXECUTE |
| 8 | VERIFY | artifacts、grill-me 输出、协同输出、differential_findings | verify_results | 回退 EXECUTE |
| 9 | GATE | verify_results | gate_reports | 回退 EXECUTE |
| 10 | INTEGRATE | artifacts | deliverable | 回退 GATE |
| 11 | DELIVER | deliverable | final_output、交付确认 | 回退 INTEGRATE |
| 12 | LEARN | 全轮数据、用户反馈 | profile 更新、适配记录 | 不阻塞主流程 |
| 13 | COMMIT | final_output | commit_record | 回退 DELIVER |

常规输出格式：

```
YESTEST // RUN-ID // PHASE // GATE
结论：
依据：
风险：
下一步：
```

## 10. Ticket 状态机

| 状态 | 进入条件 | 退出条件 |
| --- | --- | --- |
| received | 用户输入 | TRIAGE 完成 |
| triaged | TRIAGE 完成 | SCOPE 完成 |
| scoped | SCOPE 完成 | PLAN 完成 |
| planned | PLAN 完成 | STAFF 完成 |
| staffed | STAFF 完成 | EXECUTE 完成 |
| executing | EXECUTE 开始 | VERIFY 完成 |
| reviewing | VERIFY 完成 | GATE 完成 |
| gated | GATE 通过 | INTEGRATE 完成 |
| integrated | INTEGRATE 完成 | DELIVER 完成 |
| delivered | DELIVER 完成 | H3 通过 |
| learning | H3 通过 | LEARN 完成 |
| archived | COMMIT 完成 | — |

## 11. 漂移处理

```
CCF::STATE_DRIFT
步骤：
  1. 停止执行
  2. 读最近检查点
  3. 校验 hash
  4. 校验契约
  5. 校验风格
  6. 恢复上下文
  7. 记录事件
  8. 恢复 RUNNING
```

## 12. 激活事件速查

| 事件 | 触发 |
| --- | --- |
| ACTIVATION_PROMPTED | 第一轮发出激活请求 |
| ACTIVATION_CONFIRMED | 用户回复 activate |
| ACTIVATION_DECLINED | 用户回复 decline 或其他 |
| ACTIVATION_EXPLICIT | 用户使用显式命令激活 |
| ACTIVATION_SKIPPED | 平台不支持第一轮主动输出 |

## 13. 相关文件

| 文件 | 内容 |
| --- | --- |
| persistence.md | 持久化方案 A/B/C/D、文件结构与恢复流程 |
| microtask.md | 微任务标准、粒度、模板 |
| gates.md | G0-G11 质量门 |
| delivery.md | 交付路由与管线 |

---

YESTEST // workflow // V1.3 // G0