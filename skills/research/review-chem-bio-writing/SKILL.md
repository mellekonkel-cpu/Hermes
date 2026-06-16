---
name: review-chem-bio-writing
description: >-
  化学/材料/生物领域综述的完整写作规范——两种写作模式：Critical Review（C-E-L-T推进）
  与大综述金风格（流动学术散文+期刊缩写引用+无框架标签+≥200DOI）。
  覆盖：数据密度规则、框架设计方法、(Author,Year,Journal,DOI)内联引用格式、
  去AI腔清洗流程、参考文献列表构建、质量轮三层方法论。
  与 precision-review-search / review-chem-bio-pipeline 配合使用。
author: Amaranth (via wiki-for-amaranth.pages.dev)
license: MIT
metadata:
  hermes:
    tags: [review, writing, chemistry, biology, academic]
    source: "https://wiki-for-amaranth.pages.dev/skill-share/review-writing/"
---

# 化学生物综述写作规范

## 数据密度规则（重要）

1. **每个论断必须跟一个具体数字**。"高灵敏度"不够——必须写 "25 copies/reaction (Tan 2024)"。
2. **比较表填真实数字，不填定性标签**。把 "高/中/低" 替换为具体 LOD 范围、具体时间、具体成本。
3. **给范围而非最优值**。LOD 报告 "22-1000 copies/reaction" 优于 "22 copies/reaction"。
4. **每节用 "钉子开门"**：用具体数据锚点开篇，不用 "随着科技的发展"。
5. **纯 md 交付**：除非用户明确要求，否则不编译为 HTML/PDF。

## 引用格式

使用内联格式 `(Author, Year, DOI:10.xxxx/xxxxx)`，不用 markdown 链接。中文输出用 "等人"：`(Tan等人, 2024, DOI:10.1002/jmv.29624)`。

## 框架设计规则

写综述时，技术分类是默认但不推荐的写法。更好的做法：
1. **设计一个独特的分析框架**，而不是按技术罗列。
2. **框架贯穿全文**——每一节都从框架出发分析。
3. **框架必须能用一句话说清楚**。

## 金风格(Gold Style)写作模式

目标：Chemical Reviews / Chem Soc Rev 级别的巨型综述(50K+中文字)。

1. **无框架标签**。框架在引言中交代清楚后，正文不再出现框架标签。
2. **每段2-3个数据点**。每个自然段应包含至少2-3个独立数据支撑。
3. **引用包含期刊缩写**。格式为 (Author, Year, *Journal Abbrev*, DOI:10.xxxx/xxxxx)。
4. **长段落**。不分割为短段。每段150-300字。
5. **前沿进展子结构**。每个技术主题下必须设一个"近年前沿进展"小节。
6. **代价嵌入句子**。每个技术讨论应自然包含收益和代价。
7. **不单独设限制段**。限制融入每个事实陈述的同一段。
8. **最终输出为纯md**。

## 去AI腔工作流

写作完成后执行以下机械清洗步骤：
1. 删除C/E/L/T行首标记
2. 删除加粗的C/E/L/T全段
3. 删除"关键观察""数据来源""解读"等局内标注
4. 删除"需要指出的是""值得注意的是"等AI填充词
5. 将"这一结论表明"类过渡句改为自然承接
6. 将孤立C/L/T字符清除

## 技术百科型（Technical Encyclopedia）

适用场景：用户明确说"技术百科"、"可查阅型"、"不按叙事线"时。

**核心特征：**
1. **按功能链路分卷，按技术条目分节。**
2. **每节固定三段式：** ①科学史/技术演进 ②近三年前沿按瓶颈分类 ③当前性能边界表
3. **主干方向 vs 技术选项的显式标注。**
4. **密度标注：** 每个技术条目标注真实发文密度 + 真正有POCT级性能的论文占比。

## Related Skills

- `review-chem-bio-pipeline` — Full pipeline (Phase 1-8)
- `precision-review-search` — Precision search pipeline
- `paper-figure-mapper` — Figure prompt generation

## License

MIT License. From Amaranth's wiki-for-Amaranth wiki.
