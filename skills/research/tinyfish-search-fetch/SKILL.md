---
name: tinyfish-search-fetch
description: TinyFish 免费搜索（5次/分钟）+ 抓取（25 URL/分钟），基于自建 Chromium 集群渲染
version: 1.0.0
author: Amaranth
license: CC BY-NC-SA 4.0
metadata:
  hermes:
    tags: [search, tinyfish, free, scrape]
    related_skills: [public-api-brain-router, precision-review-search]
---

# TinyFish Search & Fetch

TinyFish 免费搜索与页面抓取工具。被集成到 MCP 搜索服务器的首层引擎。

## 特点

- 搜索：5次/分钟（自由层），基于自建 Chromium 集群渲染
- 抓取：25 URL/分钟
- 免注册，直接使用 API Key

## 安装

### 1. 获取 Key

访问 https://tinyfish.io 注册获取 API Key，然后：

```bash
echo "your_tinyfish_key_here" > ~/.tinyfish-key
chmod 600 ~/.tinyfish-key
```

### 2. 验证 Key

```bash
curl "https://search.tinyfish.io/api/search?q=test&key=$(cat ~/.tinyfish-key)"
```

如果返回 JSON 结果，说明 Key 有效。

## API 参考

| 功能 | 端点 | 说明 |
|------|------|------|
| 搜索 | `https://search.tinyfish.io/api/search?q={query}&key={key}` | 返回搜索结果 |
| 抓取 | `https://search.tinyfish.io/api/fetch?url={url}&key={key}` | 抓取指定 URL |

## 使用场景

- 日常搜索的默认引擎（免费、免注册）
- 学术论文摘要快速检索
- 中文内容搜索（TinyFish 对中文支持较好）
- MCP 搜索服务器的首层降级入口

## 注意事项

- 5次/分钟限制，批量任务需加 `time.sleep(12)` 间隔
- WSL/容器环境需配置 HTTP 代理
- 证书验证失败时自动 SSL 降级（脚本已处理）
- 如 Key 失效，会自动降级到 Perplexity → AnySearch → ... → DuckDuckGo
