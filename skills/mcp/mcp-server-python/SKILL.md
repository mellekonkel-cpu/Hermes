---
name: mcp-server-python
description: Write Python MCP servers that work with Hermes Agent — boilerplate, SDK API patterns, pitfalls, and templates.
version: 1.0.0
author: Amaranth
license: CC BY-NC-SA 4.0
metadata:
  hermes:
    tags: [mcp, server, python, sdk]
    related_skills: [mcp/native-mcp, software-development/public-api-brain-router]
---

# Python MCP Server Authoring for Hermes

Patterns and templates for writing custom MCP servers in Python that register as tools in Hermes Agent.

## Quick Start Boilerplate

A minimal working MCP server for Hermes (works with mcp SDK ≥1.27):

```python
#!/usr/bin/env python3
import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ServerCapabilities

server = Server("my_server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="my_tool",
            description="What this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter description"},
                },
                "required": ["param"],
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "my_tool":
        result = {"result": f"Hello, {arguments.get('param', 'world')}!"}
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="my_server",
                server_version="1.0.0",
                capabilities=ServerCapabilities(),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## SDK API Pitfall (run_stdio removed)

**mcp SDK ≤1.26** used `server.run_stdio()` — the old pattern:
```python
async with server.run_stdio(): pass  # OLD — removed in 1.27+
```

**mcp SDK ≥1.27** requires `stdio_server()` + `server.run()`:
```python
from mcp.server.stdio import stdio_server
async with stdio_server() as (read_stream, write_stream):
    await server.run(read_stream, write_stream, InitializationOptions(
        server_name="...",
        server_version="1.0.0",
        capabilities=ServerCapabilities(),  # REQUIRED in 1.27+
    ))
```

Three changes from ≤1.26 to ≥1.27:
1. `run_stdio()` → `stdio_server()` context manager
2. `server.run()` now requires explicit `read_stream` / `write_stream` args
3. `InitializationOptions` requires `capabilities=ServerCapabilities()` (Pydantic validates this field)

## Registering in Hermes

Add to `config.yaml` under `mcp_servers`:

```yaml
mcp_servers:
  my_server:
    command: /path/to/venv/bin/python3   # use venv python, not system
    args: ['/path/to/server.py']
    timeout: 30    # per-tool-call timeout
```

The tool shows up as `mcp_my_server_{tool_name}` in Hermes.

## Important Notes

- **Use the venv python**, not system python — system python likely lacks `mcp` SDK
- **Environment filtering**: Hermes only passes safe baseline env vars (PATH, HOME, etc.) to MCP subprocesses. Explicitly set API keys via `env:` in the MCP server config
- **Connection lifecycle**: MCP servers live for the lifetime of the Hermes gateway. Restart gateway to pick up new servers or code changes
- **Tool naming**: MCP tool names become `mcp_{server_name}_{tool_name}` in Hermes. Avoid hyphens/dots in function names (replaced with underscores)

## Templates

See `templates/minimal-server.py` for a ready-to-use boilerplate.
