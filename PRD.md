# CCF 产品需求文档（PRD）

![弈策集团标识](透明底无字logo.png)

| 项 | 内容 |
| --- | --- |
| 产品名称 | 弈策集团（Yestest Holdings Limited）/ CCF |
| 技能标识 | cognitivecomputing-firm |
| 文档版本 | V1.4 |
| 许可 | AGPL-3.0 |
| 规格地位 | 本文件为唯一规格来源；`references/`、`scripts/`、`evals/` 引用的全部章节号与代码项以本文件为准 |

---

## 1. 概述

CCF 是一款公司化多角色工作流技能。激活后，每次用户输入登记为工单，按固定职能、角色、个人、流程、门禁与风格法执行，产出可审计、可回滚的结果。

适用与不适用：

| 类别 | 说明 |
| --- | --- |
| 适用 | 会话内持续执行、分步推进、需可审计可回滚结果的任务 |
| 不适用 | 单轮问答、通用聊天、无状态工具调用 |

## 2. 目标

| 编号 | 目标 |
| --- | --- |
| G-1 | 第一轮主动调用（意图；由平台适配层落地） |
| G-2 | 会话内持续（激活后每轮走 CCF 协议） |
| G-3 | 任务拆分为微任务逐项执行 |
| G-4 | 每轮按固定协议执行 |
| G-5 | 交付前通过 G0–G11 |
| G-6 | 风格统一（macOS Vibrancy，默认 light） |
| G-7 | 可审计（事件、决策、检查点） |
| G-8 | 可回滚（检查点恢复） |
| G-9 | 人工例外仅 H1–H4 |
| G-10 | 表达约束 |
| G-11 | 与 grill-me 联动 |
| G-12 | 每职能多个人 |
| G-13 | 寻差能力 |
| G-14 | 创新与稳健并置 |
| G-15 | AGPL-3.0 开源合规 |
| G-16 | 多 Skill 协同 |
| G-17 | 自升级适配 |
| G-18 | 交付路由 |

---

## 3. 系统架构

### 3.1 分层

| 层 | 载体 | 职责 |
| --- | --- | --- |
| 入口层 | `SKILL.md` | 元数据、激活协议、运行时协议、风格法、表达约束 |
| 规范层 | `references/` | 宪章、组织、门禁、风格、交付、学习等规则 |
| 执行层 | `scripts/` | 状态、路由、校验、门禁、风格、协同、交付、适配 |
| 数据契约层 | `assets/` | run / ticket / microtask / artifact / gate-report 等模板 |
| 验收层 | `evals/` | 10 组验收用例 |
| 平台适配层 | `.claude/commands/`、`platform/` | 首轮提示与斜杠命令的跨平台落地 |

### 3.2 目录结构

```
cognitivecomputing-firm/
├── SKILL.md            入口
├── PRD.md              本规格
├── manifest.yaml       清单（品牌、命令、能力、聚合）
├── LICENSE / COPYING / NOTICE / AUTHORS / CHANGELOG.md
├── 透明底无字logo.png   品牌标识
├── references/         规则文档（含 brand.md、runbook.md）
├── scripts/            11 个可执行脚本
├── assets/             9 份数据契约模板
├── evals/              10 组验收用例
├── platform/           平台适配说明
└── .claude/commands/   Claude Code 斜杠命令
```

### 3.3 references 与 runbook 加载时机

| 文件 | 加载时机 |
| --- | --- |
| `references/runbook.md` | BOOTSTRAP 阶段 0（执行层接线，必需） |
| `references/brand.md` | BOOTSTRAP 阶段 1 |
| `references/charter.md` | BOOTSTRAP 阶段 2 |
| `references/style.md` | BOOTSTRAP 阶段 4 |
| `references/gates.md` | GATE 阶段 |
| `references/persistence.md` | 按需 |
| 其余 references | 按需 |

---

## 4. 激活与生命周期

### 4.1 第一轮主动调用

会话第一轮，CCF 检测到自身可用时向用户发起一次激活请求。因宿主平台不允许技能在会话首轮自行运行，该意图由平台适配层落地（CCF 意图 + 平台承接 = 完整闭环）。

### 4.2 用户回复处理

| 回复 | 行为 |
| --- | --- |
| activate | 进入 CCF::BOOTSTRAP |
| decline | 记录 ACTIVATION_DECLINED，本会话不再提示，普通模式 |
| 其他文本 | 视为 decline |

### 4.3 激活请求格式

```
YESTEST // ACTIVATION // REQUEST
弈策集团（cognitivecomputing-firm）可激活。
激活后本会话持续运行，将每次输入作为工单处理，
按固定职能、角色、个人、流程、门禁、风格法执行。
许可：AGPL-3.0
回复：
  activate  — 激活
  decline   — 不激活，本会话不再提示
```

### 4.4 显式命令激活

`/ccf start`、`/yestest start`、`调用弈策集团`、`调用 cognitivecomputing-firm`、`调用 CCF`。显式激活跳过激活请求，直接进入 BOOTSTRAP。

### 4.5 持久化能力分级

| 情况 | 平台能力 | 机制 |
| --- | --- | --- |
| A | 支持跨轮状态 | 每轮读 `run_state/state/run.json` |
| B | 支持文件读写 | 每轮写文件与 checkpoint |
| C | 仅文本 | 状态块 + 隐藏恢复块 |
| D | 不支持持久化 | `BOOTSTRAP_FAILED`，接入外部 checkpointer |

### 4.6 激活状态机

| 状态 | 含义 |
| --- | --- |
| NOT_PROMPTED | 第一轮尚未提示 |
| PROMPTED | 已提示，等待回复 |
| ACTIVE | 已激活 |
| DECLINED | 已拒绝，本会话不再提示 |
| TERMINATED | 已终止 |

### 4.7 激活事件

ACTIVATION_PROMPTED、ACTIVATION_CONFIRMED、ACTIVATION_DECLINED、ACTIVATION_EXPLICIT、ACTIVATION_SKIPPED。

### 4.8 终止

`/ccf stop`、`/yestest stop` → CCF::TERMINATE：结项报告、决策日志、工件索引、审计摘要、释放锁。

---

## 5. 多 Skill 生态协同

### 5.1 扫描与匹配

BOOTSTRAP 阶段 1 做全量扫描，每轮 VERIFY 做增量探测。

**5.1.1** 扫描来源：平台 skill 目录（`--skills-dir`）或显式清单（`--skills-json`）。

**5.1.2** 清单提取：读取目标 skill 的 `manifest.yaml` / `SKILL.md`（name、version、license、description、tags、capabilities、inputs、outputs）。

**5.1.3** 匹配度算法（0–100）：

| 维度 | 权重 |
| --- | --- |
| 领域/标签重叠 | 0–60 |
| 核心能力重叠 | 0–25 |
| 产出类型匹配 | 0–15 |

### 5.2 grill-me 联动

**5.2.1** 探测：`integration_probe.py probe`，匹配名变体 grill-me / grill_me / GrillMe。

**5.2.2** 决策状态机：installed / declined / later / install_pending / install_failed / unconfirmed / disabled。

**5.2.3** 未安装：每 Run 提示一次 `npx skills add mattpocock/skills/grill-me`；用户回复 install / decline / later。

**5.2.4 真实调用**：`integration_probe.py call` 以子进程真实执行（`--invoke-cmd`）并取回结果；无命令则写入 `run_state/state/outbox.jsonl`，由宿主编排层通过原生 Skill 工具执行后回执。连续 3 次失败自动 disabled（对应 F-5）。

### 5.3 调用编排

**5.3.1** 分级：≥80 recommended / 50–79 on_demand / <50 disabled。

**5.3.2** 调用节点映射：content_check→gate、content_generation→execute、format_conversion→integrate、analysis_enhancement→scope_plan。

**5.3.3 真实调用**：`skill_orchestrator.py call` 以子进程真实执行目标（`--invoke-cmd` 或目标 manifest 的 `invoke` 字段），或写入 outbox 派发；结果（ok/failed/dispatched）写入事件日志，不再伪造成功。

### 5.4 许可兼容

与 AGPL-3.0 兼容判定：compatible（AGPL/GPL/MIT/BSD）/ high_risk（闭源专有）/ review（未声明或其他）。

### 5.5 协同池管理

**5.5.1** ecosystem.json 结构：`scan_time`、`total_installed`、`skills{}`、`auto_enabled`。

**5.5.2** 池管理：仅 in_pool 参与自动调用；并发上限 3；超时 30s；连续 3 次失败自动移出池。

---

## 6. 组织与职能

### 6.1 组织模型

用户为董事会（Board）；CCO 为对外唯一接口；其余职能不直接对用户发言（U-9）。每职能设一名负责人（Lead）与多名个人（Individual）。

### 6.5 权限矩阵

| 角色 | read | write | veto | approve | speak_to_user |
| --- | --- | --- | --- | --- | --- |
| board | ✓ | | ✓ | ✓ | ✓ |
| CCO | ✓ | ✓ | ✓ | ✓ | ✓ |
| COO | ✓ | ✓ | | ✓ | |
| PMO/Analyst/Architect/Specialist/Integrator/Archivist Lead | ✓ | ✓ | | | |
| Red Team / Style Warden / QA Lead | ✓ | | ✓ | | |
| Learning Lead | ✓ | ✓ | ✓ | | |
| individual / differential_individual | ✓ | ✓ | | | |

核心规则：角色或个人不得审批自己的工作（P-6 / U-10）。

### 6.7–6.18 职能清单

| 节 | 职能 | id |
| --- | --- | --- |
| 6.7 | CCO | cco |
| 6.8 | COO | coo |
| 6.9 | PMO | pmo |
| 6.10 | Analyst | analyst |
| 6.11 | Architect | architect |
| 6.12 | Specialist | specialist |
| 6.13 | Red Team | red_team |
| 6.14 | Style Warden | style_warden |
| 6.15 | QA | qa |
| 6.16 | Integrator | integrator |
| 6.17 | Learning | learning |
| 6.18 | Archivist | archivist |

### 6.19–6.20 角色与契约

各职能负责人的职责、约束与升级路径见 `references/roles.md`（SW-1..SW-8 等）。

### 6.21 个人调度算法

1. 寻差需求必调寻差个人（DD-1）；
2. 按专长关键词匹配排序；
3. 按认知风格补齐视角；
4. 用户画像 `individual_weight` 调整优先级。

人数：simple 1 / medium 3 / complex 全部；最小调度 red_team、style_warden、qa 各 ≥2（6.23）。

### 6.22 寻差个人映射

| 职能 | 寻差个人 |
| --- | --- |
| analyst | gamma |
| architect | delta |
| specialist | beta |
| red_team / style_warden / qa / archivist | differential |

### 6.23 最小调度

red_team ≥2、style_warden ≥2、qa ≥2。

### 6.24 约束组装规则

AP-1 全局约束先于职能与个人约束；AP-2 冲突时以全局约束为准。

---

## 7. 交付路由

### 7.1 类型识别

在 SCOPE 阶段由 `ccf_deliver.py` 识别产物类型；无法命中返回 other 并询问（D-5）。

### 7.2 默认格式映射

| 类型 | 默认格式 |
| --- | --- |
| document | pdf |
| spreadsheet | excel |
| presentation | pdf |
| code | source |
| image | png |
| data | json |

### 7.3 交付记录字段

见 `assets/delivery.template.yaml`：delivery_id、run_id、ticket_id、artifact_ids、artifact_type、default_format、selected_format、pipeline、document_pipeline、format_conversion、license_notice、delivered_at、brand_logo。

### 7.4 文档管线

**7.4.1** 类型表见 7.2。

**7.4.2** 文档管线：`MD 源稿 → 用户确认(H3) → LaTeX → PDF`；Word 需显式请求（`approve+word`）。确认选项：approve / approve+word / revise / reject。

**7.4.3** 转换失败回退默认格式（D-3）；许可声明与来源标注保留（D-4）。

### 7.5 交付决策项

| 编号 | 内容 |
| --- | --- |
| D-3 | 格式转换失败回退默认格式 |
| D-4 | 保留 AGPL-3.0 许可声明与来源标注 |
| D-5 | 类型无法识别时询问用户 |

---

## 8. 微任务体系

每个 MicroTask：单目标、单产物、单责任人、单验收、可回滚、独立上下文；指派到具体职能与个人。拆分算法见 `references/microtask.md`。

---

## 9. 学习与自适配

### 9.1 决策分级

| 级别 | 应用方式 |
| --- | --- |
| D0 | 自动应用 |
| D1 | 自动应用 |
| D2 | 自动应用 + 审计 |
| D3 | H2 人工确认 |
| D4 | H4 人工决策 |

黑名单（L-4）：style_law、expression_constraint、license、organization_hierarchy、gate_veto、h_point_structure、security_compliance 永不自动修改；由 G11 拦截。画像版本 P-0、P-1…；支持 rollback / reset。

---

## 10. 质量门禁

### 10.1 门列表

| 门 | 名称 | 否决方 | 回退 |
| --- | --- | --- | --- |
| G0 | 立项门 | CCO | re_execute |
| G1 | 范围门 | PMO Lead | rollback |
| G2 | 证据门 | Analyst Lead | re_execute |
| G3 | 架构门 | Architect Lead | re_execute |
| G4 | 安全门 | QA Lead | rollback |
| G5 | 合规门 | QA Lead | rollback |
| G6 | 风格门 | Style Warden Lead | rollback |
| G7 | 红队门 | Red Team Lead | re_execute |
| G8 | QA 门 | QA Lead | re_execute |
| G9 | 交付门 | CCO | re_execute |
| G10 | 归档门 | Archivist Lead | re_execute |
| G11 | 学习门 | Learning Lead | rollback |

### 10.2 门规则

GR-1 检查清单；GR-2 校验流程；GR-3 失败回退；GR-4 不过门不交付；GR-5 一票否决；GR-6 连续 3 次失败触发 H4；GR-7 grill-me 输出作为 G7/G8 补充输入；GR-8 differential_findings 作为 G7/G8 补充输入；GR-9 G5/G9 检查 AGPL-3.0 与来源声明；GR-10 协同输出仅作补充输入、无否决权；GR-11 G11 拦截突破核心边界的适配。

### 10.3 门禁执行算法

```
输入：artifact, differential_findings, ecosystem_outputs
1. 识别 artifact 类型
2. 确定必经门
3. 逐门执行
4. 每门：跑校验、跑清单、收集否决意见
5. G7/G8 附加读取 grill-me 输出、协同输出与 differential_findings
6. G5/G9 附加读取许可声明与来源声明
7. G11 附加校验学习适配合规性
8. 若否决 → 记录 + 回退
9. 全过 → 下一阶段
```

---

## 11. 风格法（macOS Vibrancy）

### 11.1 适用范围

交付物 UI、结项报告、H 点简报、激活请求、审计包、门禁报告、文档、代码注释。

### 11.2 风格常量

三层深度色层；1px 边框；backdrop-blur；标题衬线、正文无衬线、代码等宽；无渐变、无发光、无装饰动画；过渡仅颜色 duration-200 ease-out；圆角最大 rounded-xl；强调色 #0a84ff 仅文字与焦点；默认 light。

### 11.3 亮色 Token

`#e8e8ed`、`#f5f5f7`、`#ffffff`、`#000000`、`#0a84ff`。

### 11.4 暗色 Token

`#1c1c1e`、`#2c2c2e`、`#3a3a3c`、`#ffffff`、`#000000`、`#0a84ff`。

### 11.5 组件契约

按钮 / 卡片 / 输入框 / 侧边栏，见 `references/style.md` 第 3 节。

### 11.6 禁止项

F-1..F-13（渐变、发光、重阴影、动画、超大圆角、全圆角、强调色背景、粗边框、渐变文字、单侧粗边框、tiny uppercase eyebrow、嵌套卡片、彩色背景灰字）。

### 11.7 禁止 class 模式

`^bg-gradient`、`^shadow-(xl|2xl|lg)$`、`^rounded-(3xl|full)$`、`^animate-`、`^border-[2-9]$`、`^text-(yellow|pink|green|purple)-[0-9]+$`。

### 11.8 必须模式

button: rounded-lg / transition-colors / duration-200；card: border / rounded-xl；input: border / rounded-lg / focus:border- / placeholder-；theme: 三层深度 / 1px 边框 / 衬线标题 / 无衬线正文 / 等宽代码 / 无渐变 / 无发光。

### 11.9 风格治理

SG-1 Style Warden 一票否决；SG-2 每轮 VERIFY 跑 `style_lint.py`；SG-3 漂移则停止、回滚、重做；SG-4 主题切换显式；SG-5 寻差个人专责漂移检测。

---

## 12. 表达约束

E-1 不出现辅助生成类标签；E-2 自动生成类标签；E-3 辅助生成类署名；E-4 自动生成类署名；E-5 辅助生成类声明；E-6 自动生成类声明；E-7 不出现暗示生成类字眼；E-8 不出现"虚拟"字样；E-9 使用中性、专业表述。检查点在 G9 交付门（`style_lint.py --expression`）。验收：表达约束 0 违规（A-22）。

---

## 13. 持久化

### 13.1 文件

`run_state/state/`、`run_state/events/events.jsonl`、`run_state/checkpoints/`。

### 13.2 run.json 结构

见 `assets/run.template.json`：run_id、active、phase、theme、style、license、contract、integration、ecosystem、learning、staffing、created_at、updated_at、hash、brand。

### 13.3 activation.json 结构

`state`、`prompted_at`、`user_reply`、`explicit_command`、`resolved_at`。

### 13.4 individuals.json 结构

`assignments[]`：microtask_id、function、individual、artifact_id、status、ignore_reason。

### 13.5 differential.json 结构

`findings[]`：finding_id、finder、function、type、severity、description、evidence、recommendation、status、ignore_reason。

### 13.6 profile.json 结构

`version`、`created_at`、`updated_at`、`preferences{}`、`adaptations[]`、`blacklist[]`。详细语义见 `references/learning.md`。

### 13.7 检查点策略

激活变更、MicroTask 完成、Gate 通过、H 点恢复、联动变更、协同池变更、个人分配变更、寻差变更、画像更新 → checkpoint；每 5 轮 TURN → heartbeat。

### 13.8 恢复流程

读 run.json → 不存在读最近 checkpoint → 校验 hash → 校验契约/风格/联动/协同/激活/分配/寻差/画像/许可 → 恢复上下文 → RUNNING。

---

## 14. 通用约束（U-1..U-16）

U-1 冷静精确克制；U-2 无感叹号/表情/口语；U-3 无空洞形容词；U-4 无标签署名声明暗示；U-5 无禁用词；U-6 结论先于依据先于风险；U-7 断言标注来源与置信度；U-8 产物标注 owner/版本/验收；U-9 不直接对用户发言（CCO 除外）；U-10 不审批自己的工作；U-11 不越界访问；U-12 只通过 Artifact 交接；U-13 不因进度压力放行；U-14 冲突升级；U-15 不可裁决升级 H4；U-16 遵守 AGPL-3.0。

## 15. 个人通用约束（IP-1..IP-10）

IP-1 单产物单责任；IP-2 结论先行；IP-3 证据标注；IP-4 不越界；IP-5 只经 Artifact 交接；IP-6 遵守表达约束；IP-7 冲突上报；IP-8 不自我审批；IP-9 版本与验收标注；IP-10 许可声明保留。详见 `references/individuals.md`。

---

## 16. 持续规则（P-1..P-12）

P-1 输入转工单；P-2 不直接回答；P-3 不绕门禁；P-4 不违风格法；P-5 不跳审计；P-6 不自我审批；P-7 H 点暂停；P-8 执行联动机制；P-9 执行职能/角色/个人调度；P-10 保留 AGPL-3.0 声明；P-11 协同按生态协议执行；P-12 交付按 7.4 路由。

---

## 17. 许可合规（LS-1..LS-5）

LS-1 以 AGPL-3.0 分发；LS-2 保留版权与许可声明；LS-3 修改以同协议发布；LS-4 网络服务提供完整源代码；LS-5 分发时提供源代码。

---

## 18. 错误码与校验规则

| 编号 | 规则 |
| --- | --- |
| PERM-1 | 未知动作 |
| PERM-2 | 越权：角色无该动作权限 |
| PERM-3 | 自我审批 |
| CT-0..CT-7 | 契约缺失/类型错误/主题非法 |
| RUN-1..RUN-5 | run 字段缺失/hash 失败/未知 phase/未知主题/许可异常 |

---

## 19. 风险登记

| 编号 | 风险 | 缓解 |
| --- | --- | --- |
| R-6 | 表达违规 | G9 检查 |
| R-16 | 违规即回退 | 回退重做 |
| R-32 | 格式转换失败 | 回退默认格式（D-3） |

---

## 20. 验收标准

### 20.1 激活与生命周期（A-1..A-6）

A-1 第一轮激活请求；A-2 请求仅一次；A-3 activate 进入 BOOTSTRAP；A-4 decline 不再提示且可显式重新激活；A-5 其他文本按 decline；A-6 显式命令激活。

### 21. 全量验收清单

| 编号 | 验收 |
| --- | --- |
| A-1..A-6 | 激活与生命周期（见 20.1） |
| A-7..A-14 | 分解、执行、门禁、风格（见 `evals/`） |
| A-18 | 终止输出结项/审计/释放锁 |
| A-20 | 不自我审批 |
| A-21 | 事件日志 append-only |
| A-22 | 表达约束 0 违规 |

完整用例见 `evals/` 下 10 组文件。

---

## 22. 术语表

| 术语 | 定义 |
| --- | --- |
| CCF | Cognitivecomputing_firm，本技能 |
| 弈策集团 / Yestest Holdings Limited | 内部公司设定，组织载体 |
| Ticket | 由用户输入登记的工作单 |
| MicroTask | 单目标单产物单责任单验收的最小执行单元 |
| Gate | 质量门，G0–G11 |
| H 点 | 人工决策点，H1–H4 |
| Differential | 寻差，专职寻找差异/边界/反例/替代 |
| 协同池 | 参与自动调用的 Skill 集合 |

---

## 23. 附录

### 23.3 表达约束原文

```
所有产物、文档、界面文案、代码注释：
不出现辅助生成类、自动生成类、暗示生成类标签、署名或声明。
不出现"虚拟"字样。
使用中性、专业表述。
```

### 23.1 品牌与标识

见 `references/brand.md`：名称释义、专业性宪章（PF-1..PF-4）、标识使用规范（LG-1..LG-6）与标识覆盖清单（11 处）。

### 23.2 执行层接线

见 `references/runbook.md`：脚本调用清单与状态文件读写顺序。

---

YESTEST // PRD // V1.4 // G0
