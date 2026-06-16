# MCP Search Routing — 配置记录

## 环境
- Hermes v0.16.0, daemon 模式
- MCP SDK v1.27.2（请用 stdio_server() + server.run()，非 run_stdio()）
- 搜索服务器路径: /opt/data/scripts/mcp_search_server.py
- MCP 配置: /opt/data/config.yaml → mcp_servers.mcp_search

## 当前状态

### MCP 服务器进程
由 Hermes gateway 自动启动，每次 gateway 重启时拉起。
```
运行时: /opt/hermes/.venv/bin/python3 /opt/data/scripts/mcp_search_server.py
```

### 工具列表
| 工具名 | 用途 |
|---|---|
| `mcp_mcp_search_search` | 统一搜索，mode 参数选引擎 |
| `mcp_mcp_search_check_engine_status` | 查看各引擎 Key 配置 |

### 搜索引擎降级链
```
tinyfish → perplexity → anysearch → firecrawl → youcom → exa
→ tavily → serper → duckduckgo
```

### 已实现的引擎
| 引擎 | 状态 | 所需 Key |
|---|---|---|
| DuckDuckGo | ✅ 免 Key 可用 | 无 |
| TinyFish | ⚠️ 需 Key | ~/.tinyfish-key |
| Serper | ⚠️ 需 Key | SERPER_API_KEY |

其他引擎已结构化但未实装搜索逻辑——当 Key 配置后会在脚本中扩展。

### 关联 Skills
- `research/tinyfish-search-fetch` — TinyFish 集成说明
- `software-development/public-api-brain-router` — 公共 API 路由
