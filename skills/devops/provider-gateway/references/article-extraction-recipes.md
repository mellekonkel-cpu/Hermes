# Article Extraction Recipes from 2026-05-13 Session

## ScienceDaily (static server-rendered)
Pattern: `<p>` and `<h1-h3>` tags, clean output.
```bash
curl -sL "https://www.sciencedaily.com/releases/2026/05/260502233908.htm" | \
python3 -c "
import sys, re
html = sys.stdin.read()
html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
texts = re.findall(r'<(?:p|h[1-3])[^>]*>(.*?)</(?:p|h[1-3])>', html, re.DOTALL)
for t in texts:
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > 40: print(t)
"
```

## LiveScience (static, rich article)
Pattern: `<p>` tags. Page has lots of sidebar/nav noise — still works because `<p>` tags are mostly article body.
```bash
curl -sL "https://www.livescience.com/technology/electric-vehicles/..." | \
python3 -c "
import sys, re
html = sys.stdin.read()
html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
texts = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
for t in texts:
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > 40: print(t)
"
```

## Inside Climate News (static, single-article layout)
Same `<p>` extraction works. Content is under generic divs.

## Coaio tech roundup (static blog post)
Same `<p>` extraction. Was able to read full article text despite modest styling.

## 前瞻产业研究院 (Chinese site, server-rendered)
Pattern: `<p>` and `<div class="*text*">` both work. Returns full Chinese article text with industry data and company names.

## 华经产业研究院 (Chinese site, server-rendered)
Pattern: `<p>` and `<h1-h6>` work. Returns complete Chinese market analysis.

## Sites that FAILED curl extraction (likely JS-rendered SPAs):
- **EurekAlert** (eurekalert.org) — returns empty, needs browser-based rendering
- **中国工业报** (cinn.cn) — returns empty, JS-dependent layout
- **LinkedIn** articles — login-gated, cannot scrape
- **Al Jazeera** (aljazeera.com/economy/) — returns empty, heavy JS

## Fallback strategy for failed extractions:
1. Summarize from the snippet/text that was captured in the Tavily-generated briefing file
2. Note honestly that the full page couldn't be read
3. Do NOT fabricate content

## Universal Extraction Pattern (with gzip fallback)

Some sites (e.g. SMM news.metal.com, some Chinese news sites) serve gzip-compressed HTML directly. Use this pattern with gzip.decompress fallback:

```python
import sys, re
data = sys.stdin.buffer.read()
try:
    import gzip; data = gzip.decompress(data)
except:
    pass
text = data.decode('utf-8', errors='replace')
text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'\\s+', ' ', text).strip()
print(text[:4000])
```

Key components:
- `gzip.decompress` fallback handles sites that serve compressed content
- Script/style removal first, then tag stripping, then whitespace normalization
- `[:4000]` limits output — adjust up if article is longer

For bash one-liner version:
```bash
curl -sL --max-time 20 "$URL" 2>/dev/null | python3 -c "
import sys, re
data = sys.stdin.buffer.read()
try:
    import gzip; data = gzip.decompress(data)
except: pass
text = data.decode('utf-8', errors='replace')
text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'\\s+', ' ', text).strip()
print(text[:4000])
"
```
