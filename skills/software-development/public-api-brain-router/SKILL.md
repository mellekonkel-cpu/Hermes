---
name: public-api-brain-router
description: 公共 API 路由 — 免 Key 公共 API 直接查询，不走搜索引擎。覆盖书籍/词典/论文/古籍/汇率/天气/地震/诗歌等场景
version: 1.0.0
author: Amaranth
license: CC BY-NC-SA 4.0
metadata:
  hermes:
    tags: [search, api, public, routing]
    related_skills: [tinyfish-search-fetch, precision-review-search]
---

# 公共 API 路由 — Public API Brain Router

免 Key 公共 API 直接查询，不走搜索引擎。适用于精确结构化数据场景。

## 支持的 API

| 领域 | API | 免 Key | 端点 |
|------|-----|--------|------|
| 搜书 | OpenLibrary | ✅ | `https://openlibrary.org/search.json?q={query}` |
| 查词典 | Free Dictionary | ✅ | `https://api.dictionaryapi.dev/api/v2/entries/en/{word}` |
| 论文 | arXiv | ✅ | `http://export.arxiv.org/api/query?search_query=all:{query}` |
| 古籍 | Chinese Text Project | ✅ | `https://ctext.org/api/search?q={query}` |
| 电子书 | Gutendex | ✅ | `https://gutendex.com/books?search={query}` |
| 汇率 | Exchangerate API | ✅ | `https://api.exchangerate-api.com/v4/latest/{base}` |
| 地震 | USGS | ✅ | `https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=10` |
| 诗歌 | PoetryDB | ✅ | `https://poetrydb.org/title/{title}` |
| IP 定位 | ip-api.com | ✅ | `http://ip-api.com/json/{ip}` |
| 论文元数据 | Crossref | ✅ | `https://api.crossref.org/works?query={query}` |
| 天气 | Weatherstack | ❌ | `http://api.weatherstack.com/current?access_key={key}&query={query}` |

## 使用方式

当用户查询涉及上述领域时，优先尝试免 Key API。降级链：

```
免 Key API → 需 Key API → MCP 统一搜索 → DuckDuckGo 兜底
```

## 快速路由

通过关键词匹配自动路由：

```yaml
路由规则:
  图书/书籍/作者 → OpenLibrary
  单词/词典/definition → Free Dictionary
  论文/article/arxiv → arXiv (国内镜像时用 https://info.arxiv.org/help/cn.html)
  古诗/诗词/poem → PoetryDB
  地震/earthquake → USGS
  汇率/exchange rate → Exchangerate API
  天气/weather → Weatherstack (需 API Key)
  IP 地址/location → ip-api.com
  古籍/ctext → Chinese Text Project
  电子书/gutenberg → Gutendex
  DOI/crossref → Crossref
```

## 安装

```bash
# 下载 skill 到 skills 目录
cp -r public-api-brain-router ~/.hermes/skills/software-development/

# Weatherstack 需 Key（可选）
# 在 .env 中添加: WEATHERSTACK_API_KEY=your_key
```

## 注意事项

- 公共 API 有 Rate Limit，批量查询需间隔
- arXiv 国内访问可能较慢，可配置国内镜像
- Chinese Text Project 返回繁体中文
- PoetryDB 以英文诗歌为主
