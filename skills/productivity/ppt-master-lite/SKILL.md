---
name: ppt-master-lite
description: 自建 PPT 生成引擎，Markdown → 原生 PPTX。基于四本设计经典（Tufte/CRAP/Duarte/Knaflic），8 套调色板，可编辑的原生形状。
category: productivity
---

# PPT-Master Lite

自建版 PPT 生成器。输入 Markdown 大纲，输出原生 `.pptx`（可在 PowerPoint 里继续编辑）。

## 设计系统

四本经典教材的设计规则已编码到生成器中：

| 原则 | 来源 | 实现 |
|------|------|------|
| 数据墨水比 | Tufte | 去装饰，留白充分 |
| CRAP 四原则 | Robin Williams | 对比/重复/对齐/邻近 |
| 5 条幻灯片规则 | Duarte | 一页一件事 |
| 去杂乱 | Knaflic | 简化颜色/去掉默认网格线 |

### 8 套调色板

| 调色板 | 风格 | 适用场景 |
|--------|------|---------|
| `business` | 深蓝灰+红 | 商务汇报 |
| `tech` | 深海蓝+青 | 科技产品 |
| `academic` | 深红+藏青 | 学术论文 |
| `modern` | 青绿+陶土 | 现代简洁 |
| `nature` | 草绿+墨绿 | 环保/自然 |
| `vibrant` | 橙+青 | 活力明快 |
| `luxury` | 黑+金+蓝 | 奢华高端 |
| `creative` | 粉紫+天蓝 | 创意设计 |

## 用法

```bash
python3 /opt/data/scripts/ppt-master-lite.py input.md -o output.pptx -p tech
```

从 stdin 输入：
```bash
cat outline.md | python3 /opt/data/scripts/ppt-master-lite.py - -o deck.pptx -p academic
```

### 参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `input` | Markdown 文件路径，`-` 为 stdin | 必填 |
| `-o` | 输出路径 | `output.pptx` |
| `-p` | 调色板 | `business` |
| `--aspect` | 比例 `16:9` 或 `4:3` | `16:9` |

## 大纲格式

```markdown
# 总标题（封面页）

## 第一页标题

- 要点一
- 要点二
  - 子要点
- 要点三

## 第二页标题

| 表头1 | 表头2 | 表头3 |
|-------|-------|-------|
| 数据1 | 数据2 | 数据3 |

## 结论

- 总结点一
- 总结点二
```

支持 `-` 列表、`1.` 编号列表、表格。
