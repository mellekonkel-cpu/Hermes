# Environment: Docker + WSL 青桑 Instance

Config file paths for this user's Docker container environment.

## Key Paths

| File | Actual Path | Expected (but wrong) Path |
|---|---|---|
| Config YAML | `/opt/data/config.yaml` | `~/.hermes/config.yaml` |
| Environment vars | `/opt/data/.env` | `~/.hermes/.env` |
| Auth credentials | `/opt/data/auth.json` | `~/.hermes/auth.json` |
| Cron jobs | `/opt/data/cron/jobs.json` | `~/.hermes/cron/` |

The container mounts the host's `~/.hermes/` to `/opt/data/` in the container.
So what was `~/.hermes/config.yaml` on the host is `/opt/data/config.yaml` inside.

**Never search `~/.hermes/` inside the container** — it's empty or doesn't exist.
Always search `/opt/data/` for config files.

## DeepSeek API Key

Stored as `OPENAI_API_KEY` in `/opt/data/.env`, using OpenAI-compatible endpoint:

```
OPENAI_API_KEY=sk-58d792ce711646cd84655d7902e47654
OPENAI_BASE_URL=https://api.deepseek.com
```

The API key is NOT stored as `DEEPSEEK_API_KEY` — searching for that env var will find nothing.

## Balance Check

```bash
curl -s --max-time 10 https://api.deepseek.com/v1/user/balance \
  -H "Authorization: Bearer $(grep OPENAI_API_KEY /opt/data/.env | cut -d= -f2)"
```

Use `/v1/user/balance`, NOT `/v1/dashboard/balance` (the latter returns empty output silently).

## Network Detection

This is the definitive detection method, tested against this specific Docker environment:

```bash
curl -s --max-time 10 https://www.reuters.com/ -o /dev/null -w "%{http_code}"
```

### Interpretation

| Exit Code / Output | Meaning | Strategy |
|---|---|---|
| Exit 124 (timeout) | No internet at all | B (GitHub MCP only) |
| HTTP **401** | **Internet works** — TCP handshake succeeded, Reuters just requires auth | A (web search) or B |
| HTTP 200 or 403 | Internet works | A (web search) |
| Exit 0, no output | Network blocked at kernel level | B (GitHub MCP) |

**Key insight**: HTTP 401 = internet works, even though the page isn't returned. The TCP connection succeeded. Do NOT treat 401 as "blocked".

### Quick Alternative

```bash
# Google News RSS as smoke test
curl -s --max-time 10 "https://news.google.com/rss/search?q=test&hl=en-US" | head -1
```

If this outputs XML, internet works. If timeout/broken pipe, no internet.

## Author

Discovered: 2026-06-11 during cron job and PDF generation setup.
