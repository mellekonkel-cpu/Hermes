# 武士淳 — Hermes Agent Windows Launch Configuration

## User Profile

- **Name**: 武士淳 (Wu Shichun)
- **OS**: Windows (Docker via WSL, Docker Desktop for Windows)
- **Home**: `C:\Users\WuShiChun\`
- **Data dir**: `C:\Users\WuShiChun\.hermes\` (mounted as `/opt/data` in container)
- **Output dir**: `/opt/data/青桑/`
- **Windows username**: `WuShiChun` (confirmed from mountinfo: `C:\Users\WuShiChun\.hermes` → `/opt/data`)

## Docker Image

```
nousresearch/hermes-agent
```

## Current Running Version (as of 2026-06-11)

- **Installed**: v0.16.0 (2026.6.5)
- **Upgrade path**: v0.12.0 → v0.16.0 (skipped v0.15.2 — Docker Hub latest was stale)
- **Running mode**: Daemon (`-d --restart unless-stopped --name hermes`)
- **Config migration**: Schema 0→29 performed during upgrade, 73 bundled skills synced
- **Remaining Docker issue**: `latest` tag on Docker Hub was not updated for weeks — user had to pull again on 06-11 to get the real latest. Always check npm/PyPI for the actual latest version (`npm view hermes-agent version`, `pip index versions hermes-agent`), not Docker Hub tags.

## Model Configuration (as of 2026-06-11)

| Variable | Value | Source |
|----------|-------|--------|
| `HERMES_MODEL` | `deepseek-v4-flash` | `-e` flag |
| `HERMES_INFERENCE_MODEL` | `deepseek-v4-flash` | `-e` flag |
| `CUSTOM_BASE_URL` | `https://api.deepseek.com/v1` | `-e` flag |
| `config.yaml model.default` | `deepseek-v4-pro` | `hermes config set` |
| `config.yaml model.provider` | `custom` | config file |
| `config.yaml model.base_url` | `https://api.deepseek.com/v1` | config file |

## API Provider

- **Primary**: DeepSeek (官方)
- **Base URL**: `https://api.deepseek.com/v1`
- **Auth**: Via `.env` file
- **SiliconFlow (auxiliary)**: For image generation, ASR — key in both `.env` and `-e`

## .env File

**Path**: `C:\Users\WuShiChun\.hermes\.env`

```
OPENAI_API_KEY=sk-58d792ce711646cd84655d7902e47654
OPENAI_BASE_URL=https://api.deepseek.com
SILICONFLOW_KEY=sk-...your-siliconflow-key
```

> ⚠️ `.env` sets `OPENAI_BASE_URL=https://api.deepseek.com` (no `/v1`), while docker run passes `CUSTOM_BASE_URL=https://api.deepseek.com/v1`. Do NOT "fix" the `.env` unless the model stops working.

## config.yaml

**Path**: `/opt/data/config.yaml` / `C:\Users\WuShiChun\.hermes\config.yaml`

```yaml
model:
  default: deepseek-v4-pro
  provider: custom
  base_url: https://api.deepseek.com/v1
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "github_pat_..."
```

## Script Files

- `/opt/data/青桑/脚本/startup.sh` — Entrypoint: unset proxy → start gateway → start watchdog → exec Hermes CLI
- `/opt/data/青桑/脚本/gateway-watchdog.sh` — Gateway health check & auto-restart (60s interval)
- `/opt/data/青桑/脚本/startup-inner.sh` — CLI entry script for `docker exec -it` (daemon mode access)

## 指令目录 — Launch Command Documents

**Path**: `/opt/data/青桑/指令/指令.txt`

| File | Purpose |
|------|---------|
| `指令.txt` | Current launch command (single source of truth) |
| `指令_YYYYMMDD_HHmmSS.txt` | Historical backups |
| `进入Hermes后台.ps1` | PowerShell script for entering daemon container CLI |

**Backup Protocol (iron rule):** When launch command changes, copy `指令.txt` → `指令_YYYYMMDD_HHmmSS.txt` first, then update `指令.txt`.

## Launch Methods (in priority order)

### 1. Daemon Mode (PRIMARY — since 2026-06-11)

The container runs as a background daemon.

**First-time start (PowerShell):**

```powershell
docker run -d --restart unless-stopped --name hermes `
  -v "$env:USERPROFILE\.hermes:/opt/data" `
  --env-file "$env:USERPROFILE\.hermes\.env" `
  -e CUSTOM_BASE_URL=https://api.deepseek.com/v1 `
  -e HERMES_INTERACTIVE=1 `
  -e HERMES_QUIET=1 `
  -e HERMES_MODEL=deepseek-v4-pro `\n  -e HERMES_INFERENCE_MODEL=deepseek-v4-pro `\n  nousresearch/hermes-agent:latest `\n  bash /opt/data/青桑/脚本/startup.sh\n```\n\n`startup.sh` auto-performs: unset proxy → start WeChat gateway → start watchdog → enter Hermes CLI.

**Enter existing container CLI (daily use):**

```powershell
docker exec -it hermes bash /opt/data/青桑/脚本/startup-inner.sh
```

Or use `C:\Users\WuShiChun\.hermes\青桑\指令\进入Hermes后台.ps1`

**Check container status:**
```powershell
docker ps --filter "name=hermes"
```

### 2. Interactive Mode (FALLBACK)

```powershell
docker run -it --rm `
  -v "$env:USERPROFILE\.hermes:/opt/data" `
  --env-file "$env:USERPROFILE\.hermes\.env" `
  -e CUSTOM_BASE_URL=https://api.deepseek.com/v1 `
  -e HERMES_INTERACTIVE=1 `
  -e HERMES_QUIET=1 `
  -e HERMES_MODEL=deepseek-v4-pro `\n  -e HERMES_INFERENCE_MODEL=deepseek-v4-pro `
  nousresearch/hermes-agent:latest `
  bash /opt/data/青桑/脚本/startup.sh
```

Ctrl+C kills gateway and watchdog with the container.

### 3. PowerShell $PROFILE Function (for one-word daemon access)

```powershell
Add-Content $PROFILE 'function hi { docker exec -it hermes bash /opt/data/青桑/脚本/startup-inner.sh }'
```

Then just type `hi` to enter.

### Desktop Shortcut Migration

Old shortcut (`docker run -it --rm ...`) will fail with "container name already in use". Fix:

```
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoExit -Command "docker exec -it hermes bash /opt/data/青桑/脚本/startup-inner.sh"
```

Or point it to `C:\Users\WuShiChun\.hermes\青桑\指令\进入Hermes后台.ps1`

## Upgrade Flow (daemon mode)

```powershell
docker pull nousresearch/hermes-agent:latest
docker run --rm nousresearch/hermes-agent:latest hermes --version
docker rm -f hermes
# Then run the daemon start command from Method 1 above
```

## Configuration Management

- **`config.yaml` is write-protected from direct file edit** — `patch`/`write_file` tools refuse to touch it. Use the Hermes CLI:
  ```bash
  /opt/hermes/.venv/bin/hermes config set <key> <value>
  ```
- **`config.yaml model.default` must match the `-e HERMES_MODEL` flag** — if they diverge, the `-e` flag wins at runtime, but `hermes config set` keeps them in sync for consistency.
- **`hermes config set` uses the binary at `/opt/hermes/.venv/bin/hermes`** — not in `$PATH`.

## Docker Environment Notes

- **No Docker socket inside container** — cannot `docker pull` or `docker rm` from within
- **Mount type**: 9p/drvfs (Docker Desktop for Windows shared filesystem)
- **Windows drive mapping**: `C:\` → `/opt/data` (NOT `/mnt/c/`)
- **No `hermes` in PATH** — binary at `/opt/hermes/.venv/bin/hermes`
- **No `file` command** — use `python3` for CRLF checks

## Session Boundaries

- When you're inside the container and the user stops it to upgrade, your session ends. That's expected.
- After daemon migration, the container persists across terminal sessions. User enters/exits freely via `docker exec -it`.
- User may talk via both WeChat (gateway) and CLI simultaneously.
