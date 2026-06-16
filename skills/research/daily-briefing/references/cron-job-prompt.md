# Daily Briefing Cron Job Prompt Template

Two variants depending on internet availability.

## Variant A: Web-based (internet available, preferred)

### Cron Config
```yaml
name: 每日新闻简报PDF
schedule: "30 0 * * *"        # 00:30 UTC = 08:30 Beijing time
deliver: origin
enabled_toolsets: ["web", "terminal", "file", "search"]
```

### Full Prompt

```
今天是新的一天。你的任务是生成今日的每日新闻简报PDF并进行多源交叉核实后以PDF文件形式交付。

## 硬规则
1. 交叉核实：每条新闻必须打开至少两个独立来源（如BBC+Reuters、央视+澎湃等）核对事实一致性，确认后方可写入
2. 连续编号跨类别不重置
3. 英文缩写首次出现括号加中文注释，如CPI（消费者物价指数）
4. 无bullet points、无破折号、无引号
5. 不压缩内容，每条展开写800-1500+字中文段落，包含事件背景、多源核实细节、影响分析、各方引述和后续展望
6. 总数控制15-18条，写透为止。质量优先于数量

## 内容覆盖范围\n必须同时涵盖国际和国内新闻，以国际为主：\n- 国际新闻（约70%）：中东局势（优先）、全球经济、欧洲非洲、俄乌冲突、亚洲动态、2026世界杯（赛事期间）、前沿科技、国际政治社会\n- 国内新闻（约30%）：中国经济、科技突破、产业政策、社会民生、文化娱乐\n两者都必须有，以国际新闻占多数。约15-18条深度覆盖，不追求数量追求每条写透。\n\n## 内容分类（按此顺序组织）\n- 中东局势（美伊、以色列-黎巴嫩等，优先于其它类别）\n- 全球经济（贸易、通胀、股市、央行政策）\n- 2026世界杯专题（赛事期间）\n- 政治与社会（各国重大政治事件）\n- 前沿科技（AI、量子计算、芯片、新能源）\n- 国内产业（中国经济、科技、产业政策）

## 数据来源
请使用web_search搜索今日新闻，同时curl抓取以下RSS源：
- BBC World: https://feeds.bbci.co.uk/news/world/rss.xml
- Al Jazeera: https://www.aljazeera.com/xml/rss/all.xml
- 央视国际: https://news.cctv.com/world

## 交叉核实流程
对每条候选新闻：
1. 从第一个来源获取标题和摘要
2. 搜索第二个独立来源进行验证
3. 确认核心事实一致后写入
4. 在来源字段列出双来源，如"Straits Times/CBS News"

## 文件路径
文本：/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.txt
PDF：/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.pdf

## 格式
第一行：=== 每日新闻简报 | YYYY-MM-DD | 星期X ===
空行后：  🌍
每个分类以"── 分类名 ──"开头，后面接具体条目。

## PDF生成
使用fpdf2+fontTools（已在/opt/hermes/.venv/下安装）：
```bash
PYTHONPATH=/opt/hermes/.venv/lib/python3.13/site-packages python3 /opt/data/skills/research/daily-briefing/scripts/gen_pdf.py "/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.txt" "/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.pdf"
```

## 分发记录
PDF生成后，在/opt/data/青桑/每日简报存档/分发记录.log末尾追加一行：
YYYY-MM-DD | ✅ 已分发 | PDF | N条深度摘要

## 断档检查
读取分发记录.log的最后几行。如果发现上次发送日期距今天超过1天（即存在缺口），在最终回复中附上询问："检测到上次简报分发于YYYY-MM-DD，中间缺口N天，是否需要整合补发？"

## 交付
验证PDF文件存在后，最终回复只输出一行：
MEDIA:/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.pdf

如果PDF生成失败，改为发送txt文件：
MEDIA:/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.txt
```

## Variant B: GitHub MCP (no internet)

### Cron Config
```yaml
name: 每日国际新闻晨报
schedule: "30 0 * * *"        # 00:30 UTC = 08:30 Beijing time
deliver: origin
enabled_toolsets: ["file"]
```

### Full Prompt
```
今天是新的一天。你的任务是生成今天的每日新闻简报，并以文件形式发送。

## 数据来源
你的容器没有直接互联网访问，但 GitHub MCP 工具是通的。请通过以下两个 GitHub 仓库获取新闻数据：
1. TypeThe0ry/news 仓库下的 news/目录，查找 YYYY-MM-DD.md（如 2026-06-12.md）
2. osa-mayor/DailyUpdate 仓库下的 GoogleNews/google_news_YYYY-MM-DD.json 和 HadaNews/hada_news_YYYY-MM-DD.md

使用 mcp_github_search_code 搜索今天的文件，然后用 mcp_github_get_file_contents 读取内容。

## 交叉核实（重要！）
从GitHub获取的每条新闻必须用浏览器打开原文核实后再写入。GitHub news repos may contain stale, miscategorized, or hallucinated content.

## 简报格式要求（严格遵守）

### 文件路径
1. 写入 /opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.txt
2. 再用gen_pdf.py转为PDF

### 标题格式
第一行：=== 每日新闻简报 | YYYY-MM-DD | 星期X ===
然后一个空行，接着两个空格加地球emoji（  🌍），再一个空行

### 内容格式
按以下分类组织：
- 国际经济
- 前沿科技
- 新能源电池
- 新材料
- 国内产业

每个分类下：
1. 第一行：📌 概览：用一句话概括该分类今日要点
2. 然后逐条写新闻，连续编号跨类别不重置

每条新闻格式：
编号. 标题 | 来源
原文：URL
一段800-1500+字的中文段落摘要。不要压缩，展开写，包含事件背景、多源核实细节、影响分析和后续展望。段落中不要使用bullet points、破折号或引号。英文缩写首次出现时括号加中文注释，如CPI（消费者物价指数）。

### PDF生成
```bash
PYTHONPATH=/opt/hermes/.venv/lib/python3.13/site-packages python3 /opt/data/skills/research/daily-briefing/scripts/gen_pdf.py "/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.txt" "/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.pdf"
```

### 分发记录
追加一行到 /opt/data/青桑/每日简报存档/分发记录.log：
YYYY-MM-DD | ✅ 已分发 | PDF | N条深度摘要

### 断档检查
读取分发记录.log最后几行。如果上次发送日期距今天超过1天，询问用户是否需要整合补发。

### 交付
验证文件后，只输出：MEDIA:/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.pdf
```

## History

| Date | Change |
|------|--------|
| 2026-06-11 | Initial template (GitHub MCP only, file tools) |
| 2026-06-12 | Added Variant A (web-based with cross-verification); Added delivery logging + gap detection; Updated PYTHONPATH to venv |
| 2026-06-12 | Updated Variant A: international-first classification (70/30 split), PDF-as-primary format |
| 2026-06-12 | Expanded format: changed per-item length from 200-500 to 800-1500+ chars; added "不压缩" rule; added 15-18 item count guidance; restructured content coverage section |
