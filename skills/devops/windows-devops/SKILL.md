---
title: Windows DevOps
name: windows-devops
description: Generate Windows-native deployment scripts (.bat, .ps1), configure Docker container launch on Windows, manage .env-based API key isolation, and set up PowerShell $PROFILE function aliases for one-word launch.
trigger: User asks for startup scripts, launch commands, or deployment tooling on Windows; or you need to generate/review/modify a .bat, .ps1, .cmd, .reg, .vbs, or .ini file for Windows use.
---

# Windows DevOps

Generate and manage Windows-compatible scripts and deployment tooling for Docker-based tools. The user runs Docker via WSL on Windows and needs native scripts that work with CMD and PowerShell.

## Golden Rule: Verify Before Presenting

**Do not tell the user the work is done until you have verified it yourself.** Every file you generate, every script you write, every config you modify must pass through the verification checklist below before you present it to the user. The user will not accept hearing about problems after delivery — they expect the first version you show them to be working.

This rule applies to every task governed by this skill. The verification checklist is not optional — it is a mandatory step between "done" and "delivered."

## Core Rules

### 1. CRLF is Law (Iron Rule)

**Every** file generated for Windows (.bat, .ps1, .psm1, .cmd, .vbs, .reg, .ini, .txt) **must** use Windows CRLF line endings (`\r\n`). Unix LF (`\n`) causes CMD/PowerShell to fail silently or produce garbage.

**Workflow:**
1. Write the file (use `write_file` or `terminal` with appropriate content)
2. Verify format immediately with: `file <path>` — look for `CRLF` in output
3. If it shows `LF` or `ASCII text`, convert: `sed -i 's/$/\r/' <path>` then re-verify

### 2. API Key Isolation — Always Use .env

**Never** hardcode API keys, base URLs, or provider addresses in scripts. Instead:
- Store all secrets in a `.env` file alongside the scripts
- Scripts load via Docker's `--env-file` flag or equivalent mechanism
- The `.env` file uses standard format: `KEY=VALUE` (one per line, no quotes)

This prevents scripts from becoming stale when providers or keys change — only the `.env` needs updating.

### 3. Three-Tier Launch Strategy

When generating Windows launch scripts for Docker containers, provide these three tiers in order of simplicity:

| Tier | Method | Input | User Effort |
|------|--------|-------|-------------|
| **1 — Double-click** | `.bat` file on Desktop or home dir | 0 | Double-click icon |
| **2 — One-line paste** | Single flat `docker run` command for CMD or PowerShell | Copy + paste | 2 seconds |
| **3 — Two-letter alias** | PowerShell `$PROFILE` function (e.g., `function hi { ... }`) | 2 chars | One-time setup, then `hi` forever |

Always deliver all three when providing launch instructions. Each serves a different user need.

### 4. PowerShell $PROFILE Function Setup

The most ergonomic long-term solution. One-time setup:

```
Add-Content $PROFILE 'function hi { docker run -it --rm -v "$env:USERPROFILE\.<dir>:/opt/data" --env-file "$env:USERPROFILE\.<dir>\.env" -e ... nousresearch/hermes-agent }'
```

Key details:
- Use **single quotes** around the outer string in `Add-Content` to prevent inline `$env:` expansion
- The function body uses **double quotes** so `$env:USERPROFILE` expands at runtime
- After setup, user opens new PowerShell window and types the function name
- To activate immediately: `. $PROFILE` then call the function

### 5. .bat File Patterns (CMD)

- File MUST be saved with UTF-8 BOM (byte sequence EF BB BF at start). Without BOM, cmd.exe interprets Chinese characters as GBK before `chcp 65001` even executes, corrupting all non-ASCII text including file paths passed to docker exec.
- Must start with `@echo off` and `chcp 65001 >nul` (BOM handles the file's own text; chcp handles runtime output from subprocesses)
- Use `title` to label the window
- Use `^` for line continuation (trailing caret at end of each line except last)
- Use `%USERPROFILE%` for home directory (CMD variable)
- End with `pause` so window stays open after container exits
- CRLF required

### 6. .ps1 File Patterns (PowerShell)

- Use `$host.ui.RawUI.WindowTitle = "..."` for window title
- Use backtick `` ` `` for line continuation
- Use `$env:USERPROFILE` for home directory
- End with `Read-Host "按 Enter 退出"` to keep window open
- CRLF required

### 7. .bat → .ps1 Hybrid Pattern (Recommended for Docker Launchers)

When Docker CLI output needs to be parsed (e.g., finding a container by image), prefer this hybrid approach: write the logic in `.ps1` (clean string handling, no `for /f` pollution from Docker tips), then create a minimal `.bat` that calls it:

**`.bat` wrapper** (user double-clicks this):
```batch
@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0script.ps1"
```

**`.ps1` logic** (all the work is here):
```powershell
$env:DOCKER_CLI_HINTS = "false"
$cid = (docker ps -q --filter "ancestor=nousresearch/hermes-agent" 2>$null)
if ($cid) {
    docker exec -it $cid bash /opt/data/path/to/entrypoint.sh
} else {
    Write-Host "未找到容器"
}
Read-Host "按 Enter 退出"
```

**Why this pattern wins over pure .bat:**
- PowerShell's `$()` captures stdout cleanly — Docker ad tips don't pollute the capture
- `2>$null` properly redirects stderr (equivalent to `2>nul` in CMD)
- No `if ()` block parsing bugs (`.bat` misinterprets `echo 1.` inside parentheses)
- No `for /f` glitches with special characters in output
- Double-click convenience preserved via the `.bat` wrapper
- `-ExecutionPolicy Bypass` avoids PowerShell execution policy restrictions

**Both files** need UTF-8 BOM + CRLF.

### 8. Hermes config.yaml Editing — Use `hermes config set`, Not Direct File Edit

The Hermes Agent config file (`config.yaml`) is **write-protected** from direct file editing tools (`patch`, `write_file`). Attempting to edit it directly will be refused. Use the Hermes CLI instead:

```bash
/opt/hermes/.venv/bin/hermes config set <key> <value>
# Example:
hermes config set model.default deepseek-v4-pro
```

### 9. Docker Launch Pattern for Windows

The canonical command structure:

```
docker run -it --rm \
  -v "%USERPROFILE%\\.<dir>:/opt/data" ^          # mount user data dir
  --env-file "%USERPROFILE%\\.<dir>\\.env" ^        # load API config
  -e CUSTOM_BASE_URL=<provider_url> ^             # API base URL
  -e MODEL=<model_name> ^                         # model override
  <docker_image>
```

CMD uses `^` continuation; PowerShell uses `` ` ``. The flat one-line version removes all continuations.

### 10. Entrypoint Override → Root Execution Problem

When overriding the Docker entrypoint with a custom script (e.g., `bash startup.sh`), the official `entrypoint.sh` that drops privileges to the `hermes` user is bypassed. The gateway then runs as **root**, which triggers the gateway's self-protection mechanism.

**Symptom:** Gateway connects to WeChat (`weixin.state: "connected"`) but enters **draining** state (`gateway_state: "draining"`) — it acknowledges the connection but refuses to process incoming messages. The user sees "Gateway is shutting down and is not accepting another turn right now" even though the gateway is technically alive.

**Check:**
```bash
cat /opt/data/gateway_state.json | python3 -m json.tool
# Look for: "gateway_state": "draining"
```

**Fix:** Add `-e HERMES_ALLOW_ROOT_GATEWAY=1` to the `docker run` command:
```powershell
-e HERMES_ALLOW_ROOT_GATEWAY=1 nousresearch/hermes-agent:latest bash /opt/data/.../startup.sh
```

**Don't confuse with s6 restart loop:** In draining state, the gateway is alive and connected but draining. In s6 restart loop, the gateway crashes and restarts repeatedly. The fix paths are different — draining needs `HERMES_ALLOW_ROOT_GATEWAY=1` (recreate container), s6 loop needs bypass + setsid.

**Long-term fix:** Use the official Docker entrypoint instead of `bash startup.sh`:
```powershell
nousresearch/hermes-agent:latest /opt/hermes/docker/entrypoint.sh hermes gateway run
```
But this requires reworking `startup.sh` to be compatible with the entrypoint flow.

## Verification Checklist

After generating any Windows file or updating launch commands for a user:

- [ ] `file <path>` shows `CRLF` (not `LF` or `ASCII text`)
- [ ] `.bat` files start with UTF-8 BOM (verify: `python3 -c "print(open(path,'rb').read(3)==b'\xef\xbb\xbf')"`)
- [ ] No hardcoded API keys or secrets
- [ ] Paths use `%USERPROFILE%` (CMD) or `$env:USERPROFILE` (PowerShell), not `/home/` or `~`
- [ ] UTF-8 declared (`chcp 65001` in .bat)
- [ ] Pause statement at end for double-click scripts
- [ ] `.env` file exists and has correct format
- [ ] **If launch command changed:** backed up old `指令.txt` with timestamp before updating (per backup protocol)

## References

- `references/config-reference-audit.md` — Workflow for comparing local config against an external reference/wiki, including the 2026-06-11 Amaranth Wiki audit findings
- `references/hermes-clone-migration.md` — Complete guide for cloning Hermes from one Windows machine to another, including backup contents, transfer, restore, transition period, and merge-back workflow
- `references/windows-mount-points.md` — Windows drive mount points (C: → /opt/data/, not /mnt/c/)
- `references/wushichun-hermes-launch.md` — Specific launch configuration for 武士淳's Hermes Agent setup (Docker image, model, .env location, API provider, launch commands, 指令.txt backup workflow)
- `references/docker-path-mapping.md` — Path mapping confusion between WSL `/opt/data/` and container `/opt/data/` (C:\Users vs C:\ root). Critical for debugging when the user says a file is at one location but you can't find it at another.

## 指令.txt Backup Protocol

When launching Hermes for 武士淳, the startup command is documented in `/opt/data/青桑/指令.txt`. On any command change:

1. Read current `指令.txt`
2. Copy to `指令_YYYYMMDD_HHmmSS.txt` (timestamp backup)
3. Write new command to `指令.txt`

This gives the user a version history of all past launch commands.

## CRLF Write-Tool Failure Modes

Writing CRLF files from within a WSL/container environment is error-prone through standard tools. This session revealed three distinct failure modes:

### Failure Mode A: `skill_manage(action='patch')` → LF corruption

The `patch` tool in `skill_manage` converts CRLF to LF **on the modified lines only**, leaving surrounding lines intact. The result is a file with **mixed line endings** — broken for Windows.

**Fix**: Never use `patch` on Windows files that must remain CRLF. Instead, re-read the entire file content, modify it in Python, then write it back with `execute_code` using a Python script.

### Failure Mode B: `write_file` with embedded `\r\n` → double CR (`\r\r\n`)

When you pass content with `\r\n` escape sequences to the `write_file` tool, it may double-encode the carriage returns, producing `\r\r\n`. The result is a file that `od -c` shows as `\r \r \n`.

**Fix**: Use `execute_code` to write the content via Python's `.write()` method, which gives byte-level control.

### Failure Mode C: Default system `write_file` → LF

Even without `patch`, the default `write_file` behavior on Linux/WSL produces LF endings (Unix default). Always verify immediately.

### Verification When `file` and `xxd` Are Unavailable

In stripped-down environments (no `file`, no `xxd`, no `dos2unix`):

```bash
# Use od -c and look for \r\n at end of each line
od -c /path/to/file.txt | head -5
# Correct:  ...\r \n...
# Wrong:    ...\n...
```

Alternative Python one-liner:
```python
python3 -c "print(repr(open('/path/to/file.txt', 'rb').read(200)))"
# Look for b'\\r\\n' sequences
```

### Python Script for Reliable CRLF Writing

```python
with open(path, 'wb') as f:
    f.write(content.encode('utf-8').replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
```

This normalizes to LF first, then converts to CRLF — safe even if input has mixed endings.

## Upgrade & Version Verification

When upgrading Hermes Agent or reporting its version to the user:

1. **Always verify with the running binary**: `/opt/hermes/.venv/bin/hermes --version`
2. **Never trust `pyproject.toml`**: The `version` field in source code may be a stale build-time artifact (e.g., 0.12.0 in source even when the actual running version is 0.16.0)
3. **Never trust documentation alone**: The `指令.txt` file is maintained manually and may be out of sync
4. **Docker Hub tags, npm, and PyPI use different versioning**: Docker uses date-based tags (v2026.6.5), npm/PyPI use semver (0.16.0), but the binary itself may report yet another format
5. **After `docker pull` + container restart**: Run `hermes --version` to confirm the new version is active before telling the user "upgrade complete"

Getting the version wrong and contradicting the user causes severe trust damage. Verify, then speak.

### 11. Daemon Mode — s6 Restart Loop (Common Failure)

**Symptom:** Container restarts repeatedly. `docker logs` shows the s6 init sequence (preinit → s6-rc → legacy-cont-init → main-hermes → "Warning: Input is not a terminal (fd=0). Goodbye!") looping every few seconds.

**Root cause:** `startup.sh` ends with `exec /opt/hermes/.venv/bin/hermes`. In daemon mode (`-d`), there is no TTY, so Hermes CLI immediately prints "Input is not a terminal" and exits with code 0. Since `exec` replaces the shell with hermes as PID 1, the container's main process exits → container stops → Docker `--restart unless-stopped` restarts it → repeat.

**Fix (two files):**

`startup.sh` (the container's PID 1):
```bash
# Replace 'exec /opt/hermes/.venv/bin/hermes' with:
sleep infinity
```
This keeps the container alive. Gateway, Dashboard, and all s6 services run independently and are unaffected.

`startup-inner.sh` (the `docker exec` entry point):
```bash
# Replace '/opt/hermes/.venv/bin/hermes' with:
/opt/hermes/.venv/bin/hermes --cli
```
The `--cli` flag forces CLI mode (not TUI), avoiding crashes in cmd.exe TTY-forwarding scenarios.

**Verification after fix:**
1. `docker restart hermes` (from PowerShell)
2. Wait 5s, then `docker exec -it hermes bash .../startup-inner.sh` — should enter Hermes CLI without traceback
3. `docker ps --filter "name=hermes"` — shows container has been running for minutes without restart

**What NOT to do:**
- Do NOT leave `exec /opt/hermes/.venv/bin/hermes` in daemon mode — it creates an infinite restart loop
- Do NOT remove `sleep infinity` thinking s6 alone keeps the container alive — the container needs a foreground PID 1
- Do NOT confuse with the **root gateway draining** issue (gateway_state: "draining") — the fixes are different

### 12. Daemon Mode Patterns

Beyond interactive mode (`docker run -it --rm`), there is daemon mode for long-running 7x24 containers:

**Launch daemon:**
```powershell
docker run -d --restart unless-stopped --name <name> `
  -v "$env:USERPROFILE\.<dir>:/opt/data" `
  --env-file "$env:USERPROFILE\.<dir>\.env" `
  -e <ENV_VARS>... `
  <image> `
  bash /opt/data/scripts/startup.sh
```

**Enter existing daemon (daily use):**
```powershell
docker exec -it <name> bash /opt/data/scripts/startup-inner.sh
```

Where `startup-inner.sh` is a simple one-liner:
```bash
#!/bin/bash
/opt/hermes/.venv/bin/hermes
```

**Check if container is in daemon mode (from inside):**
```bash
tty  # "not a tty" = daemon mode; "/dev/pts/0" = interactive mode
cat /proc/1/comm  # "s6-svscan" = Docker init-based daemon
```

**Container naming convention:** Always name daemon containers (`--name hermes` or similar) so `docker exec -it <name>` works reliably. If no name was set at creation, rename:
```powershell
docker rename <container_id> <desired_name>
```

**Desktop launcher for daemon access (.bat) — Robust Version:**

The simple `docker exec` + `if errorlevel` pattern is insufficient. The bat must pre-check every dependency and pause on ALL exit paths to prevent 闪退:

```batch
@echo off
chcp 65001 >nul
title Hermes CLI - 正在连接...

REM ① 检查 Docker 是否可用
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker 不可用
    echo 请确认 Docker Desktop 已在任务栏运行
    pause
    exit /b 1
)

REM ② 检查容器是否存在且运行中
docker ps --filter "name=^<container_name>$" --format "{{.Status}}" >nul 2>&1
if %errorlevel% neq 0 (
    REM 可能存在但已停止
    docker ps -a --filter "name=^<container_name>$" --format "{{.Status}}" >nul 2>&1
    if %errorlevel% equ 0 (
        echo 容器 <container_name> 已停止，正在启动...
        docker start <container_name> >nul 2>&1
        if %errorlevel% neq 0 (
            echo [错误] 无法启动容器
            pause
            exit /b 1
        )
        echo 容器已启动，等待就绪...
        timeout /t 3 /nobreak >nul
    ) else (
        echo [错误] 未找到容器 <container_name>
        echo 请先执行 docker run 命令创建容器
        pause
        exit /b 1
    )
)

echo 正在进入容器...
echo 提示：输入 exit 可退出
echo.
docker exec -it <container_name> bash /opt/data/...</path/to/entrypoint.sh>

echo.
echo ============================
echo  已退出容器
echo ============================
pause
```

**Key design principles behind this template:**

- **Check availability before execution** — `docker version` fails fast if Docker Desktop isn't running
- **Auto-recover stopped containers** — `docker start` prevents "container not running" errors
- **Every branch ends with `pause`** — including the success path after `docker exec` returns
- **Chinese error messages** — meaningful diagnostics, not raw Docker stderr
- **`exit /b` on fatal errors** — so calling scripts don't continue on failure

**When to simplify vs. use this template:**
- Use this template when the user has reported 闪退 (flash-close) or "bat always crashes"
- Use the simple `docker exec` + `pause` pattern only when the user explicitly asked for a minimal launcher and Docker Desktop + container are known to be stable

Note: Unlike interactive mode, the container persists after closing the CLI window.

**Daemon mode pitfalls:**
- Container name MUST be consistent between start and exec commands
- Can't do `docker ps` or `docker rm` from inside the container (no docker.sock)
- Access requires a separate terminal window (`docker exec -it`)
- If the gateway or watchdog dies inside a daemon container, restart the container from the host: `docker restart hermes`

**Upgrade flow for daemon mode:**
```powershell
docker pull nousresearch/hermes-agent:latest
docker rm -f hermes
# Then re-run the daemon start command
```

### 12. PowerShell Execution Policy — Never Assume .ps1 Works

Windows PowerShell's default execution policy is **Restricted**, which blocks ALL `.ps1` scripts.

**Three workarounds (in order of preference):**

1. **Give raw commands** — Provide the `docker` command as copy-pasteable text. Most reliable, zero friction.

2. **`.bat` wrapper** — Write a `.bat` file that calls `powershell -ExecutionPolicy Bypass -File script.ps1`. The `.bat` file bypasses the policy.

3. **One-time bypass** — User runs: `powershell -ExecutionPolicy Bypass -File script.ps1`

**Never expect the user to run `.ps1` scripts directly.** They will get `UnauthorizedAccess` / `PSSecurityException` and the script fails immediately.

### 13. Cross-Machine Clone & Migration

See `references/hermes-clone-migration.md` for the complete workflow:

- **Packaging** — tar command with include/exclude rules for a portable ~500MB archive
- **Organized delivery** — place backup + one-click setup .bat + deployment guide in a dedicated folder (e.g., `青桑/笔记本分身/`)
- **Transfer** — USB, SCP, or cloud delivery to target machine
- **Restore** — Use the companion `hermes-clone-setup.bat` for one-click restore, or extract manually to `%USERPROFILE%\\.hermes\\` with `tar` / `docker run --rm alpine:3.19 tar xzf` fallback
- **Launch** — Same `docker run` command as source, after verify with `hermes --version`
- **Transition period** — Two independent instances, one WeChat connection at a time; cron runs on both (harmless duplicates)
- **Merge-back** — Archive target `skills/` + `memories/` + `sessions/` + `state.db` + `cron/` → overwrite source → `docker restart hermes`

Key constraint: WeChat iLink supports one active connection; switching machines requires re-scan.

**Clone backup pitfalls (see `references/hermes-clone-migration.md` → Periodic Clone Maintenance for full audit procedure):**\n- **Supplement (delta) backup** — When the main backup is large (1GB) and only a few files changed, create a small supplement tar.gz instead of rebuilding. See `references/hermes-clone-migration.md` → Supplement (Delta) Backup Strategy.
- **Config path relocation** — If a service config file is moved (e.g., mihomo config from `mihomo/run/config.yaml` to `青桑/photo/config.yaml`) and launcher scripts are updated to reflect the new path, the existing backup becomes stale. The backup archive still references the old path, and the old config file may be broken or an error message. Re-backup after ANY path change.
- **Config file validity** — A backup's config file may contain subscription error text instead of valid configuration. Always `grep -q '^proxies:'` on mihomo configs in the backup to verify. Do not assume a file that "exists" is valid.
- **Deployment doc drift** — `分身部署说明.txt` and `hermes-clone-setup.bat` must be updated whenever the docker run command, startup scripts, or environment variables change. A user following outdated docs will get a broken clone.
- **tar timeout on large `sessions/`** — At default 120s terminal timeout, a tar.gz including `sessions/` (often 100MB+) may not finish. Fix: raise timeout to 300s, or `--exclude=sessions` for a faster backup that omits full transcripts (skills + memories + config are the critical parts).
- **Self-referential exclusion** — If the backup archive is stored inside the folder being tar'd (e.g., `青桑/笔记本分身/backup.tar.gz`), add `--exclude=青桑/笔记本分身` to prevent tar from trying to include the growing archive into itself. Without this, tar prints "file changed as we read it".
- **Config changes require re-backup** — After adding a new provider or changing `.env`/`config.yaml`, the existing backup is stale. Re-run the tar to capture updates before transferring to the target machine.

### 14. Daemon Mode Detection

When asked "is the container running in daemon or interactive mode?" from inside the container:

```bash
# Method 1: tty check (most reliable)
tty
# "not a tty" = daemon/background
# "/dev/pts/0" = interactive terminal

# Method 2: PID 1 process
cat /proc/1/comm
# "s6-svscan" = Docker container with s6 init (typical for daemon)
# "bash" or "hermes" = interactive

# Method 3: hostname = container ID (works in both modes)
hostname
```

## Pitfalls

- **DON'T** generate .bat files with LF endings — CMD will silently ignore the file or show garbled text
- **DON'T** hardcode API keys — they expire and the script becomes useless
- **DON'T** use Linux paths (`/home/`, `~/`) in Windows scripts — use `%USERPROFILE%` or `$env:USERPROFILE`
- **DON'T** forget `pause` / `Read-Host` at the end — the window closes instantly on error and user can't see the error message
- **DON'T** forget `chcp 65001` in .bat — Chinese characters will display as garbage
- **DON'T** forget UTF-8 BOM on .bat files with Chinese content — `chcp 65001` alone is insufficient because cmd.exe parses the file's own text BEFORE chcp executes. Without BOM, Chinese file paths like `/opt/data/青桑/脚本/startup-inner.sh` get garbled to `/opt/data/闈掓/鑴氭湰/startup-inner.sh` and fail with "No such file or directory"
- **DON'T** use `skill_manage(action='patch')` or `patch` tool to edit .bat files — these tools corrupt CRLF line endings. Use `execute_code` with Python for byte-level control, or `write_file` followed by CRLF verification+fix
- **DON'T** use `if (...) else (...)` blocks in .bat files when the body contains `echo N.` (numbered lists like `echo 1. Docker Desktop...`). The cmd.exe parser misinterprets `N.` as a file/command reference inside parenthesized blocks, causing the entire if-block to crash silently. **Use `goto` labels instead**: `if not defined VAR goto :label` → `...` → `:label`. Goto-based flow is immune to this parser bug.
- **DON'T** use `set /p` for user input after `docker exec -it` in .bat files. `docker exec -it` takes over the terminal in raw mode; when the container exits, Docker may not restore cooked mode, leaving stdin at EOF or in a corrupted state. `set /p` then either returns immediately with empty input (causing infinite "无效输入" loops) or causes cmd.exe to terminate the script entirely. **Use `choice` instead** — it calls the Win32 `ReadConsoleW` API directly, bypassing stdin redirection entirely. Example: `choice /c YN /n /m "重新进入？[Y/N]: "` → check `if errorlevel 2` (N) and `if errorlevel 1` (Y). Also remove redundant `goto :ask_reenter` loops — `choice` handles invalid input natively by beeping.
- **DON'T** use `for /f` with `docker ps -q --filter "ancestor=<image>"` in the same block as `docker exec -it` without suppressing Docker ad tips first. Set `DOCKER_CLI_HINTS=false` before any docker commands. The ad tip goes to stdout, pollutes the `for /f` capture variable, and causes `docker exec` to receive garbled text as the container ID.
- **DON'T** rely on hardcoded container names (`docker exec -it hermes`) in .bat launchers. Container names drift across rebuilds. **Use image-ancestor discovery**: `for /f %%i in ('docker ps -q --filter "ancestor=<image>" 2^>nul') do set CID=%%i` then `docker exec -it %CID% ...`. The `2^>nul` silences stderr when Docker is unreachable; `^` escapes the `>` inside `for /f`'s backtick-free command string.
- **Docker Desktop ad noise**: After EVERY docker command, Docker Desktop prints a "What's next: Try Docker Debug..." promotional tip to stdout. This is NOT an error message and does NOT mean the command failed. Users unfamiliar with this behavior may mistake it for a failure indicator. When diagnosing .bat launcher issues, check for the actual error (e.g., "No such container") BEFORE the ad tip, not the tip itself.
  - **Suppress it**: Set `DOCKER_CLI_HINTS=false` environment variable before any docker command. In `.bat`: `set DOCKER_CLI_HINTS=false`. In `.ps1`: `$env:DOCKER_CLI_HINTS = "false"`. This prevents the tip from appearing entirely.
  - **Why it matters for launcher scripts**: The ad tip goes to **stdout** (not stderr), so `2^>nul` does NOT suppress it. In `.bat` `for /f` loops that capture `docker ps -q` output, the tip pollutes the captured variable — the first "line" becomes the Docker tip text instead of the container ID, causing `docker exec` to fail with a garbled container name.
- **PowerShell backtick (`` ` ``) is NOT the same as CMD caret (`^`)** — never mix them
- `$PROFILE` path may not exist on first run — if `Add-Content` errors, create the file first: `New-Item -Force $PROFILE`
- When writing scripts inside WSL/container to a mounted Windows directory, files inherit the Unix line ending by default — always explicitly verify CRLF
- **Windows drive mount point is NOT always `/mnt/c/`** — always check `df -h` first to find where `C:\\` is mounted. In this environment, `C:\\` → `/opt/data/`. So `C:\\Users\\WuShiChun\\...` resolves to `/opt/data/Users/WuShiChun/...`, not `/mnt/c/Users/...`. Never assume the mount path without verifying.
- **`.env` vs `CUSTOM_BASE_URL` subtlety**: The `.env` file's `OPENAI_BASE_URL` may omit `/v1` (e.g., `https://api.deepseek.com`) while the docker run's `CUSTOM_BASE_URL` includes it (e.g., `https://api.deepseek.com/v1`). These serve different internal purposes in Hermes Agent. Do NOT "correct" one to match the other unless the model stops working — the current combination is verified working.
- **Respect "no shortcut files" preference**: For 武士淳, do NOT generate `.bat`/`.ps1` launcher files in the `.hermes` directory unless explicitly asked. He prefers to paste the raw `docker run` command directly. First check `references/wushichun-hermes-launch.md` for launch methods before creating any new files.
- **Git is not installed on Windows by default** — When a user on Windows wants to `git clone` or use any git command, first verify with `git --version` or `where git`. If git is unavailable, offer alternatives in this order:
  1. **One-click packages** — Many popular GitHub projects provide standalone ZIP downloads (e.g., 百度网盘 links in README). This is the most beginner-friendly option.
  2. **Docker** — If Docker is already running (common for this user), use `docker-compose up` in the project directory instead of local git.
  3. **Install Git** — Guide user to https://git-scm.com/download/win, but explain what Git is first. Many beginners confuse Git with GitHub.
  - **Common confusion:** User thinks Git = GitHub. Briefly explain: "Git 是装在你电脑上的一个软件，GitHub 是一个网站。关系就像：Git = 手机相机（拍照），GitHub = 朋友圈（分享）。"
