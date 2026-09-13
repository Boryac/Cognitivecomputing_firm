# Changelog

All notable changes to cognitivecomputing-firm (CCF) are documented in
this file. Format follows Keep a Changelog conventions.

## [1.4.0] - 2026-09-13

品牌标识在包内多处登记：SKILL.md、manifest.yaml、README.md、PRD.md、
references/brand.md、references/charter.md、assets 四份模板、CHANGELOG.md。

### Added

- `PRD.md`：产品需求规格，覆盖 references/scripts/evals 引用的全部章节号
  （3.3、4、4.5、5、6.5、6.21–6.24、7.4、9.1、10、11、12、13、15、20.1、
  21、23.3）与全部代码项（A-、R-、DD-、F-、SG-、SW-、U-、IP-、E-、LS-、
  PERM-、CT-、RUN-、GR-、P-、D-、L-）。
- `references/brand.md`：名称释义、品牌定位、专业性宪章（PF-1..PF-4）、
  标识使用规范（LG-1..LG-6）与标识覆盖清单（11 处）。
- `references/runbook.md`：执行层接线手册，把 BOOTSTRAP/TURN/TERMINATE
  映射到 11 个脚本的具体命令与 `run_state/` 状态文件读写顺序。
- `platform/`：平台适配层——Claude Code（`.claude/commands/ccf.md`）、
  WorkBuddy（`workbuddy.md` + SessionStart hook）、Codex（`codex.md`），
  以及 `ccf_sessionstart.py` 首轮提示 hook。
- 真实协同调用：`skill_orchestrator.py` 与 `integration_probe.py` 支持
  子进程真实执行（`--invoke-cmd`）或 outbox 回执派发，不再伪造成功。

### Changed

- 技能标识与目录更名为 `cognitivecomputing-firm`，符合 Agent Skills 规范
  （name 仅小写字母/数字/连字符，须匹配目录名）。
- `SKILL.md` frontmatter 重写：description 改为触发短语（含 Use when 语义），
  补 version / compatibility / allowed-tools / metadata；正文新增「Runtime 脚本
  接线协议」与公司概览章节。
- `manifest.yaml`：name 同步、version 1.4.0、brand 增加 etymology 与 coverage、
  新增 platform 段、integration/ecosystem 标注 real_call。
- README 全量重写：品牌页眉、平台技能目录表、平台适配说明、目录结构与文档索引。
- `.gitignore` 与 `references/persistence.md` 状态目录命名对齐为 `run_state/`。
- 版本号统一为 1.4.0（manifest / README / PRD / CHANGELOG）。

## [1.3.2] - 2026-09-13

### Added

- README 新增"首次使用（从 GitHub 到本地运行）"章节：Python 与 Git
  前置依赖、Git Clone 与 ZIP 两种拉取方式、Skill 目录放置、脚本编译
  验证、激活流程示例、常用命令表、后续更新方式。

### Changed

- README V1.3.1。

## [1.3.1] - 2026-09-13

### Added

- Brand asset: 透明底无字logo.png (611x611, transparent background,
  no-text glyph, hub-and-spoke node mark) added to package root and
  registered in manifest `brand.logo`.
- Brand metadata in manifest.yaml: brand name 弈策集团, legal name
  Yestest Holdings Limited, logo usage rules.
- charter.md section 1.1 "公司概览": etymology of 弈/策/Yestest
  (Yes + Test, confirm-then-verify), brand positioning table,
  organization positioning (Board = user, CCO = single interface).

### Changed

- SKILL.md Runtime section: internal company line expanded to
  弈策集团 (Yestest Holdings Limited) with brand logo reference.
- manifest.yaml version bumped to 1.3.1.

## [1.3.0] - 2026-09-13

### Added

- CCF::DELIVER delivery routing: artifact type classification at SCOPE,
  type-to-pipeline mapping (document/spreadsheet/presentation/code/
  image/data/video-audio/app/mixed/other), document pipeline with H3
  format confirmation (approve / approve+word / revise / reject),
  conversion-failure fallback to default format.
- Multi-skill ecosystem: BOOTSTRAP stage-1 full scan and per-TURN
  incremental probe, capability matching with graded recommendations
  (mandatory / recommended / on-demand / disabled), license
  compatibility check, unified CCF::ECOSYSTEM_CALL protocol, pool
  management with 3-consecutive-failure auto-removal, and user
  commands (`/ccf skills scan|list|enable|disable|auto on/off`).
- Self-adapting learning: runtime data collection, profile versioning
  (P-1, P-2, ...), decision-level adaptation (D0-D4), core-rule
  blacklist enforcement through gate G11, rollback and reset commands.
- Differential discovery: dedicated differential individuals across
  Analyst, Architect, Specialist, Red Team, Style Warden, QA and
  Archivist; findings recorded in differential.json and consumed by
  gates G7/G8; ignore reason always recorded.
- Full packaging: LICENSE (AGPL-3.0 full text), COPYING, NOTICE,
  AUTHORS, CHANGELOG.md, references/, scripts/, assets/, evals/.

### Changed

- Integration rules for grill-me extended to the ecosystem protocol;
  grill-me remains the only mandatory-level integration and keeps its
  independent license.

## [1.2.0] - 2026-09-01

### Added

- grill-me integration state machine: probe, prompt-once-per-run,
  install command display, done/failed/skip handling, single reprobe,
  decline/later handling, disable command, integration.json.
- Organization model: 12 functions, lead + individuals per function,
  permission matrix, escalation paths, individual scheduling rules.
- Gate set G0-G11 with veto owners and gate execution algorithm.

## [1.1.0] - 2026-08-20

### Added

- CCF::BOOTSTRAP phases 0-7 and CCF::TURN steps with failure handling.
- Persistence scheme A/B/C/D with state, events, checkpoints, and
  recovery flow.
- Style law (macOS Vibrancy, light default, dark alternate) and
  expression constraint with forbidden / required patterns.

## [1.0.0] - 2026-08-01

### Added

- Initial release: SKILL.md entry, first-turn activation protocol,
  explicit activation commands, run contract, Ticket state machine,
  microtask decomposition, human gates H1-H4, AGPL-3.0 licensing.

---

YESTEST // CHANGELOG // V1.3 // G0