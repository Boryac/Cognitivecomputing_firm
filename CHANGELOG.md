# Changelog

All notable changes to Cognitivecomputing_firm (CCF) are documented in
this file. Format follows Keep a Changelog conventions.

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