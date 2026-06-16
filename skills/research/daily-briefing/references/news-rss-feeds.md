# Working News RSS Feeds (for containers with internet)

Tested from Docker containers behind typical network setups.

## English Sources

| Name | Feed URL | Notes |
|------|----------|-------|
| BBC World | `https://feeds.bbci.co.uk/news/world/rss.xml` | 20+ items, detailed titles |
| NYT World | `https://rss.nytimes.com/services/xml/rss/nyt/World.xml` | 15+ items, concise |
| Al Jazeera | `https://www.aljazeera.com/xml/rss/all.xml` | 30+ items, mix of news/sports |

## Chinese Sources

| Name | Feed URL | Notes |
|------|----------|-------|
| BBC中文 | `https://feedx.net/rss/bbc.xml` | ~10 items, Chinese-language reporting on China/world |

## Parsing with Python (std lib)

```python
import re, sys, html
data = sys.stdin.read()
items = re.findall(r'<item>.*?</item>', data, re.DOTALL)
for item in items:
    title = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', item)
    link = re.search(r'<link>(.*?)</link>', item)
    desc = re.search(r'<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>', item)
    if title:
        t = html.unescape(title.group(1))
        l = link.group(1) if link else ''
        d = html.unescape(desc.group(1)[:300]) if desc else ''
        print(f'{t}\n  {l}\n  {d}\n')
```

## Network Detection

```bash
# Returns 401 = internet works (TCP handshake succeeded even if auth required)
curl -s --max-time 10 https://www.reuters.com/ -o /dev/null -w "%{http_code}"

# Returns nothing + exit 124 = no internet, use GitHub MCP
```
