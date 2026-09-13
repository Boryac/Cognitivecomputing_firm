# style.md

**路径**：`references/style.md`（加载时机：BOOTSTRAP 阶段 4，见 PRD 3.3）
**版本**：V1.3
**许可**：AGPL-3.0

---

## 1. 适用范围

| 产物 | 是否适用 |
| --- | --- |
| 交付物 UI | 是 |
| 结项报告 | 是 |
| H 点简报 | 是 |
| 激活请求 | 是 |
| 审计包 | 是 |
| 门禁报告 | 是 |
| 文档 | 是 |
| 代码注释 | 是 |

## 2. 风格常量

| 项 | 值 |
| --- | --- |
| 色层 | 三层深度 |
| 边框 | 1px |
| 模糊 | backdrop-blur |
| 标题字体 | 衬线 |
| 正文字体 | 无衬线 |
| 代码字体 | 等宽 |
| 渐变 | 无 |
| 发光 | 无 |
| 装饰动画 | 无 |
| 过渡 | 仅颜色，duration-200 ease-out |
| 最大圆角 | rounded-xl |
| 强调色 | #0a84ff，仅文字与焦点 |
| 默认主题 | light |
| 备选主题 | dark |

亮色与暗色 Token 字典见 `references/style-tokens.md`。

## 3. 组件契约

**按钮**

```
<button class="bg-white text-black/90 border border-black/10 rounded-lg
               transition-colors duration-200 ease-out
               hover:bg-black/5 active:opacity-80">
```

**卡片**

```
<div class="bg-white border border-black/8 rounded-xl p-4 md:p-6">
```

**输入框**

```
<input class="bg-white border border-black/10 rounded-lg
              text-black/90 placeholder-black/30
              focus:outline-none focus:border-black/25
              transition-colors duration-200 ease-out" />
```

**侧边栏**

```
<aside class="bg-[#e8e8ed]/80 backdrop-blur-xl border-r border-black/8">
```

## 4. 禁止项

| 编号 | 禁止 | 替代 |
| --- | --- | --- |
| F-1 | 任何渐变 | 纯色 |
| F-2 | 发光效果 | 无 |
| F-3 | spread > 2px 阴影 | 1px 边框 |
| F-4 | pulse / bounce / spin | 无 |
| F-5 | rounded-3xl | rounded-lg / xl |
| F-6 | rounded-full | rounded-lg / xl |
| F-7 | 亮色强调色作背景 | 仅文字 / 焦点 |
| F-8 | 边框 > 1px | 1px |
| F-9 | 渐变文字 | 纯色 |
| F-10 | 单侧粗边框 | 无 |
| F-11 | tiny uppercase eyebrow | 无 |
| F-12 | 嵌套卡片 | 单层 |
| F-13 | 彩色背景灰字 | WCAG AA |

## 5. 禁止 Class 模式

```
^bg-gradient
^shadow-(xl|2xl|lg)$
^rounded-(3xl|full)$
^animate-
^border-[2-9]$
^text-(yellow|pink|green|purple)-[0-9]+$
```

## 6. 必须模式

```
button: rounded-lg, transition-colors, duration-200
card:   border, rounded-xl
input:  border, rounded-lg, focus:border-, placeholder-
theme:  three-depth-gray, 1px-borders, serif-headings,
        sans-body, mono-code, no-gradient, no-glow
```

## 7. 自检清单

| 编号 | 检查项 |
| --- | --- |
| C-1 | 无渐变 |
| C-2 | 阴影 spread ≤ 2px |
| C-3 | 全部 1px 边框 |
| C-4 | 三级深度色系统 |
| C-5 | 标题衬线、正文无衬线、代码等宽 |
| C-6 | 过渡仅颜色，duration-200 ease-out |
| C-7 | 无 rounded-3xl / rounded-full |
| C-8 | 无发光、无装饰动画 |
| C-9 | 强调色未作大面积背景 |
| C-10 | 无嵌套卡片 |
| C-11 | 无渐变文字 |
| C-12 | 无单侧粗边框 |
| C-13 | 无 tiny uppercase eyebrow |
| C-14 | 对比度 WCAG AA |
| C-15 | reduced-motion 支持 |
| C-16 | 响应式无横向溢出 |

## 8. 风格治理

| 编号 | 规则 |
| --- | --- |
| SG-1 | Style Warden Lead 一票否决 |
| SG-2 | 每轮 VERIFY 跑 style_lint |
| SG-3 | 漂移则停止、回滚、重做 |
| SG-4 | 主题切换显式，默认 light |
| SG-5 | Style Warden 的 differential 个人专责漂移检测 |

## 9. 执行说明

- G6 风格门依据本文件与 `references/style-tokens.md` 执行；否决方为 Style Warden Lead。
- 每轮 VERIFY 步骤运行 `scripts/style_lint.py`（SG-2），命中第 5 节禁止 class 模式即判违规。
- 主题切换命令：`/ccf theme light`、`/ccf theme dark`；默认亮色。
- 漂移处理按 SG-3：停止、回滚、重做。

## 10. 相关文件

| 文件 | 内容 |
| --- | --- |
| style-tokens.md | 亮色 / 暗色 Token 字典（11.3、11.4） |
| gates.md | G6 风格门 |
| roles.md | Style Warden 职能契约（SW-1..SW-8） |

---

YESTEST // style // V1.3 // G0