# Cognitivecomputing_firm（弈策集团 · Yestest Holdings Limited）

CCF（Cognitivecomputing_firm）是一款驻留式公司运作 Skill：激活后，每次输入都会被登记为工单，按固定职能、角色、个人、流程、门禁与风格法执行，产出可审计、可回滚的结果。

## 特性

- 第一轮激活协议：会话首轮主动请求一次，用户确认后持续运行；亦支持显式命令（`/ccf start`、`/yestest start`）。
- 公司化组织：12 个职能（CCO、COO、PMO、Analyst、Architect、Specialist、Red Team、Style Warden、QA、Integrator、Learning、Archivist），每职能多个人并行产出，由职能负责人合并。
- 寻差机制：Analyst/Architect/Specialist/Red Team/Style Warden/QA/Archivist 均设专职寻差个人，产出供 G7/G8 门禁消费。
- 全流程门禁：G0–G11 十二道质量门，含否决与回退；H1–H4 人工决策点。
- 风格法：macOS Vibrancy 亮色默认、暗色备选；1px 边框、accent #0a84ff、无渐变无发光无装饰动画。
- 表达约束：所有产物不带任何标签、署名或暗示性字样。
- 微任务体系：任务逐层细化为单目标、单产物、单责任人、单验收的 MicroTask。
- 外部协同：与 grill-me 官方联动；多 Skill 生态扫描、分级推荐、统一调用协议，失败降级不阻塞主流程。
- 自适配：基于运行数据迭代用户画像（D0–D4 分级应用），核心规则置于黑名单不可自动修改。
- 交付路由：按产物类型自动匹配交付管线（文档默认 PDF，Word 需显式请求）。
- 许可合规：AGPL-3.0 分发，来源与许可声明全程保留。

## 首次使用（从 GitHub 到本地运行）

### 前置依赖

| 依赖 | 用途 | 要求 |
| --- | --- | --- |
| Python 3.10+ | 运行 `scripts/` 下状态/门禁/风格/协同/适配等 11 个脚本 | 命令行可输入 `python` 即可 |
| Git | 拉取与后续更新 | 可选，ZIP 方式无需安装 |

### 拉取到本地

任选其一：

**方式 A：Git Clone**（推荐，方便后续更新）

```bash
git clone https://github.com/Boryac/Cognitivecomputing_firm.git
```

**方式 B：下载 ZIP**（无需 Git）

在仓库页面点击 `Code → Download ZIP`，解压后得到 `Cognitivecomputing_firm/` 文件夹。

### 放置到 Skill 目录

将整个 `Cognitivecomputing_firm/` 文件夹复制到当前计算机的 Skill 根目录：

```
%USERPROFILE%\.meituan-catpaw\<user_id>\skills\
```

放置完成后，该目录下应直接存在 `SKILL.md`、`manifest.yaml`、`references/`、`scripts/`、`assets/`、`evals/`。

### 验证可运行性

进入 `scripts/` 目录，确认脚本可解析：

```bash
python -m py_compile *.py && echo OK
```

### 在 CatPaw 中启动

新建会话，首轮将收到如下格式的激活请求：

```
YESTEST // ACTIVATION // REQUEST
弈策集团（Cognitivecomputing_firm）可激活。
回复：
  activate  — 激活
  decline   — 不激活
```

回复 `activate` 后即进入 CCF 协议，每次输入都按工单处理。

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

已用 Git Clone 拉取时：

```bash
cd Cognitivecomputing_firm
git pull
```

已用 ZIP 安装时：重新下载 ZIP 并整体替换 `Cognitivecomputing_firm/` 文件夹即可。

> 注意：`run_state/`、`events/`、`checkpoints/` 为首次运行后生成的会话产物（已在 `.gitignore` 中忽略），更新时不会被覆盖。

## 目录结构

```
Cognitivecomputing_firm/
├── SKILL.md            入口：激活协议、运行时、风格法、表达约束
├── manifest.yaml       清单：命令、聚合、许可、品牌
├── LICENSE / COPYING / NOTICE / AUTHORS / CHANGELOG.md
├── references/         17 份规则（宪章、组织、门禁、风格、交付、学习…）
├── scripts/            11 个可执行逻辑（状态、路由、门禁、风格检查、协同…）
├── assets/             9 份数据契约模板
└── evals/              10 组、111 个验收用例
```

## 文档索引

| 文件 | 内容 |
| --- | --- |
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

YESTEST // README // V1.3.1 // G0