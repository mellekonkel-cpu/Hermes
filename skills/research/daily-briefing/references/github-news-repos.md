# GitHub News Repositories for No-Internet Briefings

Used by `daily-briefing` skill when the container has no direct internet access but GitHub MCP is available.

## TypeThe0ry/news

**URL**: https://github.com/TypeThe0ry/news
**Description**: 实时更新的全自动新闻仓库
**File format**: Markdown (.md) — each day is `news/YYYY-MM-DD.md`
**Content**: RSS-curated news from FT, BBC, NYT, Al Jazeera, SCMP, etc.
**Notes**: Contains ~50-60 articles per day. Some entries have 2025 stale data (especially WSJ Market articles). Filter by context. The repository has a `flat` directory structure with dates.

## osa-mayor/DailyUpdate

**URL**: https://github.com/osa-mayor/DailyUpdate
**Description**: Multi-source daily news aggregation
**File format**: Both JSON (structured) and Markdown (readable) per source per day

### Available Sources
| Source Directory | Format | Content |
|---|---|---|
| `GoogleNews/` | JSON + MD | Tech-focused AI/LLM news, Korean summaries |
| `HadaNews/` | JSON + MD | General news, Korean summaries |
| `HackerNews/` | JSON + MD | Tech/startup news |
| `OfficialNews/` | JSON | Official/press release news |
| `ModelEvalSignals/` | JSON | AI model evaluation data |

### Key Files
- `GoogleNews/google_news_YYYY-MM-DD.json` — Tech news with Korean summaries, tags, daily_key_points
- `HadaNews/hada_news_YYYY-MM-DD.json` — General news
- `HackerNews/hacker_news_YYYY-MM-DD.json` — Tech community news
- Both repos also have `*_latest.json` symlinks pointing to the most recent day's file

### Notes
- GoogleNews JSON has rich metadata: `category`, `summary`, `technical_value`, `key_points`, `tags`
- Summaries are in Korean — use as raw data, rewrite in Chinese
- Published daily around 04:00-05:00 KST (19:00-20:00 UTC previous day)

## Search Pattern

```python
# Find today's news files
mcp_github_search_code(q="YYYY-MM-DD news repo:TypeThe0ry/news")
mcp_github_search_code(q="YYYY-MM-DD repo:osa-mayor/DailyUpdate")

# Get specific file
mcp_github_get_file_contents(
    owner="TypeThe0ry",
    repo="news",
    path="news/YYYY-MM-DD.md"
)

mcp_github_get_file_contents(
    owner="osa-mayor",
    repo="DailyUpdate",
    path="GoogleNews/google_news_YYYY-MM-DD.json"
)
```

## Category Mapping

For the briefing categories, map GitHub news data as follows:

| Briefing Category | Best Sources |
|---|---|
| 国际经济 | TypeThe0ry news (FT, BBC, Reuters economy), SCMP business |
| 前沿科技 | GoogleNews (osa-mayor), HackerNews, TypeThe0ry tech |
| 新能源电池 | TypeThe0ry filtered (search within for "battery") |
| 新材料 | TypeThe0ry filtered (search within for "material|graphene|composite") |
| 国内产业 | SCMP (TypeThe0ry has good China coverage) |

## Limitations

- Korean summaries must be translated/rewritten to Chinese
- WSJ articles from Jan 2025 are stale but appear in search results — check publish date
- No dedicated battery/materials sections — these must be manually filtered from general news
- Coverage favors US/Europe/Asia politics and AI tech over specialized materials science
- Updates depend on the repo owner's cron schedule (typically UTC 04:00-08:00 daily)
