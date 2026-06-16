---
name: daily-briefing
description: Generate daily news briefings with expanded Chinese coverage (不压缩 — full detail, not summaries), supporting both web-search and no-internet (GitHub MCP) data acquisition strategies.
version: 1.5.2
author: Hermes Agent
license: MIT
metadata:
  tags: [news, briefing, daily, cron, github-mcp, no-internet, chinese]
---

# Daily Briefing (每日新闻简报)

Generate daily news briefings with expanded full-length Chinese reporting (不压缩 — user explicitly rejected compressed/summarized format). Supports two data acquisition strategies depending on the container/agent environment.

## When to Use

- User asks for "每日新闻简报", "daily briefing", "今日简报", "今天的新闻"
- A cron job needs to produce daily briefings automatically
- The user expects briefings to arrive without being prompted (passive delivery)

## Data Acquisition Strategies

### Strategy A: Web Search (preferred, requires internet)

Use web search tools (Tavily, Bing, Google) OR curl RSS feeds to find today's news.

**Enhanced path — MCP Search Routing (三层搜索架构):**

When a custom MCP search server is configured (mcp_search in mcp_servers), use it as the SECOND layer between RSS and web_search:

```
RSS feeds (curl)          ← 第一层：直接抓取
       ↓
mcp_mcp_search_search     ← 第二层：MCP 统一搜索
       ↓
web_search / web_extract  ← 第三层：兜底
```

MCP search tool: `mcp_mcp_search_search` (naming: mcp_{server_name}_{tool_name})
- mode=news — 优先走 You.com 新闻引擎
- mode=zh — 中文新闻
- mode=academic — 深度/学术视角
- mode=fast — 快速查询（默认 auto）
- mode=fallback — DuckDuckGo 零成本兜底
- mode=google — Serper Google 搜索

The MCP search tool auto-rotates API keys and falls through a 9-engine chain on failure.

**Working RSS feeds (tested from Docker containers that pass HTTP traffic):**

| Source | Feed URL | Language | Works when |
|--------|----------|----------|------------|
| BBC World | `https://feeds.bbci.co.uk/news/world/rss.xml` | EN | Internet OK |
| BBC中文 | `https://feedx.net/rss/bbc.xml` | CN | Internet OK |
| NYT World | `https://rss.nytimes.com/services/xml/rss/nyt/World.xml` | EN | Internet OK |
| Al Jazeera | `https://www.aljazeera.com/xml/rss/all.xml` | EN | Internet OK |

**Network detection:**
```bash
curl -s --max-time 10 https://www.reuters.com/ -o /dev/null -w "%{http_code}"
```
- `401` = TCP connected, internet works (Reuters requires auth but TCP handshake succeeded)
- Timeout (exit 124) = no internet, fall back to Strategy B
- Quick check: compare with `httpbin.org` or `8.8.8.8` ping (but these can also time out in Docker)

### Strategy B: GitHub MCP (fallback, no internet)

When the container/environment has no direct internet access (curl/browser timeouts) but GitHub MCP tools work:

1. **TypeThe0ry/news** — General news aggregation repo
   - Search: `mcp_github_search_code(q="YYYY-MM-DD news repo:TypeThe0ry/news")`
   - Read: `mcp_github_get_file_contents(owner, repo, path="news/YYYY-MM-DD.md")`
   
2. **osa-mayor/DailyUpdate** — Multi-source news aggregation repo
   - Available sources: GoogleNews, HadaNews, HackerNews, OfficialNews, ModelEvalSignals
   - Files exist as both `.json` and `.md` formats
   - Search: `mcp_github_search_code(q="YYYY-MM-DD repo:osa-mayor/DailyUpdate")`
   - Read: `mcp_github_get_file_contents(owner, repo, path="GoogleNews/google_news_YYYY-MM-DD.json")`

## Category Structure

Two mutually exclusive variants. Decide based on user's request:

### Variant A: Standard (International-first + Domestic)

**International news is PRIMARY; domestic is secondary but still required.** This user mandates comprehensive coverage with an international focus.

**Content priority: 不压缩** — every item must be a full write-up (800-1500+ chars). User explicitly rejected compressed/summarized versions.

Priority ordering (international sections always come first, within this exact order):
1. **国际·中东局势** (highest priority — US-Iran, Israel-Lebanon, OPEC, Gulf dynamics)
2. **国际·全球经济** (trade, inflation, central banks, stock markets, currencies)
3. **2026世界杯专题** (during tournament — matches, results, controversies)
4. **国际·政治与社会** (major political events across all regions: Europe, Africa, Russia-Ukraine, Asia)
5. **前沿科技** (AI, quantum, chips, new energy, space, biotech)
6. **国内新闻** (China economy, tech breakthroughs, industrial policy, social affairs)

~70% international, ~30% domestic. Both categories must be present in every briefing.

Keywords that trigger Variant A: "综合版", "国内外", "国际国内", "都要", "内容要求全面 包括国内外 但是要以国际新闻为主", "全面 包括国内外 以国际为主". This is the default for cron jobs.

### Variant B: International only

Original five-category structure (used when user specifically asks for "国际"):
1. 国际经济 (International Economy)
2. 前沿科技 (Frontier Technology)
3. 新能源电池 (New Energy Batteries)
4. 新材料 (New Materials)
5. 国内产业 (Domestic Industry — keep this even in international mode, but reduce weight)

## Cross-Verification (多源交叉核实) — HARD RULE

Every news item MUST be verified against TWO independent sources before being written into the briefing. This is a hard user requirement.

### Workflow
1. Identify a candidate story from one source (RSS, web search, GitHub repo)
2. Search for a SECOND independent source (different outlet, language, or region) that reports the same story
3. Cross-check core facts: names, dates, numbers, locations
4. Only write the item after confirming factual consistency
5. In the source field, list BOTH sources: `Straits Times/CBS News` or `路透社/BBC`

### Why
- GitHub news aggregator repos may contain stale, miscategorized, or hallucinated content
- Breaking news evolves rapidly; a single source may be inaccurate
- User explicitly requires multi-source verification before delivery

### Examples of paired sources
| Primary | Cross-check | Good for |
|---------|-------------|----------|
| Straits Times | CBS News | US-Iran conflict |
| BBC | Reuters | Middle East |
| Malay Mail | AFP | Iran official statements |
| ABP News | Livemint | India-related news |
| 央视 | 澎湃新闻 | China domestic news |

## Format Rules

### File Path
`/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.txt`

### Header
```
=== 每日新闻简报 | YYYY-MM-DD | 星期X ===

  🌍 
```

### Per-Category
```
── 国际经济 ──

1. Article Title | Source1/Source2
800-1500+ Chinese character expanded paragraph. Include: what happened, background context, multiple independent source cross-verification, market/geopolitical implications, forward outlook. No compression. No bullet points. No dashes. No quotation marks. Translate and explain English abbreviations on first occurrence, e.g. CPI（消费者物价指数）.
```

### Rules
- Continuous numbering across categories (do NOT reset per category)
- Format: `N. Title | Source`
- Line: `原文：URL`
- Paragraph: 800-1500+ Chinese characters per item — expand with background context, multiple source quotes, market impact analysis, historical context, and forward-looking implications
- DO NOT compress/summarize. User explicitly said "不要压缩新闻的内容". Each item should read like a mini-article, not a digest blurb
- Quality over quantity: 15-18 deeply expanded items is better than 20+ compressed ones
- NO bullet points in paragraphs
- NO dashes (破折号)
- NO quotation marks (引号)
- English abbreviations: add Chinese explanation in parentheses on FIRST use
- Limit to max 18 items total. The user prefers fewer items with deep coverage over many shallow items
- Last line: `=== 简报结束 | 共计 N 条深度报道 ===`

## Cron Job Setup — Step-by-Step

**CRITICAL: Before creating a new daily briefing cron, always check for existing ones first.**
Creating a second cron without removing the old one will cause duplicate deliveries, which the user has explicitly complained about ("你为什么发了两个").

### Procedure

1. **List existing cron jobs**: Run `cronjob action=list`. Look for jobs whose name or prompt matches "新闻简报", "每日新闻", "daily briefing", or "每日简报".

2. **Handle existing crons**:
   - If one exists with the same schedule (00:30 UTC), **update** it via `cronjob action=update` with the new prompt — do not create a duplicate.
   - If one exists with a different schedule (e.g., old 00:22 UTC text-based cron), **remove** the old one first via `cronjob action=remove job_id=...`, then create the new one.
   - Only proceed to create a brand new cron when no matching job exists.

3. **Choose the template** (below) and create/update the cron with the appropriate config.

4. **Verify**: Run `cronjob action=list` and check that `last_status` shows as `"ok"` after the first scheduled run. Better yet, manually test via `cronjob action=run job_id=<new_id>` and verify the delivery.

### Template — Web-based (internet available, preferred)

```yaml
name: 每日新闻简报PDF
schedule: "30 0 * * *"        # 00:30 UTC = 08:30 Beijing time
deliver: origin               # Send back to user's chat platform
enabled_toolsets: ["web", "terminal", "file", "search"]  # web for search, terminal for PDF gen, file for writing
```

### Template — GitHub MCP only (no internet)

```yaml
name: 每日国际新闻晨报
schedule: "30 0 * * *"        # 00:30 UTC = 08:30 Beijing time
deliver: origin               # Send back to user's chat platform
enabled_toolsets: ["file"]    # File tools for writing output
```

### Prompt Checklist

The cron prompt should always include:
- [ ] Current date context
- [ ] Content coverage: "涵盖国内外新闻，以国际为主" (international-first, 70/30 split)
- [ ] Cross-verification requirement (MUST check 2+ sources per item)
- [ ] Which data sources to check (三层架构: RSS → MCP search → web_search)
- [ ] MCP search tool: `mcp_mcp_search_search(query=..., mode="news")` for news gathering
- [ ] Full formatting instructions (no bullet points, no dashes, no quotes)
- [ ] File save path and PDF generation command
- [ ] Delivery date logging (append to 分发记录.log)
- [ ] Gap detection (read 分发记录.log, ask user if gap found)

See `references/cron-job-prompt.md` for the exact prompt text used in the user's active cron.

## Catch-Up Flow (开机后补简报)

When the user returns after being offline (computer was off, container stopped), check the delivery log first, then archive directory for gaps:

1. Read `/opt/data/青桑/每日简报存档/分发记录.log` to find the last delivery date
2. Also list all files in `/opt/data/青桑/每日简报存档/每日新闻简报_*.txt` for cross-reference
3. If gap exists (last log date vs today), **ask the user first**: "检测到上次简报分发于YYYY-MM-DD，中间缺口N天，是否需要整合补发？"
4. Only proceed after explicit confirmation (user preference: never auto-execute)
5. For each missing day, regenerate by searching web (Strategy A) or GitHub news repos (Strategy B)
6. Compile into a single summary document, deliver as file attachment

**Rule**: 发现缺口 → 先问用户 → 得到确认再执行。绝不擅自行动。

## Delivery Date Logging (分发记录)

After each successful briefing delivery, append a record to the delivery log so gaps can be detected later.

### Log File Path
`/opt/data/青桑/每日简报存档/分发记录.log`

### Format (append only, one line per delivery)
```
2026-06-12 | ✅ 已分发 | PDF | 14条深度报道 | v2（更新版含特朗普-伊朗协议）
```

### When to Log
- AFTER the PDF/txt file is generated and verified
- BEFORE the final MEDIA: delivery line
- Append via terminal: `echo "YYYY-MM-DD | ✅ 已分发 | PDF | N条深度报道" >> /opt/data/青桑/每日简报存档/分发记录.log`

### Gap Detection on Cron Run
Each cron job run should read the last line of the log file. If the date on that line is older than yesterday, the job should append to its final response: "检测到上次简报分发于YYYY-MM-DD，中间缺口N天，是否需要整合补发？"

## Delivery Format: PDF (Primary) / Text (Fallback)

**PDF is the primary delivery format.** This user explicitly requires PDF versions of all briefings. Text (`.txt`) is only used as a fallback when PDF generation fails (e.g., fpdf2/fontTools unavailable, font missing, disk space).

The cron job prompt and delivery workflow must always attempt PDF generation first, and only fall back to `.txt` on confirmed failure.

### PDF Generation (Requires fpdf2 + fontTools)

Standard PDF fonts (Helvetica, Times, Courier) do NOT support Chinese characters. Attempting to use them produces blank pages.

Use the skill's `gen_pdf.py` script which handles fpdf2 + fontTools auto-installation and uses the system's wqy-zenhei.ttc Chinese font:

```bash
# Preferred: fpdf2 installed in venv
PYTHONPATH=/opt/hermes/.venv/lib/python3.13/site-packages:$PYTHONPATH \
python3 /opt/data/skills/research/daily-briefing/scripts/gen_pdf.py \
  /opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.txt \
  /opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.pdf
```

**fontTools install locations (try in order):**
1. `/opt/hermes/.venv/lib/python3.13/site-packages/` (via `uv pip install fpdf2 fonttools`)
2. `/opt/data/home/.local/lib/python3.13/site-packages/` (via `setup.py install --user`)

**System Chinese font path (confirmed working):** `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`

**Installation (uv preferred):**
```bash
uv pip install fpdf2 fonttools
```

**Pip-less install procedure** (for environments without pip):
```bash
# 1. Download source tarballs
curl -sL https://files.pythonhosted.org/packages/source/f/fpdf2/fpdf2-2.8.1.tar.gz -o /tmp/fpdf2.tar.gz
curl -sL https://files.pythonhosted.org/packages/source/f/fonttools/fonttools-4.55.3.tar.gz -o /tmp/ft.tar.gz

# 2. Extract and install to user site-packages
cd /tmp && tar xzf fpdf2.tar.gz && cd fpdf2-* && python3 setup.py install --user
cd /tmp && tar xzf ft.tar.gz && cd fonttools-* && python3 setup.py install --user
```

**Common failure: "Not enough horizontal space to render a single character"**
- Cause: Long URL line exceeding page width
- Fix: Set `pdf.set_left_margin(15)` and `pdf.set_right_margin(15)`, use 7pt font for URLs, truncate long URLs at ~90 chars

**Important:** DeepSeek API does NOT support `image_url` content type in chat/completions. The built-in `vision_analyze` tool will fail with `unknown variant image_url, expected text`. Use the SiliconFlow API directly instead (see Pitfalls section below — `SILICONFLOW_KEY` + `Qwen/Qwen3-VL-8B-Instruct` works).

The script:
- Auto-installs fpdf2 and fontTools via curl + setup.py install --user if missing
- Uses `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` for CJK text
- Formats: section headers in blue, URL lines in gray, auto page breaks
- Falls back gracefully — if install fails, just deliver as `.txt` instead

### Format Variants

Two variants supported:

| Variant | File Suffix | When to Use |
|---|---|---|
| Standard (default) | `每日新闻简报_YYYY-MM-DD` | General purpose, covers all 5 categories |
| International | `每日新闻简报_YYYY-MM-DD_国际版` | User specifically wants international/foreign news focus, skips domestic |

### File Delivery via WeChat MEDIA

When delivering the briefing to WeChat, the final agent response should contain a single line:

```
MEDIA:/opt/data/青桑/每日简报存档/每日新闻简报_YYYY-MM-DD.pdf
```

This `MEDIA:` prefix is interpreted by the WeChat gateway as an instruction to attach the file as a native document download rather than embedding the text in the chat message.

**Important**: The MEDIA line must be the **final/only** content of the agent's response. Extra text after it may be ignored or treated as a separate message.

### Cron Job Delivery Configuration

The cron job must use `deliver: origin` (NOT `deliver: local`) so the agent's final response (including the MEDIA: line) is forwarded back to the user's chat. With `deliver: local`, the file would be saved to disk but never reach the user.

```yaml
# Correct cron job config:
deliver: origin
enabled_toolsets: ["file"]
```

The `file` toolset is needed for writing the briefing file. MCP GitHub tools (for data source) and fpdf2+fontTools (for PDF generation) are handled separately — MCP comes from config.yaml, PDF deps are auto-installed by `gen_pdf.py`.

## User Preference: Browser Verification

Before presenting any news to the user, verify the original source article in a browser:

```
GitHub搜到新闻 → 用浏览器打开原文核实 → 确认无误再发
```

This is a hard user preference. GitHub news aggregator repos may contain stale, miscategorized, or hallucinated content. Always check the original URL.

## Network Independence Note (Proxy/Search Gap)

Important: Hermes' `web_search` tool and `web_extract` tool use their own backend (Parallel Search / custom MCP search server) — they are **not** routed through the container's mihomo/Clash proxy. This means:

| Tool | Works without proxy? | Notes |
|------|---------------------|-------|
| `web_search` | ✅ Always | Uses its own search backend, independent of curl/proxy |
| `web_extract` (domestic sites) | ✅ Yes | e.g. CCTV, 澎湃, Sina — directly reachable |
| `web_extract` (overseas sites) | ❌ No | e.g. BBC, Reuters, Al Jazeera — need GFW bypass |
| `curl` to overseas sites | ❌ No | Times out without proxy |

**Practical impact on briefings:**
- Even if the user's Clash/mihomo proxy is down, **web_search still finds news** — it returns results for any query regardless of whether the container has overseas HTTP access.
- `web_extract` for cross-verification of overseas sources (BBC, Reuters, WSJ) will fail without proxy. Workaround: use `web_search` to find multiple sources reporting the same story, or switch to domestic sources (CCTV, 澎湃, 央视) that are directly reachable.
- Strategy A (web) with Layers 2+3 works fully independent of the proxy. Only Layer 1 (RSS curl) requires the proxy.
- Detect this state: `web_search` responds but `curl -s --max-time 10 https://www.reuters.com/` times out = proxy down, use web_search only.

This is explicitly tested: during the 2026-06-17 session, `web_search` returned results while curl to Reuters timed out (HTTP 000).

## Pre-run Checks

### 1. DeepSeek API Balance

The DeepSeek key is stored as `DEEPSEEK_API_KEY` in the `.env` file (using OpenAI-compatible endpoint at `https://api.deepseek.com`).  
**Path**: `/opt/data/.env`, NOT `~/.hermes/.env`.

```bash
# Check balance — correct endpoint is /v1/user/balance, NOT /v1/dashboard/balance
source /opt/data/.env && curl -s --max-time 10 https://api.deepseek.com/v1/user/balance \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

If balance is below 1 CNY, alert the user but proceed with generation.

### 2. Network Availability

```bash
curl -s --max-time 10 https://www.reuters.com/ -o /dev/null -w "%{http_code}"
```

Interpret results (401 = internet works, TCP connected):

| Result | Meaning | Strategy |
|---|---|---|
| Exit 124 (timeout) | No internet | B (GitHub MCP) |
| HTTP 401 | **Internet works** (TCP OK) | A (web search) or B |
| HTTP 200-499 | Internet works | A (web search) |
| Exit 0, no output | Network blocked at kernel | B (GitHub MCP) |

### 3. Cron Health

After setup, verify the cron job ran:

```bash
hermes cron list
```

Check that `last_run_at` is non-null and `last_status` is `"ok"`. A `last_run_at: null` means the job never fired — common causes:
- The referenced script file doesn't exist (for `no_agent=true` jobs)
- The cron scheduler hasn't ticked yet (use `hermes cron run <job_id>` to test)
- The job's `next_run_at` is in the past but scheduler is busy

### 4. Config File Locations

In this user's environment (Docker with volume mount), config files are at:

| File | Path |
|---|---|
| Config | `/opt/data/config.yaml` |
| Environment | `/opt/data/.env` |
| Auth/credentials | `/opt/data/auth.json` |

NOT at `~/.hermes/` — the home directory inside the container is not the mounted volume.

## Pitfalls

- **Browser-verify GitHub news**: GitHub news repos may contain stale, miscategorized, or hallucinated articles. Always open the original URL (浏览器) to verify before presenting to the user. "GitHub找到新闻后须用浏览器打开原文核实后再发" is the user's explicit rule.
- **Container no-internet**: Many Docker containers block curl/wget/browser. Do NOT retry failed network commands. Use GitHub MCP instead. See [references/news-rss-feeds.md](references/news-rss-feeds.md) for working RSS feeds when internet is available.
- **Script never existed**: A `no_agent=true` cron referencing a script that doesn't exist will silently fail with no errors. Always verify `last_run_at` after setup.
- **Memory limits**: Briefing files can be large (2000+ lines over 10 days). Don't read all at once into context.
- **Subagents without MCP**: delegate_task subagents do NOT get MCP tools by default. Run news searches in the main session.
- **Old format data**: Some GitHub news repos include stale articles (e.g. 2025 data mixed with 2026). Filter by date.
- **Korean/Japanese content**: osa-mayor/DailyUpdate GoogleNews has Korean summaries and tags. Use as raw data, not final output.
- **Config file paths**: The user's `.env` and `config.yaml` are at `/opt/data/` (the mounted volume root), NOT at `~/.hermes/`. Searching `~/.hermes/` for API keys will find nothing. The DeepSeek key is stored as `DEEPSEEK_API_KEY` (not `OPENAI_API_KEY`). The `source /opt/data/.env` approach works for balance checks.
- **MCP tool naming**: Custom MCP server tools follow the pattern `mcp_{server_name}_{tool_name}`. For example, server name `mcp_search` with tool `search` becomes `mcp_mcp_search_search`. Check the actual tool name by looking at gateway logs or by calling `mcp_mcp_search_check_engine_status` when available.
- **MCP search server rate limits**: TinyFish free tier is 5 req/min for search, 25 URL/min for fetch. The MCP server handles automatic fallback through the engine chain on failure, but batch tasks should still be throttled.
- **Vision_analyze tool fails (DeepSeek)**: The built-in `vision_analyze` tool sends `image_url` content type which DeepSeek chat/completions API does not support. Always returns `unknown variant image_url`.
- **SiliconFlow vision API DOES work (direct call)**: When the user needs image analysis, read `SILICONFLOW_KEY` from `/opt/data/.env` and call `https://api.siliconflow.cn/v1/chat/completions` with model `Qwen/Qwen3-VL-8B-Instruct` (faster) or `Qwen/Qwen3-VL-32B-Instruct` (better quality). Base64-encode the image and submit as `image_url` with `data:image/jpeg;base64,...`. Use the `payload.json` + `curl -d @file` pattern to avoid "Argument list too long" errors with large images. See `references/siliconflow-vision.md` for working code.
- **PDF generation font**: Standard PDF fonts render blank pages for Chinese text. Must use wqy-zenhei.ttc or another CJK TTF font. Set PYTHONPATH to include user site-packages where fpdf2+fontTools are installed.
- **PDF "no horizontal space" error**: Long URL lines in multi_cell exceed page width. Fix by reducing URL font size to 7pt, setting explicit margins (15mm), and truncating URLs at ~90 chars.
- **Duplicate cron jobs cause duplicate deliveries**: Before creating a new daily briefing cron job, ALWAYS run `cronjob action=list` to check for existing jobs with similar names/prompts. If a duplicate exists, remove the old one via `cronjob action=remove job_id=...` first. This user received duplicate briefings when two cron jobs (old text-based + new PDF) ran on the same day — causing confusion ("你为什么发了两个"). Only one daily briefing cron should be active at any time.