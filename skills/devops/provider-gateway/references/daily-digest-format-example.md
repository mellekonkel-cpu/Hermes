# Daily Digest Format Reference

## Full Example Output

```
=== 每日新闻简报 | 2026-05-22 | 星期五 ===

  🌍 International Day for Biological Diversity

── 国际经济 ──

📌 概览：美国关税政策持续升级，中美贸易关系释放稳定信号但不确定性仍存...

1. 全球市场周报 | T. Rowe Price
原文：https://www.troweprice.com/personal-investing/resources/insights/global-markets-weekly-update.html
[200-500 word Chinese paragraph summarizing the article content]

2. ...

── 前沿科技 ──

📌 概览：AI芯片领域持续突破...

...

=== 简报结束 | 共计 18 条深度摘要 ===
```

## Format Rules

- `===` banners at top and bottom
- Date format: YYYY-MM-DD
- Weekday in Chinese (星期一 through 星期日)
- Holiday line: `  🌍 Holiday Name` (indented 2 spaces)
- Category headers: `── Category Name ──`
- Overview line: `📌 概览：[sentence]`
- Article entries:
  - `N. Title | Source`
  - `原文：URL`
  - Paragraph of 200-500 Chinese characters
- No bullet points in summaries
- No dashes (—) or quotation marks ("") in summaries
- No markdown formatting
- Items are numbered sequentially across all categories (1, 2, 3, ...)

## Archive Path

Archives directory: `/opt/data/青桑/每日简报存档/`
Script: `/opt/data/skills/devops/provider-gateway/scripts/fetch-daily-news.py`

⚠️ 根目录不再保留每日新闻简报.txt。简报仅在存档目录中按日期保存。
