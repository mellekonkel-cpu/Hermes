# 电池对比信息图 — Prompt 工程参考

## 已测试的模型
| 模型 | 耗时 | 风格 | 适用场景 |
|---|---|---|---|
| Qwen/Qwen-Image | ~10-17s | 精准，适合学术图 | 第一选择 |
| Kwai-Kolors/Kolors | ~4s | 偏艺术渲染 | 速度优先 |
| Tongyi-MAI/Z-Image-Turbo | ~2.5s | 一般 | 快速测试 |

## Prompt 风格模板

### 通用学术风格
> Academic journal style figure, side-by-side comparison of battery energy density. Left panel labeled 'Traditional': graphite anode + NCM cathode, cylindrical cell schematic, simple bar chart at 250 Wh/kg. Right panel labeled 'Advanced': lithium metal anode + LRMO cathode, pouch cell schematic, glowing bar chart at 450+ Wh/kg with highlighted effect. Center arrow 'Energy Density Boost' with particles. Scientific illustration style, white background, blue and teal professional color scheme, clean technical lines, minimal text, research journal quality.

### Nature 期刊风格
> Nature journal Figure 1 style. Side-by-side comparison diagram of battery energy density. Left panel: Traditional System, graphite anode + NCM cathode, schematic of cylindrical 18650 cell with labeled layers Graphite and NCM, bar chart at 250 Wh/kg. Right panel: Advanced System, lithium metal anode + LRMO cathode, schematic of pouch cell with labeled layers Lithium Metal and LRMO, taller glowing bar chart at 450+ Wh/kg. Center arrow with Energy Density Enhancement label. White background, Nature journal figure formatting, clean Helvetica font, professional blue and teal colors, minimalist scientific illustration, publication-quality.

### ACS 期刊风格
> ACS journal Graphical Abstract style. Comparison infographic of battery energy density. Left: graphite anode + NCM cathode, cylindrical cell drawing, energy density bar 250 Wh/kg. Right: lithium metal anode + LRMO cathode, pouch cell drawing, energy density bar 450+ Wh/kg with glow. Center arrow labeled Energy Density Boost. ACS journal style, white background, clean Arial font, blue and teal ACS color palette, crisp lines, professional chemistry materials science journal figure, minimal text, high resolution.

## 关键要点
- 白色背景比深色背景更接近学术期刊风格
- Qwen-Image 对科学插图的理解最好，但速度最慢
- 指定字体（Helvetica/Arial）有助于保持干净外观
- 用 "publication-quality"、"journal figure" 等词强化学术感
- 平衡图里的文字不宜过多，模型对中文支持有限
