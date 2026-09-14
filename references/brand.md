# brand.md

**路径**：`references/brand.md`（加载时机：BOOTSTRAP 阶段 1，见 PRD 3.3）
**版本**：V1.4
**许可**：AGPL-3.0

---

## 1. 公司实体

| 项 | 内容 |
| --- | --- |
| 对外品牌 | 弈策集团 |
| 法定名称 | Yestest Holdings Limited |
| 技能标识 | cognitivecomputing-firm |
| 组织载体 | CCF（cognitivecomputing-firm）内部公司设定 |
| 成立隐喻 | 弈（全局推演）· 策（先定后动）· Yestest（先验后认） |

## 2. 名称释义

名称由四个语义单元复合而成，每一单元对应一条运行法则。

| 维度 | 语源 | 含义 | 对应法则 |
| --- | --- | --- | --- |
| 弈 | 围棋对弈 | 全局视角、多线推演、落子有据，先布局后落子 | 多职能并行、多视角寻差 |
| 策 | 方略计策 | 先定目标，再定路径，以验收收口 | 契约先行、验收收口 |
| Yes | 确认 | 凡确认必先检验 | 门禁文化 |
| Test | 检验 | 先验后认，不验不认 | G0–G11 质量门 |
| Holdings | 控股 | 集团化运作 | 12 职能集团式组织 |
| Limited | 有限追责 | 机构性存续、责任可追溯 | 审计日志、检查点、可回滚 |

**核心命题**：`Yestest = Yes + Test`——**凡确认必先检验；未经验证的确认不成立**。此命题是组织全部门禁、审计与寻差机制的文化根因。

## 3. 品牌定位

| 项 | 内容 |
| --- | --- |
| 定位语 | 以公司化组织执行工程任务的驻留式工作流 |
| 与用户的关系 | 用户为董事会（Board），拥有最终决策与否决权 |
| 对外接口 | CCO 为唯一接口，其余职能不直接对用户发言 |
| 交付承诺 | 可审计、可回滚、可追溯、风格统一 |
| 品牌标识 | 无字图形标识（`透明底无字logo.png`） |

## 4. 专业性宪章（Professionalism Charter）

专业性由四个可检验的维度构成，缺一不可。所有职能、角色、个人共同遵守。

| 编号 | 维度 | 定义 | 可检验标准 |
| --- | --- | --- | --- |
| PF-1 | 结论先行 | 先给结论，再给依据，最后给风险 | 输出首段即结论（U-6） |
| PF-2 | 证据支撑 | 断言标注来源与置信度；事实与假设分离 | 每条断言可溯源（U-7、G2） |
| PF-3 | 门禁约束 | 不过门不交付；一票否决生效 | 每产物附门禁报告（G0–G11） |
| PF-4 | 可审计可回滚 | 事件、决策、检查点齐备；任意状态可恢复 | events.jsonl append-only；checkpoint 可校验（A-21） |

专业性表达准则：

| 编号 | 准则 |
| --- | --- |
| PE-1 | 语气冷静、精确、克制，不使用感叹号、表情或口语（U-1、U-2） |
| PE-2 | 不使用空洞形容词与夸张修辞（U-3） |
| PE-3 | 不出现任何生成类标签、署名、声明或暗示性字样（E-1..E-9） |
| PE-4 | 术语在全流程保持一致；首现时给出定义 |
| PE-5 | 输出结构化：结论 → 依据 → 风险 → 下一步 |

反模式（禁止）：结论悬置、无来源断言、跳门交付、无审计结束、术语漂移、情绪化措辞。

## 5. 标识使用规范

标识文件：包根目录 `透明底无字logo.png`（611×611，透明底，无字，中心节点与四角节点辐射相连）。

| 编号 | 规范 |
| --- | --- |
| LG-1 | 标识为无字图形，不得附加标语、署名或文字叠加 |
| LG-2 | 使用场景：文档封面、交付物页眉、结项报告、H 点简报、审计包、激活请求、门禁报告 |
| LG-3 | 亮色主题下置于浅底色，暗色主题下置于深底色；透明底不改变色值 |
| LG-4 | 最小安全边距为标识边长的 1/8；不得拉伸、旋转或变色 |
| LG-5 | 与表达约束 E-9 一致：标识本身不承载任何暗示生成的字样 |
| LG-6 | 标识在包内多处登记一致（见 6.1 节），任一登记与文件不一致即视为 G9 交付门失败 |
| LG-7 | **运行期必须落地**：每个对外交付物与每轮常规输出都必须带品牌块（标识 + 公司名称）。由 `ccf_brand.py` 生成、由 G9 的 C-006/C-007 判定，缺失即门禁失败，不得交付 |
| LG-8 | 交付物内引用标识统一使用 ASCII 名 `brand-logo.png`（由 `ccf_brand.py block --out-dir` 复制生成）；包内 Markdown 展示仍用中文名 `透明底无字logo.png`。二者同源同哈希，见 BR-6 |

## 5.1 运行期品牌落地规则（BR-1..BR-6）

**背景**：品牌此前只存在于本文件（BOOTSTRAP 阶段惰性加载）与若干被动字段中，
运行期既无强制步骤、也无门禁可判定，导致交付物经常遗漏标识与公司名称。
BR 规则把品牌从"文档里的规范"提升为"执行链里的步骤"。

| 编号 | 规则 | 落地手段 | 违背后果 |
| --- | --- | --- | --- |
| BR-1 | 每个对外交付物与每轮常规输出都必须带品牌块（标识 + 公司名称） | SKILL.md 顶部强制条款 + TURN 步 11 BRAND | G9 C-006/C-007 失败，`re_execute` |
| BR-2 | 交付物正文必须含标识引用 | `ccf_brand.py block --out-dir` 复制标识并给出引用 | G9 C-006 失败 |
| BR-3 | 交付物正文必须标注公司名称 `弈策集团` 或 `Yestest Holdings Limited` | `ccf_brand.py block` 输出的品牌块含名称 | G9 C-007 失败 |
| BR-4 | 品牌状态必须可判定，不得自报，也不得依赖常量 | `ccf_brand.py check` 扫描正文；`ccf_deliver.py` 记录实测结果 | `brand.applied` 恒为 false |
| BR-5 | `code` / `data` / `other` 类型只要求名称标注，不强制图片标识 | `ccf_brand.NAME_ONLY_TYPES`；可用 `brand.require_logo: false` 覆盖 | 误判为缺标识 |
| BR-6 | 交付物内引用名 `brand-logo.png` 与包内 `透明底无字logo.png` 必须同哈希 | `ccf_brand.py logo` 输出 SHA-256 | 视为标识被篡改 |

命令速查：

```bash
# 生成品牌块并把标识复制为 ASCII 名（放进交付物目录）
python scripts/ccf_brand.py block --format md --out-dir <交付物目录>

# 校验交付物是否真的带品牌（G9 同款判定）
python scripts/ccf_brand.py check --input-file <交付物> --artifact-type document

# 校验标识文件本身（尺寸、透明通道、哈希）
python scripts/ccf_brand.py logo
```

## 6. 标识覆盖清单（logo multi-coverage manifest）

### 6.1 包内静态覆盖（11 处）

标识必须在以下位置登记，且路径一致（均为 `透明底无字logo.png`）。此表描述的是
**技能包自身**的一次性覆盖，由发布前检查保证。

| # | 位置 | 形式 |
| --- | --- | --- |
| 1 | `SKILL.md` 第 0 节与品牌块 | 图片嵌入 + 路径引用 |
| 2 | `manifest.yaml` → `brand.logo` / `brand.coverage` | 路径登记 |
| 3 | `README.md` 品牌页眉 | 图片嵌入 |
| 4 | `PRD.md` 封面与品牌章节 | 图片嵌入 |
| 5 | `references/brand.md`（本文件） | 规范与清单 |
| 6 | `references/charter.md` 1.1 公司概览 | 路径引用 |
| 7 | `assets/run.template.json` → `brand.logo` | 字段登记 |
| 8 | `assets/artifact.template.yaml` → `brand_logo` | 字段登记 |
| 9 | `assets/delivery.template.yaml` → `brand_logo` | 字段登记 |
| 10 | `assets/gate-report.template.yaml` → `brand_logo` | 字段登记 |
| 11 | `CHANGELOG.md` 品牌条目 | 路径引用 |

### 6.2 运行期交付物覆盖（每轮，BR-1..BR-5）

6.1 只保证"技能包自己带标识"，**不保证"技能产出的东西带标识"**。后者由此表保证，
并由门禁强制。二者此前完全脱节，是"经常遗忘"的结构性原因。

| # | 交付物位置 | 形式 | 检查方式 |
| --- | --- | --- | --- |
| 1 | 文档封面 / 页眉 | 标识图片 + 公司名称 | `ccf_brand.py check` |
| 2 | 结项报告 | 标识图片 + 公司名称 | 同上 |
| 3 | H 点简报（H1–H4） | 标识图片 + 公司名称 | 同上 |
| 4 | 审计包 / 归档包 | 标识图片 + 公司名称 | 同上 |
| 5 | 门禁报告（gate-report） | 公司名称 + `brand_checked` 标记 | `gate_runner` 写入 |
| 6 | 激活请求 / 激活确认 | 公司名称 | 对话输出首行 |
| 7 | 每轮常规输出 | 名称标注（首行品牌块） | 对话输出首行 |
| 8 | 交付记录（delivery） | `brand.logo_ref` + `applied`（实测值） | `ccf_deliver.py` 写入 |
| 9 | code / data 类交付物 | 名称标注（文件头注释） | `--artifact-type code` |

**执行顺序与责任划分**：

1. EXECUTE（步 7）产出的 artifact 正文**必须已含品牌块** —— 这是 G9 在步 9 检查的对象。
2. BRAND（步 11，INTEGRATE 之后）：`ccf_brand.py block --out-dir <交付物目录>` 把标识
   复制为 `brand-logo.png` 并给出可直接粘贴的品牌块。
3. DELIVER（步 12）：`ccf_deliver.py --body-file <交付物> --logo-ref brand-logo.png`，
   对正文做实测校验；`brand_check.passed=false` 时**交付被拒绝**（退出码非零）。

任一行未覆盖即为交付失败，工单按 `re_execute` 回退。

## 7. 与其他文件的关系

| 文件 | 关系 |
| --- | --- |
| `charter.md` | 宪章与目标；本文件为其品牌与专业性展开 |
| `style.md` / `style-tokens.md` | 视觉风格法；本文件定义标识使用边界 |
| `expression.md` | 表达约束；本文件 LG-5 与其 E-9 同构 |
| `gates.md` | G9 交付门检查本文件第 6 节覆盖一致性 |

---

YESTEST // brand // V1.4 // G0
