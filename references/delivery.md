# delivery.md

**路径**：`references/delivery.md`（加载时机：INTEGRATE 阶段，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 交付分类与路由

交付物在 SCOPE 阶段标注类型，按类型自动匹配交付管线：

| 产物类型 | 默认交付格式 | 可选格式 | 交付管线 |
| --- | --- | --- | --- |
| 文档类 | PDF | MD、Word、LaTeX | MD 源稿 → 用户确认 → LaTeX 排版 → PDF 交付 |
| 表格类 | Excel | CSV、PDF | 数据结构 → 表格生成 → Excel 交付 |
| 演示类 | PDF | PPTX、MD | 大纲 → 幻灯片生成 → PDF 交付 |
| 代码类 | 源码包 | 可执行文件 | 源码 → 构建校验 → 源码包交付 |
| 图片类 | PNG | SVG、JPG、PDF | 源文件 → 导出校验 → PNG 交付 |
| 数据类 | JSON | CSV、Excel | 数据集 → 格式封装 → JSON 交付 |
| 视频/音频类 | 源文件 | 压缩格式 | 素材 → 封装校验 → 源文件交付 |
| 应用/服务类 | 部署包 | 镜像 | 构建产物 → 部署包交付 |
| 混合类 | 压缩包 | 分文件 | 各产物按对应管线 → 打包交付 |
| 其他 | 默认格式 | 按需转换 | 按契约约定执行 |

## 2. 文档类交付管线

1. Specialist 输出 MD 源稿（权威内容源）
2. G6、G7、G8 门禁校验通过
3. 进入交付确认（H3 节点），格式：

```
YESTEST // DELIVERY // CONFIRM // DOC
事项：文档交付格式确认
背景：内容已通过全部门禁
选项：
  A. approve — 确认交付 PDF
  B. approve+word — 同时交付 PDF + Word
  C. revise — 返回修改内容
  D. reject — 驳回
建议：默认交付 PDF
风险：Word 格式可能存在排版差异
影响：选择 Word 将增加格式转换环节
回复：approve / approve+word / revise / reject
```

4. 用户确认后执行格式转换
   - approve：LaTeX 排版 → 输出 PDF
   - approve+word：LaTeX 排版 → PDF + 转换 Word
   - revise：回退到 Specialist 环节修改
   - reject：回退到 SCOPE 阶段
5. G9 交付门最终校验后输出

## 3. 通用交付规则

| 编号 | 规则 |
| --- | --- |
| D-1 | 未明确指定格式时，按该类型默认格式交付 |
| D-2 | 格式转换类协同 Skill 优先于内置转换能力调用 |
| D-3 | 格式转换失败时，回退到默认格式交付，不阻塞主流程 |
| D-4 | 所有交付物必须保留许可声明与来源标注 |
| D-5 | 交付物类型识别有歧义时，先询问用户，不猜测 |

## 4. delivery 结构

结构与 `assets/delivery.template.yaml` 一致：

```
delivery_id: DL-001
run_id: CCF-YYYY-MM-DD-NNN
ticket_id: T-001
artifact_ids: []

artifact_type: "document | spreadsheet | presentation | code | image | data | video_audio | app_service | mixed | other"
default_format: "pdf | excel | pdf | source | png | json | source | deploy | archive | default"
selected_format: ""
pipeline: ""

# 文档管线：md → 用户确认(H3) → latex → pdf；Word 需显式请求
document_pipeline:
  source_ref: ""
  confirm: "approve | approve+word | revise | reject"
  confirm_at: "ISO8601 | null"
  latex_ref: ""
  pdf_ref: ""
  word_ref: ""

format_conversion:
  used_skill: ""
  status: "ok | failed | fallback"
  fallback_to: ""
  note: ""

license_notice: "AGPL-3.0 — 见 LICENSE；来源与许可声明保留"
delivered_at: "ISO8601 | null"
version: 1
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| delivery_id | 交付记录编号，格式 DL-001 |
| artifact_type | 产物类型（SCOPE 阶段标注） |
| default_format / selected_format | 默认格式与最终选定格式 |
| pipeline | 匹配的交付管线 |
| document_pipeline | 文档管线各环节引用与确认记录 |
| format_conversion | 格式转换记录：使用的协同 Skill、状态、回退目标 |
| license_notice | 许可与来源声明保留 |
| delivered_at | 交付时间 |

## 5. 相关文件

| 文件 | 内容 |
| --- | --- |
| workflow.md | DELIVER 步骤与 H3 节点 |
| gates.md | G6、G7、G8、G9 门禁 |
| ecosystem.md | 格式转换类协同 Skill 调用（D-2） |
| license.md | 交付物许可声明（D-4） |

---

YESTEST // delivery // V1.3 // G0