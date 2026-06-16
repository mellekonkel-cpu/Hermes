---
name: paper-figure-mapper
description: >-
  扫读论文/综述全文，识别需配图的关键数据/机理/概念，
  按 baoyu-article-illustrator 格式输出每张图的 prompt（YAML frontmatter + hex 色板 + 类型模板）。
  不生成图片。产出 prompt 文件后由用户选定平台批量出图。
author: Amaranth (via wiki-for-amaranth.pages.dev)
license: MIT
metadata:
  hermes:
    tags: [figures, illustrations, paper, prompts, review]
    source: "https://wiki-for-amaranth.pages.dev/skill-share/review-writing/"
---

# Paper Figure Mapper

## 与 baoyu-article-illustrator 的关系

```
论文/综述全文
  → 本 skill（paper-figure-mapper）：扫读 → 识别图位 → 产出 prompt 文件
  → baoyu-article-illustrator / mcp_meigen_generate_image / Codex CLI image2 → 出图
```

## 输入

论文/综述的章节文件列表。

## 输出

```
paper-figures/{paper-slug}/prompts/
├── _test-timeline-concept.md     # 测试图（先产1张）
├── 01-timeline-concept.md        # 批量产出
├── 02-comparison-data.md
└── ...
```

## 工作流

### Step 0：定义风格体系（一次性）
用户指定色板 + 渲染规则。之后所有图用同一套。

### Step 1：扫读 → 识别图位
逐节扫描，识别以下 8 类必须配图的信号：
| 信号 | 例子 |
|:-----|:------|
| 时间线/序列 | 1857→1908→1951→1994→… |
| 多路对比 | 方法 A vs 方法 B |
| 定量关系 | 线性拟合、定标公式 |
| 结构拆解 | 分子/界面/晶面的放大对比 |
| 决策分歧 | 当 X 走路径 A，当 Y 走路径 B |
| 分层框架 | 第一层…第二层…第三层… |
| 数据矛盾 | A 组报告 35 nm 红移，B 组报告 20 nm 蓝移 |
| 时空范围 | 不同技术的分辨率/灵敏度对比 |

### Step 2：归类 → 排序
| 优先级 | 标准 |
|:-----:|------|
| P0 | 无图就讲不清楚的核心概念（≤5 张） |
| P1 | 支撑关键论证的机理图解（5–8 张） |
| P2 | 深化数据展示（不限） |

### Step 3：测试一图 → 迭代确认风格（不可跳过）

### Step 4：批量产出剩余 prompt

支持5种类型模板：timeline / comparison / infographic / flowchart / framework

### Step 6：风格一致性验证

## Related Skills

- `review-chem-bio-pipeline` — Full pipeline
- `review-chem-bio-writing` — Writing conventions

## License

MIT License. From Amaranth's wiki-for-Amaranth wiki.
