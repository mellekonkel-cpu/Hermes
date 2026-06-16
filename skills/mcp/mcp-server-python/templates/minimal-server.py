#!/usr/bin/env python3
"""
Minimal working MCP server template for Hermes Agent.
Copy this file, rename, and modify the tool definitions.

Usage:
    python3 minimal-server.py

Register in config.yaml:
    mcp_servers:
      my_server:
        command: /path/to/venv/bin/python3
        args: ['/path/to/minimal-server.py']
        timeout: 30
"""
from __future__ import annotations

import asyncio
import json

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ServerCapabilities

server = Server("my_server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="hello",
            description="Returns a greeting for the given name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet",
                    },
                },
                "required": ["name"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "hello":
        name_val = arguments.get("name", "world")
        result = {"message": f"Hello, {name_val}!"}
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2),
        )]
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
