# style-tokens.md

**路径**：`references/style-tokens.md`（加载时机：按需，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 说明

本文件为 macOS Vibrancy 风格法的亮色与暗色 Token 字典，逐行对应 PRD 11.3 与 11.4 两表。
默认主题为亮色（light），暗色（dark）为备选主题。切换命令：`/ccf theme light`、`/ccf theme dark`。

## 2. 亮色 Token

| 类别 | Token 值 |
| --- | --- |
| L1 sidebar | bg-[#e8e8ed]/80 backdrop-blur-xl |
| L2 panel | bg-[#f5f5f7] |
| L3 card | bg-white |
| border | border-black/8 至 border-black/12 |
| radius | rounded-lg 至 rounded-xl |
| text-primary | text-black/95 |
| text-secondary | text-black/70 |
| text-muted | text-black/40 |
| accent | #0a84ff |
| transition | transition-colors duration-200 ease-out |

## 3. 暗色 Token

| 类别 | Token 值 |
| --- | --- |
| L1 sidebar | bg-[#1c1c1e]/80 backdrop-blur-xl |
| L2 panel | bg-[#2c2c2e] |
| L3 card | bg-[#3a3a3c] |
| border | border-white/8 至 border-white/12 |
| radius | rounded-lg 至 rounded-xl |
| text-primary | text-white/95 |
| text-secondary | text-white/70 |
| text-muted | text-white/40 |
| accent | #0a84ff |
| transition | transition-colors duration-200 ease-out |

## 4. 使用规则

- 色层：三层深度（sidebar 模糊层、panel 面板层、card 卡片层），L1 使用 backdrop-blur。
- 边框一律 1px；圆角限 rounded-lg 至 rounded-xl。
- 强调色 accent #0a84ff 仅用于文字与焦点，不作大面积背景（见 `references/style.md` F-7）。
- 过渡仅颜色：transition-colors duration-200 ease-out。

## 5. 相关文件

| 文件 | 内容 |
| --- | --- |
| style.md | 适用产物、组件契约、禁止项、自检清单 |
| gates.md | G6 风格门 |

---

YESTEST // style-tokens // V1.3 // G0