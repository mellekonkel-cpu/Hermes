# MCP Setup for WSL + Docker Hermes Environment

## Environment Profile

- **OS**: WSL2 (Ubuntu) inside Windows 11
- **Hermes**: Docker container, config at `~/.hermes/config.yaml`
- **Node.js**: v20.19.2 (with npm 9.2.0, npx)
- **Python**: pip3 available (user site-packages), uv 0.11.6
- **No root/sudo**: Cannot apt-get install
- **No browser**: Chrome/Puppeteer/Playwright not available for web scraping

## Prerequisites

```bash
pip3 install mcp
```

## Config Location

Edit `~/.hermes/config.yaml` (mounted to `/opt/data/config.yaml` inside container).

Add `mcp_servers` section:

```yaml
mcp_servers:
  server_name:
    command: "npx"           # or "uvx"
    args: ["-y", "package-name"]
    env:
      SOME_KEY: "value"
```

## Practical Server Examples

### 1. Time server (verify MCP works)

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

Registers: `mcp_time_get_current_time`, `mcp_time_convert_time`, `mcp_time_get_timezone_list`

### 2. Filesystem server (access Windows desktop)

```yaml
mcp_servers:
  desktop:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/mnt/c/Users/武士淳/Desktop"]
```

Registers: `mcp_desktop_read_file`, `mcp_desktop_write_file`, `mcp_desktop_list_directory`, etc.

### 3. Sequential thinking (step-by-step reasoning)

```yaml
mcp_servers:
  think:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]
```

Registers: `mcp_think_sequentialthinking`

## Restart After Config Change

Exit and relaunch Hermes. On startup you'll see:

```
✅ Connected to MCP server: time (3 tools)
```

## Tool Naming

Tools get prefixed: `mcp_{server_name}_{tool_name}`.
Hyphens/dots in names → underscores.

## Environment Variable Safety

MCP subprocesses inherit a **filtered** environment (PATH, HOME, USER, LANG only).
Explicitly pass any needed keys via `env:` in config.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `pip3 install mcp` fails | Try `uv pip install mcp` instead |
| "Command not found" for npx | Check `which npx` — should be at `/usr/bin/npx` |
| Server fails to start | Increase `connect_timeout: 60` in config |
| Tools not appearing | Run `/reset` after config change |
| "No MCP servers configured" | Check YAML indentation under `mcp_servers:` |
