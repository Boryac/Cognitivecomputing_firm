# 弈策集团（Yestest Holdings Limited）· CCF

![弈策集团标识](透明底无字logo.png)

**cognitivecomputing-firm**（CCF）是一款公司化多角色工作流技能：激活后，每次输入都会被登记为工单，按固定职能、角色、个人、流程、门禁与风格法执行，产出可审计、可回滚的结果。

> `Yestest = Yes + Test`——凡确认必先检验；未经验证的确认不成立。此为该组织全部门禁与审计机制的文化根因。

## 特性

- **第一轮激活协议**：会话首轮主动请求一次，用户确认后持续运行；亦支持显式命令（`/ccf start`、`/yestest start`、`调用弈策集团`）。因宿主平台不允许技能在首轮自行运行，该行为由平台适配层落地（Claude Code SessionStart hook / WorkBuddy SessionStart hook / Codex AGENTS.md）。
- **公司化组织**：12 个职能（CCO、COO、PMO、Analyst、Architect、Specialist、Red Team、Style Warden、QA、Integrator、Learning、Archivist），每职能多个人并行产出，由职能负责人合并。
- **寻差机制**：Analyst/Architect/Specialist/Red Team/Style Warden/QA/Archivist 均设专职寻差个人，产出供 G7/G8 门禁消费。
- **全流程门禁**：G0–G11 十二道质量门，含否决与回退；H1–H4 人工决策点。
- **风格法**：macOS Vibrancy 亮色默认、暗色备选；1px 边框、accent #0a84ff、无渐变无发光无装饰动画。
- **表达约束**：所有产物不带任何标签、署名或暗示性字样。
- **微任务体系**：任务逐层细化为单目标、单产物、单责任人、单验收的 MicroTask。
- **外部协同（真实调用）**：与 grill-me 官方联动；多 Skill 生态扫描、分级推荐、统一调用协议，调用为真实执行（子进程或 outbox 回执），失败降级不阻塞主流程。
- **自适配**：基于运行数据迭代用户画像（D0–D4 分级应用），核心规则置于黑名单不可自动修改。
- **交付路由**：按产物类型自动匹配交付管线（文档默认 PDF，Word 需显式请求）。
- **执行层脚本化**：11 个 Python 脚本承载状态、路由、门禁、风格、协同、交付与适配，接线协议见 `references/runbook.md`。
- **许可合规**：AGPL-3.0 分发，来源与许可声明全程保留。

## 首次使用（从 GitHub 到本地运行）

### 前置依赖

| 依赖 | 用途 | 要求 |
| --- | --- | --- |
| Python 3.10+ | 运行 `scripts/` 下 11 个脚本 | 命令行可输入 `python3` 即可 |
| Git | 拉取与后续更新 | 可选，ZIP 方式无需安装 |

### 拉取到本地

**方式 A：Git Clone**（推荐）

```bash
git clone https://github.com/Boryac/cognitivecomputing-firm.git
```

**方式 B：下载 ZIP**：仓库页面 `Code → Download ZIP`，解压得到 `cognitivecomputing-firm/`。

### 放置到 Skill 目录

将整个 `cognitivecomputing-firm/` 文件夹复制到宿主平台的 Skill 根目录：

| 平台 | 技能目录 |
| --- | --- |
| Claude Code | `~/.claude/skills/cognitivecomputing-firm/` 或 `<项目>/.claude/skills/cognitivecomputing-firm/` |
| WorkBuddy | `~/.workbuddy/skills/cognitivecomputing-firm/` 或 `<项目>/.workbuddy/skills/cognitivecomputing-firm/` |
| Codex | `~/.codex/skills/cognitivecomputing-firm/` |

放置后该目录下应直接存在 `SKILL.md`、`PRD.md`、`manifest.yaml`、`references/`、`scripts/`、`assets/`、`evals/`、`platform/`。

### 首轮提示与斜杠命令（平台适配）

技能包自身不含平台配置；按需安装适配文件，见 `platform/README.md`：

- Claude Code：复制 `.claude/commands/ccf.md` 到 `~/.claude/commands/`；可选在 `settings.json` 配置 `SessionStart` hook 指向 `platform/ccf_sessionstart.py`。
- WorkBuddy：见 `platform/workbuddy.md`。
- Codex：见 `platform/codex.md`。

零配置入口：`调用弈策集团` / `调用 cognitivecomputing-firm` / `调用 CCF`。

### 验证可运行性

```bash
python3 -m py_compile scripts/*.py && echo OK
```

### 常用命令

| 场景 | 命令 |
| --- | --- |
| 显式激活 | `/ccf start` / `/yestest start` / `调用弈策集团` |
| 切换亮色主题 | `/ccf theme light` |
| 切换暗色主题 | `/ccf theme dark` |
| 查看已安装协同 Skill | `/ccf skills list` |
| 查看当前用户画像 | `/ccf profile` |
| 终止并生成审计包 | `/ccf stop` |

### 后续更新

```bash
cd cognitivecomputing-firm && git pull
```

> 注意：`run_state/` 为首次运行后生成的会话产物（已在 `.gitignore` 中忽略），更新时不会被覆盖。

## 目录结构

```
cognitivecomputing-firm/
├── SKILL.md            入口：激活协议、运行时脚本接线、风格法、表达约束
├── PRD.md              产品需求规格（唯一规格来源）
├── manifest.yaml       清单：品牌、命令、聚合、许可
├── LICENSE / COPYING / NOTICE / AUTHORS / CHANGELOG.md
├── 透明底无字logo.png   品牌标识
├── references/         19 份规则（含 brand.md 品牌、runbook.md 接线手册）
├── scripts/            11 个可执行脚本（状态/路由/门禁/风格/协同/交付/适配）
├── assets/             9 份数据契约模板
├── evals/              10 组验收用例
├── platform/           平台适配（Claude Code / WorkBuddy / Codex）
└── .claude/commands/   Claude Code 斜杠命令
```

## 文档索引

| 文件 | 内容 |
| --- | --- |
| `PRD.md` | 产品需求规格（全部章节号与代码项的权威定义） |
| `references/brand.md` | 品牌定位、名称释义、专业性宪章、标识使用规范 |
| `references/runbook.md` | 脚本接线手册（调用清单、状态文件顺序、平台落地） |
| `references/charter.md` | 宪章、六不原则、约束优先级、通用约束 |
| `references/workflow.md` | 激活、BOOTSTRAP、TURN、TERMINATE |
| `references/org.md` / `roles.md` / `individuals.md` | 组织架构、职能契约、个人清单 |
| `references/microtask.md` | 微任务体系与拆分算法 |
| `references/gates.md` | G0–G11 质量门与执行算法 |
| `references/style.md` / `style-tokens.md` | macOS Vibrancy 风格法与 token 字典 |
| `references/expression.md` | 表达约束 E-1..E-9 |
| `references/persistence.md` | 状态、事件、检查点与恢复 |
| `references/integration-grill-me.md` | grill-me 联动状态机 |
| `references/ecosystem.md` | 多 Skill 协同协议 |
| `references/delivery.md` | 交付路由与管线 |
| `references/learning.md` | 自适配与画像版本管理 |
| `references/differential.md` | 寻差机制 |
| `references/license.md` | AGPL-3.0 合规细则 |

## 许可

GNU Affero General Public License v3.0。全文见 [LICENSE](LICENSE)。按 AGPL-3.0 要求，以网络方式对外提供本 Skill 服务时，必须提供对应完整源代码。

---

YESTEST // README // V1.4.0 // G0
