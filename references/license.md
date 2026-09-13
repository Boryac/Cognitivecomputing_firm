# license.md

**路径**：`references/license.md`（加载时机：BOOTSTRAP 阶段 2，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 协议选择

本 Skill 采用 GNU Affero General Public License v3.0（AGPL-3.0）。

## 2. 许可要点

| 编号 | 要点 |
| --- | --- |
| L-1 | 允许自由使用、修改、分发 |
| L-2 | 分发或通过网络提供服务时必须提供源代码 |
| L-3 | 修改版本必须以相同协议发布 |
| L-4 | 必须保留版权与许可声明 |
| L-5 | 必须标注修改 |
| L-6 | 不提供担保 |

许可约束原文（PRD 23.4）：

```
本 Skill 以 AGPL-3.0 分发。
分发或提供网络服务时必须提供源代码。
修改必须以相同协议发布并标注。
必须保留版权与许可声明。
不提供担保。
```

## 3. 文件要求

分发版本必须包含：

| 文件 | 内容 |
| --- | --- |
| LICENSE | AGPL-3.0 全文 |
| COPYING | AGPL-3.0 副本说明 |
| NOTICE | 版权与第三方声明 |
| AUTHORS | 贡献者名单 |
| CHANGELOG.md | 版本变更记录 |

打包时校验 license_files（风险 R-22：分发版本缺少许可文件 → 打包时校验）。

## 4. 来源声明规则

所有产物、分发版本、网络服务端，必须包含：

| 编号 | 规则 |
| --- | --- |
| LS-1 | 保留版权声明 |
| LS-2 | 保留许可声明 |
| LS-3 | 标注修改 |
| LS-4 | 提供源代码获取方式 |
| LS-5 | 提供许可全文链接 |

## 5. 与 grill-me 及协同 Skill 的许可关系

| 项 | 说明 |
| --- | --- |
| grill-me 许可 | 由 grill-me 自身决定 |
| 协同 Skill 许可 | 由各 Skill 自身决定 |
| 本 Skill 许可 | AGPL-3.0 |
| 调用关系 | 通过接口调用，不构成合并 |
| 许可独立性 | 相互独立 |

## 6. 与第三方依赖的关系

| 依赖 | 处理 |
| --- | --- |
| 平台自身 | 遵循平台条款 |
| grill-me | 遵循其自身许可 |
| 协同 Skill | 遵循其自身许可 |
| 模板与样式 | 本 Skill 内定义，随本 Skill 许可 |
| 用户产物 | 归用户所有，按用户选择的许可处理 |

第三方依赖许可冲突时：独立许可声明，NOTICE 标注（风险 R-24）。

## 7. 商业使用

| 情形 | 允许 |
| --- | --- |
| 内部使用 | 是 |
| 分发 | 是，须遵守 AGPL-3.0 |
| 网络服务 | 是，须提供源代码 |
| 修改后分发 | 是，须以 AGPL-3.0 发布 |
| 闭源分发 | 否 |

用户将产物用于闭源分发时，以许可全文与提示明确禁止（风险 R-25）。

## 8. 许可相关事件

| 事件 | 触发 |
| --- | --- |
| LICENSE_LOADED | BOOTSTRAP 阶段 2 加载许可 |
| LICENSE_DECLARED | 产物包含许可声明 |
| LICENSE_VIOLATION | 检测到许可违规 |
| LICENSE_CHECK_PASSED | G5、G9 许可检查通过 |

## 9. 门禁与许可输出

- G5 合规门检查法律、政策、许可、协同许可兼容性；G9 交付门检查许可合规（PRD 10.1；GR-9）。
- 协同 Skill 许可兼容性校验见 `references/ecosystem.md` 第 6 节。
- 许可输出格式（`/ccf license`）：

```
YESTEST // LICENSE // AGPL-3.0
本 Skill 以 GNU Affero General Public License v3.0 分发。
许可全文：见 LICENSE 文件。
源代码获取：见 manifest.yaml 中 source_code 字段。
修改必须标注，并以相同协议发布。
网络服务必须提供源代码。
```

## 10. 合规义务汇总

| 义务 | 落实位置 |
| --- | --- |
| 分发版本包含许可文件 | LICENSE、COPYING、NOTICE、AUTHORS、CHANGELOG.md |
| 所有产物保留版权与许可声明 | 产物 license_notice 字段（如 `AGPL-3.0 — 见 LICENSE`） |
| 修改版本标注修改 | LS-3 |
| 网络服务提供源代码获取方式 | LS-4、`/ccf license` |
| G5、G9 许可合规检查 | GR-9、LICENSE_CHECK_PASSED |

按 AGPL-3.0 保留来源与许可声明为持续规则 P-10（`references/workflow.md`）。

## 11. 相关文件

| 文件 | 内容 |
| --- | --- |
| gates.md | G5、G9 许可检查 |
| ecosystem.md | 协同 Skill 许可兼容性校验 |
| integration-grill-me.md | grill-me 许可独立性 |
| delivery.md | 交付物许可声明（D-4） |

---

YESTEST // license // V1.3 // G0