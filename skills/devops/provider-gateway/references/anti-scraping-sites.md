# Known Anti-Scraping Sites (Daily News Briefing)

These sites block non-browser HTTP clients. **Do not** retry more than once — consumed tool calls are invisible to the user and waste time.

## ⚠️ Tool-Call Wastage Warning (Critical for delegate_task sub-agents)

Sub-agents do not have access to this skill. When dispatching a delegate_task for a known-blocking site, include explicit instructions in the task context:

> "One curl attempt only. If blocked, skip immediately with a note. Do not try alternate User-Agents, proxies, Wayback Machine, Google cache, textise proxies, or API workarounds."

**Observed wastage without this instruction:**
| Site | Tool Calls Wasted | Attempts Made |
|------|------------------|---------------|
| insideevs.com | ~25 calls, ~117s | direct curl, Google cache, Wayback, Jina AI reader, CORS proxy, Python urllib, Google News RSS |
| sciencedirect.com | ~45 calls, ~317s (hit max_iterations) | direct curl ×3 UA, CrossRef API, Semantic Scholar API, OpenAlex API, CORE API, Wayback, Google Scholar, PubMed, Elsevier API |
| bloomberg.com | ~30 calls, ~223s | direct curl ×3 UA, Google cache, Wayback ×2, outline.com, 12ft.io, archive.is, textise.iitty, Google News RSS, proxies |

**Conclusion**: Save ~25-45 tool calls per blocking site by giving the delegate the "one attempt only" rule explicitly.

## DataDome (CAPTCHA Challenge)

| Site | Behavior | Fallback Strategy |
|------|----------|-------------------|
| reuters.com | Returns JS challenge page (all sections: markets, tech, AI) | Google News RSS: `curl -s "https://news.google.com/rss/search?q=site:reuters.com+markets&hl=en-US&gl=US"` yields headlines + snippets. Works well. |
| bloomberg.com | Paywall + DataDome on article and video pages | Google News RSS: same pattern but with `site:bloomberg.com`. Title + context only; no full text. |
| ft.com | Soft paywall; partial content on direct curl | Google News RSS works best: `site:ft.com global economy`. One quick curl try first, then RSS. |
| insideevs.com | AWS WAF CAPTCHA | No bypass available. Skip immediately — one try, zero workarounds. |

## Vercel Security Checkpoint

| Site | Behavior | Notes |
|------|----------|-------|
| programming-helper.com | Returns HTTP 429 with JS challenge | Every request blocked. No workaround. |

## Science Publisher Paywalls

| Site | Behavior | Notes |
|------|----------|-------|
| sciencedirect.com | CAPTCHA + institutional login | Abstract only via DOI. One try then give up. Do NOT attempt API workarounds (CrossRef, Semantic Scholar, OpenAlex, CORE) — these will waste 30+ tool calls. |
| link.springer.com | CAPTCHA challenge | Occasionally works (one attempt succeeded for `s43939-026-00610-w`). One try only. |
| nature.com | CAPTCHA + paywall | Usually blocked. |

## Unreliable / Partial

| Site | Notes |
|------|-------|
| **cnbc.com** | JS-rendered article content — curl returns navigation HTML only. Not reliably readable. Skip or use Google News RSS fallback. |
| tradingeconomics.com | Real-time data table stream, not an article. Curl works but returns HTML tables + scrolling headlines. Summarize as: key market moves (FX, rates, commodities, equities). |
| semiconductors.org (SIA) | Curl works for top-level page but navigation links within the page may not resolve. Extract visible headlines from initial HTML. |
| ieknet.iek.org.tw (工研院IEK) | Paywalled — full report requires IEK membership login (~28-page PPTX). Public metadata only (title, author, overview, download count). Summarize from public section and note it's paywalled. |
| news.metal.com (上海有色网) | Curl works but returns enormous HTML (~80KB) with gzip-compression. Article content is in script JSON or deeply nested divs. Must use gzip.decompress fallback. Extract via `<p>` tags or `JSON.parse()` from inline JSON. |
| www.rbccm.com (RBC Capital Markets) | Curl works. Article content in `<p>` tags. Large page (50KB+). Extract with Python regex. |
| taxfoundation.org | Curl works. Clean HTML. Extract with Python regex on `<p>` and `<h2>` tags. |
| www.large-battery.com | Curl works. Clean article HTML in Chinese. Extract `<p>` tags directly. |
| www.flashbattery.tech | Curl works. Article content embedded in JSON-LD structured data (`<script type=\"application/ld+json\">`). Extract `articleBody` from JSON. |
| www.greencars.com | Curl works. Clean `<p>` tag extraction. |
| pmc.ncbi.nlm.nih.gov (PMC/NIH) | Curl works. Full academic article text available. Extract visible text body. |

## Subagent-Unfriendly Sites (curl works in main thread but fails when delegated)

| Site | Issue | Mitigation |
|------|-------|-----------|
| csis.org (CSIS) | Subagent returns raw tool-call XML instead of content. Main-thread curl works fine. | Read directly in main agent, do NOT delegate. |
| troweprice.com | Subagent fabricates generic summaries unrelated to actual page content. | Read directly in main agent. |
| eureka.patsnap.com | Subagent returns raw tool-call XML. | Read directly in main agent. |

## Reliable (curl Works — One Try Only)

All of the following return full article content with standard curl (no special headers needed):

| Site | Notes |
|------|-------|
| livescience.com | Battery, EV articles |
| sciencedaily.com | Science articles (memory chips, solid-state batteries, graphene) |
| electrek.co | EV/battery news |
| interestingengineering.com | Engineering breakthroughs |
| eurekalert.org | Press releases on research — may return empty (JS-rendered). One try only. |
| sina.com.cn / finance.sina.com.cn | Chinese finance (Sina Finance) |
| qianzhan.com | 前瞻产业研究院 reports |
| huaon.com | 华经情报网 market reports |
| dshnewenergy.com | Battery market analysis |
| openpr.com | Press releases |
| coaio.com | Tech news aggregator |
| azonano.com | Nanotechnology articles |
| deloitte.com | Weekly economic updates (no paywall on this specific insights page) |
| dfcfw.com (PDFs) | PDF downloads via curl; extract text from PDF binary |
| bbc.com/news | BBC business/economy |
| monolithai.com | Solid-state battery analysis |
| verifiedmarketreports.com | Market research reports |
| deloitte.com/insights | Economic analysis (no paywall) |
| **Fortune Business Insights** (fortune.com/fortune-insights) | Clean HTML, readable headers and market data paragraphs |
| **Mordor Intelligence** (mordorintelligence.com) | Clean HTML with market size, CAGR, and segmentation data |
| **Graphene Flagship** (graphene-flagship.eu) | Clean HTML with full article text |
| **Nanografi** (nanografi.com) | Decent HTML content about graphene materials |
| **RSC Publishing** (pubs.rsc.org) | Clean abstract text; full article may be behind paywall — abstract is usually enough |
| **MDPI** (mdpi.com) | Open access, full article text. Check date — may be old academic papers |
