---
title: Provider Gateway (信息交换枢纽)
name: provider-gateway
description: Route requests across multiple external API providers — SiliconFlow (主力), Tavily (搜索), OpenRouter (海外免费模型). The user acts as a hub, supplying API keys; the agent handles all backend routing and aggregation.
trigger: User asks to configure/test/verify external API providers, or makes a request that should be routed through a configured provider (text chat, image gen, search, etc.)
---

# Provider Gateway (信息交换枢纽)

The user supplies API keys from various platforms. The agent acts as a routing hub — no direct calls from user to any backend. Route all external-API tasks through this system.

## Provider Roles

| Provider | Role | Speed | Region | Format | Auth |
|----------|------|-------|--------|--------|------|
| **SiliconFlow** (硅基流动) | Primary — text, image, video, voice, OCR, **ASR**, embedding | Fast | 🇨🇳 Domestic | OpenAI-compat | Bearer header |
| **Tavily** | AI-optimized web search (ultra-fast/fast/basic/advanced) | Medium | Global | JSON POST | Key in body |
| **OpenRouter** | Complement — only specific free models | Variable | 🌐 Overseas | OpenAI-compat | Bearer header |
| **Google AI Studio** | Gemini models (flash/pro/lite) | Medium | 🌐 Overseas | ❌ Native Google AI | Query param `?key=` |
| **SenseNova** (商汤日日新) | Fallback — text, multimodal vision | Medium | 🇨🇳 Domestic | OpenAI-compat | Bearer `sk-` / env: `SN_API_KEY` (per user's Amaranth Wiki) |

## Non-OpenAI-Compatible Providers

Some providers use different API formats. **Do NOT assume OpenAI format** — check the reference file first:

| Provider | Reference | Key Difference |
|----------|-----------|---------------|
| **Google AI Studio** | `references/google-ai-studio.md` | Uses `contents/parts` format, auth via query param |

When routing to these, load the reference file and construct the request manually.

## Session Continuity

After complex multi-step configurations (adding new providers, batch testing), maintain a todo list (`todo` tool) so the user can ask "我们刚才进行到底哪里了" and get a clear answer. This prevents losing progress in session handoffs.

## Writing Style for Provider Descriptions

This user has a strong preference for **single continuous paragraphs** over structured/bulleted output when writing prose for provider applications, requirement descriptions, or any text that reads as a statement or narrative.

- "整段" = one coherent paragraph, not bullet points or numbered items
- This applies to: provider application 需求描述, API usage declarations, personal introductions, or any text submitted to a third-party form
- The rule is already in memory for 润色 (polish) tasks; extend it to any first-draft prose written for the user
- When in doubt, write a paragraph; only use structure (bullets, numbered sections) when the user explicitly says "分点" or "列出来"

### 1. Route a Request
Check the user's intent, then choose the right provider:
- **Text chat / image gen / video / voice / OCR / embedding** → SiliconFlow (OpenAI-compatible, call via `curl` or Python)
- **Image / visual analysis (VL/vision)** → **Do NOT use current model** — most text models (including `DeepSeek-V4-Flash`) do NOT support `image_url` in messages. Route to a dedicated VL model on SiliconFlow instead (see `references/siliconflow-vl-models.md`).
- **Web search** → Tavily (dedicated search API)
- **Large-parameter / overseas model** → OpenRouter free models only

### 2. Verify All Providers (Ping)
Use a single Python script to ping all configured providers in parallel (see `scripts/ping-all-providers.py`).

### 3. Register a New Provider
1. Update memory with the API key, base URL, and constraints
2. Add a reference file under `references/` with endpoint details and quirks
3. Run the ping script to verify

## Memory Management

Memory (`tool memory`) is limited to ~2,200 chars. When registering providers:

1. **Check usage first** — memory entries show `usage: X%/2,200`
2. **Consolidate before adding** — merge related entries (e.g., merge two SiliconFlow entries into one concise line)
3. **Delete stale entries** — use `memory(action='remove', old_text='unique substring')`
4. **Keep it compact** — API keys can be truncated (`sk-koy...`) unless the full key is needed for a specific task

After any memory consolidation, ping all providers again to confirm nothing broke.

## Tavily for Automated News Collection

### Verification Gate (铁律 — must verify BEFORE delivery)

Whenever you create, update, or modify any script, cron job, file, or configuration under this skill, **you must run it immediately to verify it works before presenting to the user.** 

Verification checklist (run all applicable items):
1. **Script exists** — `ls -la` the file path
2. **Syntax check** — `python3 -c "py_compile.compile('path', doraise=True); print('OK')"`
3. **Test execution** — Run it with a short timeout, capture output
4. **Output file** — Confirm the output file was created/updated, check its date is current
5. **Cron job** — Confirm `enabled: true`, check `next_run_at` is reasonable, and **run a manual test** — do NOT rely on `cronjob(action='run')` setting `last_run_at`, because `last_run_at` stays `null` until the scheduler actually fires. Instead, poll the output file to confirm it was written.

Do NOT tell the user the job is complete until all checks pass. The user explicitly requires self-verification — errors found by the user after delivery are unacceptable. This was enforced after a cron job was reported as "fixed" but had never actually run.

Tavily can be used as the backend for a daily news briefing cron job.

### Preferred Approach: Script Mode (no_agent)

**Do NOT use LLM-agent mode (`deliver: "local"` with a text prompt).** Cron jobs in agent mode (`no_agent: false`) have been observed to never execute — `last_run_at` stays `null` indefinitely and no file is produced.

Instead, use `no_agent: true` with the `script:` parameter:

1. Copy `scripts/fetch-daily-news.py` to `~/.hermes/scripts/` (the cronjob tool only accepts scripts under this path):
   ```
   cp /opt/data/skills/devops/provider-gateway/scripts/fetch-daily-news.py ~/.hermes/scripts/
   ```
2. Create the cron job:
   ```
   cronjob(action='create', name='每日国际新闻晨报', schedule='22 0 * * *',
           no_agent=True, script='fetch-daily-news.py')
   ```
3. The script searches Tavily for 5 categories (economy, tech, battery/energy, materials, job market), saves to `/opt/data/青桑/每日新闻简报.txt`

### Integration with Morning Briefing

When user says "hi":
1. `session_search` to recall yesterday's work
2. Read `/opt/data/青桑/每日新闻简报.txt` for international news
3. Combine into morning briefing

### Catch-Up Delivery (隔N天发N天)

When the user returns after multiple days without saying "hi" (detected via `session_search` — check the most recent session's date):

1. **Identify the gap**: Find the last session date vs today. If 2+ days gap, proceed.
2. **Check archived briefs**: Look for `每日新闻简报_YYYY-MM-DD.txt` files for each missing date:
   ```bash
   ls /opt/data/青桑/每日新闻简报_*.txt | sort
   ```
3. **Fill missing dates**: For any missing date, manually run `fetch-daily-news.py` (the script creates dated archives when it runs). Note: Tavily searches for "today's news" — retroactive searches for past dates won't reflect what was happening that day accurately, but provide the best available approximation.
4. **Present chronologically**: Deliver news in date order, oldest first. Label each day clearly: `=== 📅 5月8日 简报 ===`

### Dated Archive Mechanism

The script now saves TWO files:
- `每日新闻简报.txt` — always the latest (overwritten each run)
- `每日新闻简报_YYYY-MM-DD.txt` — dated copy (never overwritten, `if not os.path.exists()` guard)

This allows the catch-up mechanism to work across multiple days.

### News Brief Format (用户确认的三要素)

每条新闻必须包含以下三项，缺一不可：
1. **🔗 原文链接** — 从 Tavily 结果的 `url` 字段提取，直接输出
2. **📝 核心要点摘要** — 清理后的内容截取前 300 字符，突出关键信息
3. **按重要性排序** — 同一类别内，重要新闻排前面（基于内容判断：政策/重大事件优先于常规更新）

脚本 `fetch-daily-news.py` 已内置此格式，输出样例：
```
▪ Global markets weekly update | T. Rowe Price
  🔗 https://www.troweprice.com/...
  📝 Ahead of the planned May 14–15 meeting between Trump and Xi Jinping in Beijing...
```

### Script Configuration (fetch-daily-news.py)

Current categories (no job/recruitment):
1. 国际经济 — `major international economic news markets trade policy today this week`
2. 前沿科技 — `latest technology news AI semiconductor breakthrough innovation this week`
3. 新能源电池 — `battery electrolyte lithium metal solid state battery new energy vehicle news this week`
4. 新材料 — `new materials science research breakthrough graphene polymer composite this week`
5. 国内产业 — `中国新能源电池新材料产业政策 market dynamics lithium battery 2026`

Each category returns 6 results with `include_answer: True` (Tavily generates a summary overview per category). Content snippets are cleaned via `clean_text()` (strips markdown headings, HTML tags, navigation text) and truncated to 500 characters. Search depth is `advanced`.

If the user asks to adjust categories, result count, or content length, edit the script's `CATEGORIES` dict, `max_results` parameter, or the `[:500]` truncation in the `main()` loop.

## Related Infrastructure

In addition to API providers, the user may have proxy infrastructure deployed (e.g., mihomo for external network access). See `container-network-proxy` skill for proxy deployment in restricted containers.

## Pitfalls

- **Current model does NOT support vision** — `DeepSeek-V4-Flash` (and most text-only models) reject `image_url` in messages with error `unknown variant 'image_url'`. For image analysis, route to a dedicated VL model on SiliconFlow (see `references/siliconflow-vl-models.md`) or use free alternatives (see `references/free-vision-alternatives.md`).

### SenseNova Two-Platform Trap

When the user says they registered for SenseNova but the API returns 401:

1. **They may be on the wrong platform.** 商汤 has two separate API systems:
   - `platform.sensenova.cn` (Token Plan) → `sk-` API key, endpoint `token.sensenova.cn/v1`
   - `console.sensecore.cn` (SenseCore) → AccessKey ID + Secret, endpoint `api.sensenova.cn/v1/llm/`
2. **API key alone is not enough.** Even on the correct platform, the Token Plan must be **manually activated** in the console. Without activation, the key returns 401 `code: 16 Forbidden`.
3. **The user's env var convention** (from Amaranth Wiki) is `SN_API_KEY`, not `SENSENOVA_API_KEY`.
4. **Do NOT redirect platforms.** If the user has a `sk-` key but is on `console.sensecore.cn`, guide them back to `platform.sensenova.cn` to activate the Token Plan.
5. **"我按wiki操作的"** — verify they followed: sensenova.cn/token-plan → 免费开始 → 管理中心 → API Key 管理.

### API Key Testing with Secret Redaction

When testing API keys, the Hermes secret redaction system (`security.redact_secrets: true`) will corrupt any file or shell command that contains the key value inline. To work around this:

**Correct pattern** — read key from .env at runtime, build header via concatenation:
```
import subprocess
key = ""
with open("/opt/data/.env") as f:
    for line in f:
        if line.startswith("SN_API_KEY=...");
            key = line.strip().split("=", 1)[1]
            break
result = subprocess.run(["curl", "-s", "https://token.sensenova.cn/v1/models",
    "-H", "Authorization: Bearer " + key],
    capture_output=True, text=True, timeout=15)
```

**Broken patterns** that get corrupted by the redaction system:
- f-strings containing the key variable inline
- Inline key values in string literals (redaction replaces them, breaking string terminators)
- Shell pipelines with key values in subshell expansions

- **OpenRouter free models** return HTTP 429 under load (rate limiting). Retry with backoff. Do NOT call paid models.
- **OpenRouter free models list** (only these 4):
  - `nousresearch/hermes-3-llama-3.1-405b:free` — ❌ consistently 429
  - `meta-llama/llama-3.3-70b-instruct:free` — ❌ consistently 429
  - `minimax/minimax-m2.5:free` — ✅ **most stable, sometimes works** (~2500ms)
  - `qwen/qwen3-coder:free` — ❌ consistently 429
- **OpenRouter availability pattern**: minimax-m2.5 is the only free model that recovers from 429. The other 3 have been blocked across multiple test sessions. If a task needs an overseas model, try minimax-m2.5 first.
- **SiliconFlow** uses `curl` for image gen (Hermes built-in `image_generate` is hardcoded to FAL, not SiliconFlow)
- **No pip/root/apt-get** in container — use stdlib (urllib, json) for API calls
- All generated files go to `/opt/data/青桑/`
- **Cron jobs in agent mode (`no_agent: false`) may silently fail to execute** — `last_run_at` stays `null` and no output is produced. Always use `no_agent: true` with a `script:` for scheduled tasks that write to files.
### Cron job script path restriction — scripts must reside in `~/.hermes/scripts/`. A relative filename (e.g., `fetch-daily-news.py`) is resolved relative to that directory. Absolute paths are rejected. If no_agent+script mode consistently fails to execute, create a regular agent-mode cron instead (`no_agent: false`/omit field) with a prompt like `"执行 fetch-daily-news.py 脚本来获取今天的新闻并更新每日新闻简报文件。"` — the agent will run the script via terminal on trigger.

### News brief date check (required)
When presenting the daily news brief, ALWAYS check the file's date before reading it. The brief file may be stale (generated days ago). Steps:
1. Run `head -1 /opt/data/青桑/每日新闻简报.txt` to get the date line (`=== 每日新闻简报 | YYYY-MM-DD ===`)
2. Parse the date using `date -d "YYYY-MM-DD" +%s` and compare to today's date
3. If the brief is from 2+ days ago, first manually run the script, then read the fresh output
4. Only present the brief if it's from today or yesterday

This prevents user frustration from stale news — they get annoyed when seeing old data.
- **`cronjob(action='run')` is not synchronous** — calling `run` updates `next_run_at` immediately but `last_run_at` remains `null` until the scheduler processes the run. Poll the output file to verify completion; do not rely on `last_run_at` in the response.
- **`fetch-daily-news.py` has a hardcoded Tavily API key** — if the user rotates their Tavily key, this script must be updated before the next cron run or it will fail silently.

## Daily News Briefing — Presentation & Verification Rules

This section consolidates the presentation rules for the daily news briefing. The fetch script lives at `scripts/fetch-daily-news.py`; these rules govern how the agent formats and verifies output before delivering to the user.

### 0. Hard Rule: NEVER truncate URLs

NEVER shorten, abbreviate, or add `...` to any URL. Copy URLs directly from the source archive file. This has been explicitly corrected and is non-negotiable.

### RULE 1: Self-verification before delivery (MANDATORY)

Before presenting ANY news to the user, verify:
- File date matches today (or correct catch-up date if backfilling)
- Every URL is COMPLETE (no `...` truncation)
- Cron job status verified (check `last_run_at` / `next_run_at`); if stale, run script manually
- Each news item has: 🔗 link + 📝 summary
- News ordered by importance (most important first)

**If the file is stale (date != today), run the script immediately rather than reporting stale data.**

### RULE 2: Holiday info format

The briefing includes a "today's special day" line. Format: plain line with flag icons, no header:
```
   🇨🇳 母亲节  |  🌍 International Day of Argania, Mother's Day
```

**CRITICAL: Do NOT add a "📅 今天是什么日子" header line.** The holidays are sourced from a lookup table in `fetch-daily-news.py` (~150 entries) plus floating-date detection (Mother's Day 2nd Sunday May, Father's Day 3rd Sunday June, Thanksgiving 4th Thursday November).

### 3. News item format —三条必备

每条新闻必须包含：
1. 🔗 **原文链接** — 从存档文件原文复制，完整URL，不加省略号
2. 📝 **核心要点摘要** — 提炼关键信息，不复制大段原文
3. 按**重要性排序**，重要新闻在前

### 4. Catch-up delivery (隔N天发N天)

When user returns after multiple days:
1. Check last active date from `session_search`
2. List which dates are missing between last active and today
3. For each missing date, check if `每日新闻简报_YYYY-MM-DD.txt` exists in archives
4. If missing, run `python3 /opt/data/skills/devops/provider-gateway/scripts/fetch-daily-news.py` to generate it (note: the script only generates today's brief, retroactive searches approximate past news)
5. Present all missed briefs in chronological order

### Verification Checklist (run before presenting)

- [ ] File exists at expected path
- [ ] File date matches today (or correct catch-up date)
- [ ] All URLs in the output are complete (grep for `...` or truncated patterns)
- [ ] Cron job is enabled and has a valid next_run_at
- [ ] Each news item has: 🔗 link + 📝 summary
- [ ] News are ordered by importance

### Archive file format

The script saves two files:
- `每日新闻简报.txt` — always the latest (overwritten each run)
- `每日新闻简报_YYYY-MM-DD.txt` — dated copy (never overwritten, `if not os.path.exists()` guard)

This enables catch-up delivery across multiple days.

## Image Generation & Vision Analysis via SiliconFlow

This section covers SiliconFlow-specific image generation and vision-language (VL) analysis workflows. SiliconFlow is the primary image gen provider for this environment.

### Image Generation API
### Image Analysis / Vision (VL)

**First choice:** SiliconFlow VL models (see `references/siliconflow-vl-models.md`).

**Fallback options (free, no SiliconFlow key needed):** See `references/free-vision-alternatives.md` for:
- **Agnes AI** — permanently free, supports **vision** (`agnes-2.0-flash`), **image generation** (`agnes-image-2.1-flash`), and **video generation** (`agnes-video-v2.0`). OpenAI-compatible. ⚠️ Requires proxy in China (Cloudflare CDN blocked by GFW). Full details + proxy setup in the reference file.
- **SenseNova 6.7 Flash-Lite** — 1500 calls / 5 hours free from 商汤 Token Plan. Full provider details in `references/sensenova.md` (including activation requirement — API key alone is not sufficient; Token Plan must be activated on platform.sensenova.cn).

**Recommended vision pipeline (from Amaranth Wiki):**
```
Primary:   SiliconFlow Qwen3-VL (via SILICONFLOW_KEY)
Fallback:  SenseNova 6.7 Flash-Lite (free, native multimodal)
Last:      EasyOCR (local, zero-cost offline)
```

### SenseNova Skills (26 free skills from OpenSenseNova)

50+ free office automation skills from [OpenSenseNova/SenseNova-Skills](https://github.com/OpenSenseNova/SenseNova-Skills), installed to `~/.hermes/skills/sensenova/`:

| Skill Type | Skills | Use Case |
|------------|--------|----------|
| Image gen | sn-image-base, sn-infographic (87×66 layouts), sn-image-imitate, sn-image-resume | Infographics, image generation |
| PPT | sn-ppt-entry, sn-ppt-standard, sn-ppt-creative, sn-ppt-doctor | PowerPoint generation |
| Data analysis | sn-da-excel-workflow, sn-da-image-caption, sn-da-large-file-analysis, sn-da-non-spreadsheet-analysis | Excel/CSV data processing |
| Research | sn-deep-research, sn-dimension-research, sn-research-planning, sn-research-report, sn-research-synthesis | Multi-source deep research |
| Search | sn-search-academic, sn-search-code, sn-search-image, sn-search-social-cn, sn-search-social-en | Specialized search tools |
| Other | sn-md-to-html-report, sn-report-format-discovery, sn-update, sn-image-doctor | Format conversion, updates |

**Core dependency**: `sn-image-base` (tier 0) provides underlying tools: `sn-image-generate`, `sn-image-recognize` (VLM), `sn-text-optimize` (LLM).

**Installation** (requires GitHub access):
```bash
git clone https://github.com/OpenSenseNova/SenseNova-Skills.git --depth=1
cp -r SenseNova-Skills/skills/* ~/.hermes/skills/sensenova/
```

Skills are auto-discovered by Hermes from the `skills/` directory. Use `/skill <name>` to load a skill in session.

**Note**: The SenseNova skills are optimized for SenseNova models. Using them with other models may produce lower quality results (especially sn-infographic layout generation).

SiliconFlow VL call format:

```bash
curl -s https://api.siliconflow.cn/v1/chat/completions \
  -H "Authorization: Bearer $SILIC...EY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen-Image",
    "prompt": "your prompt here",
    "n": 1,
    "size": "1024x1024"
  }'
```

**Note**: The `image_generate` tool in Hermes is hardcoded to FAL backend, NOT SiliconFlow. Use `curl` directly.

### Available Image Gen Models

| Model | Speed | Best For |
|-------|-------|----------|
| `Qwen/Qwen-Image` | ~10-14s | Academic/scientific figures, infographics, text rendering |
| `Qwen/Qwen-Image-Edit` | — | Image editing/inpainting |
| `Tongyi-MAI/Z-Image` | — | General generation |
| `Tongyi-MAI/Z-Image-Turbo` | ~2.5s | Fast prototyping, lower quality |
| `baidu/ERNIE-Image-Turbo` | — | Alternative |
| `Kwai-Kolors/Kolors` | ~3-4s | Artistic/creative concepts (poor at text/infographics) |

### Iterative Refinement Workflow

Academic/science users typically iterate on image results. Pattern:

1. **Generate first draft** with user's exact prompt
2. **Show all generated files** with model name, timing, and size
3. **Listen for style feedback**:

| User says | Meaning | Fix |
|-----------|---------|-----|
| "太艺术了 / 不是这个风格" | Too creative | Switch to Qwen-Image, add "scientific illustration, clean technical lines, minimalist" |
| "学术一点 / 期刊风格" | Need publication-ready | Add "academic journal style figure, white background, publication-ready, Nature/ACS journal quality" |
| "太丑 / 不行" | Reject entirely | Change model AND prompt style simultaneously |
| "都不行" (all rejected) | Deep rejection | Stop generating blindly. Ask for specific style reference: Nature, ACS, or general academic white bg |
| "给我看一下" / multiple versions | Compare options | Generate 2-3 variants, organize into table, ask for feedback |
| "不够专业" | Needs cleaner lines | Add "professional dashboard feel, minimalist data visualization, clean lines" |
| "文字不对" | Wrong labels | Shorten text labels (1-3 words) — models render short labels best |
| "颜色不对" | Wrong color scheme | Explicitly specify colors: "blue and teal color scheme", "dark/white background" |

4. **Adjust prompt** based on feedback and regenerate
5. **Try different model** if prompt adjustments alone don't help
6. **Tag output files** with model name in filename to track versions

### Model Selection Guide for Academic Use

| Use Case | Best Model | Why |
|----------|-----------|-----|
| Academic/scientific figures | Qwen-Image | Best detail, handles structured layouts |
| Quick iteration / prototyping | Z-Image-Turbo | Fastest turnaround |
| Artistic/conceptual illustrations | Kolors | Creative style |
| Infographics with text | Qwen-Image | Best text rendering |
| Image editing / inpainting | Qwen-Image-Edit | Purpose-built |

**Output directory**: All generated files go to `/opt/data/青桑/`.

### Academic/Scientific Prompt Templates

**Style anchor words** — decisive for output quality:

| Desired Style | Must-include words |
|---------------|-------------------|
| Nature journal | `Nature journal Figure 1 style. White background, Nature journal figure formatting, clean Helvetica font, professional blue and teal colors, minimalist scientific illustration, publication-quality.` |
| ACS journal | `ACS journal Graphical Abstract style. ACS journal style, white background, clean Arial font, blue and teal ACS color palette, crisp lines, professional chemistry materials science journal figure, minimal text.` |
| General academic | `Academic journal style figure. Clean white background, scientific illustration, blue and teal professional color scheme, clean technical lines, minimal text, research journal quality.` |
| Blank/simple | `Simple side-by-side comparison. White background, clean lines, minimal labels.` |

**Proven template** (battery energy density comparison):
```
{journal_style} Side-by-side comparison diagram of battery energy density.
Left panel: Traditional System, graphite anode + NCM cathode,
  schematic of cylindrical 18650 cell with labeled layers Graphite and NCM,
  bar chart at 250 Wh/kg.
Right panel: Advanced System, lithium metal anode + LRMO cathode,
  schematic of pouch cell with labeled layers Lithium Metal and LRMO,
  taller glowing bar chart at 450+ Wh/kg.
Center arrow with Energy Density Enhancement label.
{style_elements}
```

### Account Balance Management

SiliconFlow returns `{"code":30001,"message":"Sorry, your account balance is insufficient"}` when credits run out. Each Qwen-Image call costs ~1-2 CNY. After 4-5 successful generations, balance depletion is likely. Tell the user clearly: "硅基流动余额用完了，第 N 张没调通。你可以给这个 Key 续费，或者换另一个 Key 继续。"

### ASR (Audio Transcription) via SiliconFlow

SiliconFlow supports OpenAI-compatible audio transcription at `POST https://api.siliconflow.cn/v1/audio/transcriptions`. Uses the same `$SILICONFLOW_KEY`.

| Model | Accuracy | Speed | Best For |
|-------|----------|-------|----------|
| `TeleAI/TeleSpeechASR` | Highest | ~30s/8min audio | Chinese academic/technical speech, domain terminology |
| `FunAudioLLM/SenseVoiceSmall` | Good | Faster | General-purpose, fallback |

**Basic usage:**
```bash
curl -s -X POST "https://api.siliconflow.cn/v1/audio/transcriptions" \
  -H "Authorization: Bearer $SILICONFLOW_KEY" \
  -F "file=@/path/to/audio.m4a" \
  -F "model=TeleAI/TeleSpeechASR" \
  -F "language=zh" \
  -F "response_format=json"
```

**Pre-processing long recordings with ffmpeg:**
```bash
# Check duration
ffprobe /path/to/audio.m4a 2>&1 | grep Duration

# Extract specific segment (e.g. second half from 9:00)
ffmpeg -y -ss 00:09:00 -i /path/to/audio.m4a -c copy /path/to/output.m4a
```

See `references/siliconflow-asr.md` for full API reference, parameters, file format support, and known working configurations.

### ASR Mode Decision: Verbatim vs Structured

**Critical rule: Never assume which mode the user wants.** The user has explicitly stated: "以后我没要求你做的你不需要自己脑补" — do not assume intent. Always confirm before processing.

**Mode A: Verbatim / Raw Transcription (原封不动)**

When user says "原封不动" or "逐字转写" or "不要加工":
1. Run the ASR API call and capture raw text output
2. Save directly with minimal frontmatter
3. Do NOT attempt speaker separation, punctuation insertion, or content structuring
4. Note ASR errors for domain terminology are expected — do NOT "fix" unless asked

**Mode B: Structured / Post-Processed (问答提取)**

When user asks for "问答提取" or "总结" or "提炼":
1. Read raw transcript, identify speaker turns from semantic cues (questions → rising intonation, "这个...", "那..."; answers → "因为...", "就是...")
2. Extract Q&A pairs grouped by topic
3. Clean text, fix known ASR errors for domain terms
4. Write structured markdown with Q&A pairs and summary

See `references/audio-transcription-siliconflow-qa.md` for known ASR error table and Q&A extraction methodology.

#### Audio Preprocessing for ASR

Convert to 16kHz mono MP3 for ASR APIs:
```bash
ffmpeg -y -i input.m4a -ar 16000 -ac 1 -b:a 32k /tmp/audio_for_asr.mp3
```

- `-ar 16000`: 16kHz sample rate (Whisper's native rate)
- `-ac 1`: mono channel
- `-b:a 32k`: ~32kbps bitrate keeps ~2MB for 8-minute audio

For lossless WAV:
```bash
ffmpeg -y -i input.m4a -ar 16000 -ac 1 -c:a pcm_s16le /tmp/audio_for_asr.wav
```

File size limits: Most ASR APIs have a 25MB limit. 8 min of 32kbps MP3 ≈ 2MB.
For longer files (>30min), split with:
```bash
ffmpeg -y -ss 00:09:00 -i input.m4a -c copy /tmp/output_segment.m4a
```

### Route an ASR Request

1. Check file exists and format with `ls -lh` + `ffprobe`
2. Ask user: verbatim (原封不动) or structured (问答提取)? — do NOT skip this step
3. If partial transcription needed, split with ffmpeg (use `-c copy` for fast extraction)
4. Convert to 16kHz mono MP3 for optimal ASR quality
5. POST to SiliconFlow `/v1/audio/transcriptions` with multipart form data
6. Process output per the confirmed mode above

### Fallback Strategies (No API Key Available)

When `$SILICONFLOW_KEY` is unset AND no other image gen API is configured:

**Fallback A — OCR via tesseract.js (Node.js)**
1. Install: `cd /opt/data/青桑/photo && npm install tesseract.js`
2. Run: `Tesseract.recognize('input.png', 'chi_sim+eng')`
3. Pitfalls: Accuracy varies with image quality; small fonts produce noisy output; Chinese ~70-85% on clean screenshots

**Fallback B — HTML/CSS + Puppeteer infographic rendering**
1. Install Puppeteer: `npm install puppeteer`
2. Create HTML with inline CSS (dark background `#0f1729`, gradient bars, glass-morphism cards)
3. Screenshot with headless Chrome:
   ```js
   const puppeteer = require('puppeteer');
   const browser = await puppeteer.launch({
     headless: 'new',
     args: ['--no-sandbox', '--disable-setuid-sandbox']
   });
   const page = await browser.newPage();
   await page.setViewport({ width: 1280, height: 780 });
   await page.goto('file:///path/to/file.html', { waitUntil: 'networkidle0', timeout: 30000 });
   await page.screenshot({ path: 'output.png', type: 'png', fullPage: true });
   await browser.close();
   ```
4. Save both `.html` source and `.png` screenshot
5. Pitfalls: `--no-sandbox` mandatory in container; `headless: 'new'` required; set timeout >= 30s

## Related Skills

- `container-network-proxy` — proxy deployment for reaching overseas providers from restricted containers
- `academic-writing` — academic thesis/paper writing support (translation, battery data interpretation, defense speech)

---

## Section N: Article Extraction from URLs (absorbed from `web-content` skill)

This section documents curl-based web content extraction patterns used during per-link news summary processing.

### Core Workflow

When extracting content from a URL:

1. **Extract text** using `curl -sL <URL> | python3` regex extraction
2. **Strip `<script>` and `<style>`** blocks first
3. **Extract `<p>` tags** for article text, or try `<div class="content">` etc.
4. **Clean HTML entities** and whitespace
5. **Summarize as a paragraph**, not bullet points — user preference: "不分点，总结成一段话"

### Article Extraction Patterns

Basic template for most news/science sites:

```bash
curl -sL "<URL>" | python3 -c "
import sys, re
html = sys.stdin.read()
html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
texts = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
for t in texts:
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\\s+', ' ', t).strip()
    if len(t) > 40:
        print(t)
"
```

For ScienceDaily-style articles (h1–h3 + p):
```python
texts = re.findall(r'<(?:p|h[1-3])[^>]*>(.*?)</(?:p|h[1-3])>', html, re.DOTALL)
```

For Chinese news sites with rich text:
- Try `<div class="content">`, `<div class="article">`, or `<section>` wrappers
- Many Chinese sites render server-side, so curl often works directly

### Known Anti-Scraping Sites (one attempt only, then skip)

| Site | Protection | Action |
|------|-----------|--------|
| reuters.com | DataDome | Skip; use Google News RSS fallback |
| bloomberg.com | Paywall + DataDome | Skip; use Google News RSS fallback |
| ft.com | Soft paywall | One curl try; then Google News RSS |
| sciencedirect.com | CAPTCHA + paywall | One try, then skip — no API workarounds |
| link.springer.com | CAPTCHA | One try, then skip |
| insideevs.com | AWS WAF | Skip immediately |
| programming-helper.com | Vercel checkpoint | Skip (always 429) |

### Reliable Sites (curl works)

livescience.com, sciencedaily.com, electrek.co, interestingengineering.com, eurekalert.org, cnbc.com, sina.com.cn, qianzhan.com, huaon.com, dshnewenergy.com, openpr.com, azonano.com, bbc.com/news, deloitte.com/insights

### When curl Fails

- **LinkedIn articles** — login-gated, report as such
- **YouTube links** — mark as 🎬 and provide link only
- **Aggregator/feed pages** (CNBC World Economy, Trading Economics, TechCrunch category pages) — label as feed page and provide link
- **PDF links** — use `pymupdf` or Python `pdfminer`

### Delegate Task Instructions for Sub-agents

When dispatching per-link reading via `delegate_task`, include this instruction to prevent tool-call wastage:

> "For sites known to block scraping (Reuters, Bloomberg, FT, ScienceDirect, Springer, InsideEVs, Vercel-hosted), make ONE curl attempt only. If blocked, skip immediately. Do not try workarounds (different User-Agents, proxies, Wayback Machine, Google cache, textise, CORS proxies)."

See `references/article-extraction-recipes.md` for per-site extraction recipes and `references/anti-scraping-sites.md` for full blocking-site table with fallback strategies.

---

## Section O: Daily News Briefing — Delivery Workflow (absorbed from `daily-news-briefing` skill)

This section covers the user-facing delivery workflow for daily news briefings fetched via Tavily. The fetch infrastructure is in Section L above; this section governs what to present and how.

### ⚠️ MANDATORY — First-Response Rule

**When the user says "hi", "你好", "早", "早上好", or any greeting, you MUST load this skill and deliver the news as the very first response.** Do not respond with a greeting back. Do not check balances first (do that silently). The greeting in this context means "give me my news," not "start a conversation."

### Two-Stage Delivery (BOTH Mandatory)

**Stage 1 — Briefing Overview**: Concise summary of all 5 categories with highlights.

**Stage 2 — Per-Link Chinese Summaries**: Process EVERY SINGLE link (~30 total) with a detailed Chinese summary. All links must be processed.

### Per-Link Processing Strategy

1. Use `delegate_task` in batches of 3 (parallel, system concurrency limit)
2. Each task reads one URL via curl and returns a Chinese paragraph summary
3. Collect results and present grouped by category

### Presentation Format

**Per-Item:**
```markdown
[Paragraph summary covering what was done + key result + significance]
🔗 [full URL — NEVER truncate with ...]
```

**Category Grouping**: Start each category with `── [name] ──`

**Summary Style**: One coherent paragraph (not bullet points, not numbered items). Cover what was done, key finding, and significance. 200–500 characters.

**Items numbered CONTINUOUSLY** across all categories, not per-category. Item 1 starts in 国际经济, then continues through 前沿科技, 新能源电池, etc.

### English Abbreviation Rule

Every English abbreviation in the briefing MUST have Chinese annotation on its first occurrence in the document. Format: `缩写（中文全称）`

Essential reference:
- CPI（消费者物价指数）, PPI（生产者价格指数）
- GDP（国内生产总值）, IMF（国际货币基金组织）
- EV（电动汽车）, LIB（锂离子电池）
- LFP（磷酸铁锂）, NMC（镍钴锰三元）
- RGO（还原氧化石墨烯）
- USMCA（美墨加协定）, CSIS（战略与国际研究中心）
- IEA（国际能源署）, SMM（上海有色网）
- MTIA（Meta训练与推理加速器）
- Wh/kg（瓦时每千克）, GWh（吉瓦时）
- CAGR（年复合增长率）

### Category Order (fixed)

1. 国际经济 — major international economic news, markets, trade, policy
2. 前沿科技 — AI, semiconductor, tech breakthroughs
3. 新能源电池 — battery, electrolyte, lithium, solid-state, EV
4. 新材料 — graphene, polymer, composite, new materials
5. 国内产业 — 中国新能源电池、新材料产业政策、市场动态

### Failed Extraction Handling

- Note the reason (paywall/CAPTCHA/AWS WAF)
- Try Google News RSS fallback for Reuters/Bloomberg/FT
- Provide the full URL so user can open manually
- Do NOT fabricate content

### ⚠️ Subagent URL Reading Reliability — Mitigation Patterns

Delegating per-link article reading to `delegate_task` subagents has observed failure modes, **but can be made reliable with correct toolset configuration**.

#### Root Cause

The primary cause of subagent failure is **toolset selection**. Subagents without `terminal` in their `toolsets` will try tools like `web_read` or `web_fetch` that don't exist in the subagent context, causing them to output raw XML or empty results.

#### Observed Failure Modes

1. **Subagent outputs raw tool-call XML** instead of content — common when subagents lack the `terminal` toolset.
2. **Subagent outputs reasoning chain instead of summary** — common on complex HTML pages when no extraction tool is available.
3. **Subagent fabricates a generic summary** — sounds plausible but unrelated to actual article content.
4. **Subagent never runs** — task times out or returns empty.

#### ✅ Mitigation: Use `toolsets=["terminal","web"]`

**This session demonstrated that subagents with `toolsets=["terminal","web"]` successfully extract content from ~18 links reliably.** The key pattern:

```json
{"context":"Article URL: https://example.com/article
Read the full content with curl and Python text extraction, then summarize in Chinese.","goal":"Read this article in full and summarize it in 200-500 Chinese characters. Include the full original URL.","toolsets":["terminal","web"]}
```

The `terminal` toolset gives subagents access to `curl` + Python for HTML extraction. The `web` toolset provides search fallback.

#### Subagent Extraction Template

When dispatching a per-link reading task, include this pattern in the context:

```
Read with curl+Python extraction, summarize in 200-500 Chinese characters.
```

The subagent will use this pattern:
```bash
curl -sL "<URL>" | python3 -c "
import sys, re
html = sys.stdin.read()
html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
texts = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
for t in texts:
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\\\\s+', ' ', t).strip()
    if len(t) > 40:
        print(t)
"
```

#### Special Cases

- **JSON-LD embedded content** (e.g., flashbattery.tech): Subagents can extract `articleBody` from `<script type="application/ld+json">` blocks.
- **BBC articles from category pages**: The category URL (e.g., `/news/business/economy`) is a feed page. The subagent should find the actual article URL from the feed and read it directly. The actual BBC article URL looks like `/news/articles/{id}`.
- **Paywalled sites** (ieknet.iek.org.tw): Subagents should report paywall and summarize public metadata only.

#### When to Skip Delegation

Some sites remain unreliable even with correct toolset configuration:
- **CSIS (csis.org)** — subagent returns raw tool-call XML regardless of toolset. Read in main thread.
- **Patsnap (eureka.patsnap.com)** — same issue. Read in main thread.
- **T. Rowe Price** — subagent fabricates unrelated summaries. Read in main thread.

These are documented in `references/anti-scraping-sites.md` under the "Subagent-Unfriendly Sites" section.

#### Batch Size

The system concurrency limit is `max_concurrent_children: 3`. Batch tasks in groups of 3. For ~18 links, expect ~6 batches = ~50-90s total (dominated by slow sites at ~20-30s each).

### Type Icons for Non-Readable Links
- 🎬 = YouTube/video
- 📄 = PDF download
- 🔒 = Login/paywall gated
- No icon = aggregator/feed page (note in text)

### Catch-Up Delivery (隔N天发N天)

When user returns after multiple days:
1. Check last active date from `session_search`
2. List missing dates between last active and today
3. For each missing date, check if `每日新闻简报_YYYY-MM-DD.txt` exists in archives
4. If missing, run the fetch script to generate it
5. Present all missed briefs in chronological order, oldest first, labeled `=== 📅 5月8日 简报 ===`

### What NOT to Do
- ❌ Don't re-run fetch-daily-news.py after first successful run — results will differ
- ❌ Don't truncate URLs with `...` (hard rule, previously corrected)
- ❌ Don't use bullet points for individual article summaries
- ❌ Don't fabricate content from failed extractions
- ❌ Don't present only the overview and stop — process ALL links
- ❌ Don't waste tool calls on known-blocking sites
- ❌ Don't respond with a greeting — deliver news immediately
- ❌ Don't add a "📅 今天是什么日子" header to the holiday line
- ❌ Don't link to category/feed pages (BBC `/news/business/economy`, Reuters `/technology`, FT `/semiconductors`) — find the actual article URL instead. Category pages change daily and provide no stable content.
- ❌ Don't delegate CSIS, Patsnap, or T. Rowe Price to subagents — read these in the main thread

See `references/daily-digest-format-example.md` for abstract format template.
See `references/daily-digest-real-output-example.md` for a concrete real-world corrected output.
See `references/anti-scraping-sites.md` for the full blocking-site table and `references/article-extraction-recipes.md` for per-site extraction patterns.
