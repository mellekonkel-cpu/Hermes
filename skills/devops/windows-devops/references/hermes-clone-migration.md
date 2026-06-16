# Hermes Clone & Cross-Machine Migration (Windows Docker)

How to clone a running Hermes Agent from one Windows machine to another, run both independently during a transition period, and merge back.

## Target Scenario

- **台式（主）** — 长期主力机器，已有完整 Hermes 配置
- **笔记本（副）** — 过渡期间使用，需要克隆台式上我的一切
- **目标**：笔记本上能独立运行、产生新记忆/skill → 稳定后合并回台式

## Architecture

```
台式 (主)                 笔记本 (副)
  ┌──────┐                ┌──────┐
  │Hermes│  tar.gz ───→   │Hermes│  过渡期各自运行
  │v0.16 │  (clone)       │v0.16 │
  └──────┘                └──────┘
      ↑                      │
      └──── tar.gz (merge) ←─┘  稳定后合并回台式
```

## Step 1: Backup on Source Machine

From inside the Hermes Docker container or from WSL (where `/opt/data` is the bind mount):

```bash
cd /path/to/.hermes  # e.g. /opt/data
tar czf hermes-backup-$(date +%Y%m%d_%H%M%S).tar.gz \
  --exclude=logs \
  --exclude=ComfyUI \
  --exclude=mihomo \
  --exclude=home \
  --exclude=cache \
  --exclude=image_cache \
  --exclude=audio_cache \
  --exclude=pastes \
  --exclude=bin \
  --exclude=lsp \
  --exclude=pylib \
  --exclude=.cache \
  --exclude=.npm \
  --exclude=.local \
  --exclude=weixin \
  --exclude=workspace \
  --exclude=sandboxes \
  --exclude=images \
  --exclude=interrupt_debug.log \
  --exclude="*.bak*" \
  --exclude="*.lock" \
  --exclude="*.pid" \
  --exclude="*_cache.json" \
  --exclude="state.db-wal" \
  --exclude="state.db-shm" \
  --exclude=sessions \
  --exclude="青桑/笔记本分身" \
  .
```

**Included:**

| Item | Why |
|---|---|
| `.env` | API Keys (DeepSeek, etc.) — **critical, protect this file** |
| `config.yaml` | Model routing, provider config |
| `skills/` | All skills including custom ones (public-api-brain-router, tinyfish-search-fetch, etc.) |
| `memories/` | MEMORY.md (Hermes's notes) + USER.md (user profile) |
| `cron/` | Scheduled jobs (daily briefing, watchdog, etc.) |
| `scripts/` | Custom helper scripts |
| `青桑/` | User's personal scripts, batch files, papers, audio |
| `profiles/` | Worker profiles and their config |
| `state.db` | Session index (so the new machine can search past sessions) |
| `gateway_state.json` | Gateway connection state (will need re-auth on new machine) |
| `channel_directory.json` | Channel routing config |
| `auth.json` | Auth tokens |

**On tar timeout — exclude sessions to speed up:**
Including `sessions/` (often 100MB+) can cause `tar` to exceed the default 120s terminal timeout. Workarounds:
- **Option A (fast + small, ~400MB):** Add `--exclude=sessions` — omits full transcripts. The new machine won't have past session history, but skills + memories + config are the critical parts for continuity.
- **Option B (complete but slow, ~500MB+):** Keep `sessions/` included but raise terminal timeout to 300s. This preserves full conversation history on the new machine.

**Excluded:**

| Item | Why |
|---|---|
| `logs/` | Stale logs, new machine starts fresh |
| `ComfyUI/` | 541MB of ComfyUI models — too large, not required for core Hermes |
| `mihomo/` | Proxy binaries — install fresh on new machine |
| `home/`, `cache/*`, `image_cache/*`, `audio_cache/*`, `pastes/*` | Cached data, regenerated |
| `bin/`, `lsp/`, `pylib/` | Tools/cache — not needed for clone |
| `*.bak*`, `*.lock`, `*.pid` | Temp files, process locks |

## Step 2: Package Deliverable (Recommended: Organized Folder)

Rather than leaving the tar.gz loose, create a dedicated folder with all clone materials:

```bash
mkdir -p 青桑/笔记本分身
cp hermes-backup-$(date +%Y%m%d_%H%M%S).tar.gz 青桑/笔记本分身/
```

Then add two companion files inside the folder:

**One-click setup script** (`hermes-clone-setup.bat`) — automates the entire restore process:
- Checks Docker Desktop is running
- Creates `%USERPROFILE%\\.hermes` if it doesn't exist
- Extracts the backup (falls back to `docker run --rm alpine:3.19 tar xzf` if Windows tar fails)
- Pulls the Docker image
- Runs the `docker create` command with correct env vars
- Output: a running container on the target machine

**Deployment guide** (`分身部署说明.txt`) — standalone reference covering:
- Pre-requisites (Docker Desktop, proxy, backup file location)
- Auto-setup and manual setup paths
- WeChat reconnection instructions
- Transition period notes
- Merge-back workflow for returning to source

See `青桑/笔记本分身/` for a concrete example of this pattern.

## Step 3: Transfer Archive

Method options (pick one):
- **USB drive** — fastest for ~500MB
- **SCP** — `scp user@台式IP:hermes-backup-*.tar.gz .`
- **网盘/云存储** — upload to Baidu Netdisk / OneDrive / etc.
- **SMB share** — map network drive on both machines

**Tip:** Copy the entire `青桑/笔记本分身/` folder, not just the tar.gz. The .bat and .txt files go with it.

## Step 4: Restore on Target Machine

### Option A: One-Click (Recommended)

1. Copy the `青桑/笔记本分身/` folder to the target machine (anywhere)
2. Double-click `hermes-clone-setup.bat`
3. The script handles extraction, image pull, and container creation

### Option B: Manual

On the Windows target machine (笔记本):

```powershell
# 1. Create the .hermes directory if it doesn't exist
mkdir "$env:USERPROFILE\.hermes" -Force

# 2. Copy the tar.gz into it
copy D:\path\to\hermes-backup-*.tar.gz "$env:USERPROFILE\.hermes\"

# 3. Extract — Windows tar may fail; use Docker as fallback
cd "$env:USERPROFILE\.hermes"
tar xzf hermes-backup-*.tar.gz
if ($LASTEXITCODE -ne 0) {
    # Windows tar parser sometimes chokes on long paths
    docker run --rm -v "$env:USERPROFILE\.hermes:/data" alpine:3.19 tar xzf /data/hermes-backup-*.tar.gz -C /data/
}

# 4. Verify critical files exist
ls .env, config.yaml, skills/, memories/
```

**Why the `docker run --rm alpine:3.19` workaround:** Windows 10's built-in `tar` has known issues with long paths and certain tar features. Docker's Alpine container has a proper GNU tar that handles portable archives reliably. This avoids silent corruption on extraction failure.

## Step 5: Launch on Target Machine

```powershell
docker pull nousresearch/hermes-agent:latest
docker run -d --restart unless-stopped --name hermes ^
  -v "$env:USERPROFILE\.hermes:/opt/data" ^
  --env-file "$env:USERPROFILE\.hermes\.env" ^
  -e CUSTOM_BASE_URL=https://api.deepseek.com/v1 ^
  -e HERMES_INTERACTIVE=1 ^
  -e HERMES_QUIET=1 ^
  -e HERMES_MODEL=deepseek-v4-flash ^
  -e HERMES_INFERENCE_MODEL=deepseek-v4-flash ^
  -e HERMES_ALLOW_ROOT_GATEWAY=1 ^
  nousresearch/hermes-agent:latest ^
  bash /opt/data/青桑/脚本/startup.sh
```

Note: Model name and env vars should match what the source machine was using. Update from the source's `指令.txt`.

## Step 5: Reconnect WeChat Gateway

The cloned container will have the old `gateway_state.json` from the source machine. The new machine needs its own WeChat QR code connection:

```powershell
docker exec -it hermes bash /opt/data/青桑/脚本/startup-inner.sh
# Then within the Hermes CLI:
# hermes gateway run  (or re-scan QR code)
```

## Step 6: Transition Period

- **台式**：可以 `docker stop hermes` 停掉容器的前台交互，或放任不管（微信 iLink 只允许一个连接，笔记本连上后台式自动断开）
- **笔记本**：正常使用，产生新对话、新记忆、新 skill
- **微信**：两者不能同时接微信 — 笔记本上用的时候台式的微信网关会失效

## Step 7: Merge Back to Source

When ready to return to the desktop machine:

### 7a. Backup the target machine (笔记本)

Same tar command as Step 1, but this time **include** `sessions/` and `state.db`:

```bash
tar czf hermes-merge-$(date +%Y%m%d_%H%M%S).tar.gz \
  .env config.yaml skills/ memories/ cron/ scripts/ \
  青桑/ profiles/ state.db sessions/ \
  --exclude=logs --exclude=ComfyUI ...
```

### 7b. Transfer archive back to source machine

USB / SCP / cloud — same as Step 2.

### 7c. On source machine: backup current state first, then overwrite

```powershell
cd "$env:USERPROFILE\.hermes"
# Backup the old source state just in case
mv .env .env.source-backup
mv skills/ skills.source-backup
mv memories/ memories.source-backup
# ... etc for each directory being replaced

# Extract the merged archive on top
tar xzf D:\path\to\hermes-merge-*.tar.gz

# Restart the container
docker restart hermes
```

### 7d. Verify

```powershell
docker exec -it hermes bash /opt/data/青桑/脚本/startup-inner.sh
# Check: skills, memories, and recent sessions all present
```

## Important Caveats

- **WeChat iLink = single connection** — Only one gateway can be active at a time across all machines. Switching machines requires re-scanning the QR code.
- **Cron jobs run on both machines** — During transition, both machines will attempt to run scheduled tasks (daily briefing, watchdogs). This is harmless but redundant. Either:
  - Stop cron on the source machine: `docker stop hermes`
  - Or accept duplicate outputs
- **`state.db` is the session index** — It references sessions by path. If sessions from both machines are merged, the new `state.db` on the source will index both sets. Old source sessions from before the clone will be in the merged sessions/ directory too (since both sides started from the same clone).
- **API Keys in `.env`** — The same `.env` works on both machines IF the target has network access to the same API providers. For DeepSeek (api.deepseek.com), this is fine from China; from overseas, a proxy may be needed.
- **Docker version compatibility** — Both machines should use the same Hermes image version (`nousresearch/hermes-agent:latest`). If the source was pinned to an older version, pin the same on the target. Verify with `hermes --version` after launch.

## Periodic Clone Maintenance (Backup Audit)

When the user asks "检查笔记本分身是否有遗漏" (check backup for omissions), or when significant config changes are made to the running system, run a full audit against the clone backup stored at `青桑/笔记本分身/`.

### Audit Checklist

Run these checks in order when auditing a backup:

1. **File inventory comparison** — List files in the backup tar vs current state. Key files to verify: `.env`, `config.yaml`, `skills/` manifest, `memories/`, `cron/jobs.json`, all startup scripts in `青桑/脚本/`.

2. **Script config path drift** — For every startup/driver script (especially `start.sh`, `startup.sh`, `startup-inner.sh`, `start-gateway.sh`), compare the file paths it references between the backup copy and the current copy. If a config file was moved (e.g., mihomo config from `mihomo/run/config.yaml` → `青桑/photo/config.yaml`), update the backup's script and ensure the target config file is physically present in the backup.

3. **Config file validity** — For each config file in the backup, verify it's not empty, not an error message, and contains working data (valid proxies, valid JSON, valid YAML). The most common failure: the backup's `mihomo/run/config.yaml` contains 176 bytes of subscription error text ("The following link doesn't contain any valid node info") instead of valid proxy config. Validate with: `grep -q '^proxies:' <config-path>` for mihomo, or `python3 -c "import yaml; yaml.safe_load(open(...))"` for general YAML.

4. **.env and main config integrity** — Compare backup `.env` and `config.yaml` with current versions via `diff`. These change infrequently but must match exactly. Values are masked for security in output.

5. **Session data freshness** — Compare `state.db` sizes. A 5MB+ gap indicates unrecoverable conversations on the clone (acceptable — sessions are not critical for clone functionality, but worth noting in the report).

6. **Image/media consistency** — Verify the backup's `青桑/photo/` directory matches the essential images from the current environment. Generated/cache images can be excluded.

7. **Deployment docs alignment** — Verify `分身部署说明.txt` and `hermes-clone-setup.bat` still match the actual deployment process. If `startup.sh` or docker run parameters have changed, update these docs.

### Common Failure: Config Path Relocation

**Symptom:** The backup's launcher script (e.g., `start.sh`) references a config file path, but the referenced config file in the backup is either missing or contains invalid data. Meanwhile, the working config exists at a different path in the current environment.

**Example (mihomo proxy):**
```
Location          | Backup State                | Current State
------------------|-----------------------------|-------------------------------
mihomo/run/config.yaml   | 176 bytes (ERROR: sub dead)  | file no longer exists
青桑/photo/config.yaml  | ❌ NOT IN BACKUP             | 698 bytes (VALID: US08 node)
mihomo/start.sh          | points to mihomo/run/ (old)   | points to 青桑/photo/ (new)
```

**Root cause:** The config file was moved when the subscription was refreshed (new subscription saved to a different location for organization), but the clone backup was not updated to match. The old config at the original path may have been overwritten with garbage (e.g., subscription error output).

**Fix:** Update the backup in four steps:
1. Copy the current working config file into the backup archive at the path the launcher script expects, OR update the launcher script to point to the path that will exist after extraction
2. Update the launcher script (`start.sh`, `startup.sh`, etc.) in the backup tar to reference the correct config path
3. Re-tar the backup to produce a fresh, consistent archive
4. Update `分身部署说明.txt` if the deployment process changed (new env vars, new docker run flags, different startup sequence)

### When to Re-Backup

Trigger re-backup immediately when ANY of these change:

- `.env` or `config.yaml` (Hermes main config) modified
- New provider added or API key changed
- Proxy config (`mihomo`) reloaded with new subscription
- New skill installed or custom script added
- `start.sh` / `startup.sh` / entry point scripts modified
- A significant new workflow is configured (dual vision pipeline, new gateway, new cron job)
- Any file path relocation occurs that affects startup scripts

If more than 3 days have passed since the last backup, audit it proactively — the user may not realize the backup is stale.

### Supplement (Delta) Backup Strategy

When the main backup is large (500MB+) and only a few files changed, **do NOT rebuild the entire archive**. Instead, create a small supplement tar.gz that overlays on top of the main backup:

```bash
# Create a supplement with just the changed/missing files
cd /opt/data
tar czf 青桑/笔记本分身/hermes-backup-supplement.tar.gz \
  mihomo/bin/mihomo \
  sn_scripts/new_script.py \
  state.db \
  memories/MEMORY.md \
  memories/USER.md \
  channel_directory.json
```

**Deployment script must then extract both archives in sequence:**
```bash
# Extract main backup first
tar xzf hermes-backup-20260615_0845.tar.gz -C %USERPROFILE%\.hermes
# Then extract supplement (overwrites stale files, adds new ones)
tar xzf hermes-backup-supplement.tar.gz -C %USERPROFILE%\.hermes
```

**Rules for supplement backups:**
- The supplement only contains files that are MISSING from or STALE in the main backup (not duplicates of unchanged files)
- Both archives share the same relative paths — the supplement's files land on top of the main backup's files on extraction
- Update the deployment instruction doc and setup script to mention both files
- The supplement file name should clearly connect to the main backup (e.g., `hermes-backup-supplement.tar.gz`)
- The main backup is never modified — the supplement is regenerated each time

**Why this matters:** Re-compressing a 1GB archive takes 2-5 minutes and uses 2GB+ interim disk space (uncompressed + re-compressed). A supplement is created in seconds and is typically 50-100MB.

### Pitfall: Nested Backup Bloat

If the backup archive itself is stored INSIDE the directory being tar'd (e.g., `青桑/笔记本分身/hermes-backup-*.tar.gz` lives under `青桑/` which is included in the tar), the new backup will contain the old backup(s). This wastes space and creates confusion.

**Symptom:** Running `tar -tzf` on the backup shows:
```
青桑/笔记本分身/hermes-backup-20260613_135243.tar.gz
青桑/笔记本分身/hermes-backup-20260615_0845.tar.gz
```

**Fix:** Add `--exclude=青桑/笔记本分身` to the tar command, or move the backup archive outside the directory being packaged.

### Detailed Audit Procedure

When called to audit the clone backup, follow this procedure:

```
1. Stat the backup tar: ls -lh 青桑/笔记本分身/*.tar.gz
2. List backup contents: tar -tzf <backup>.tar.gz | grep -v '/$\|__pycache__\|\.pyc$'
3. For each key file (.env, config.yaml, *.sh), extract from backup and compare with current
   - diff <(tar -xzf backup -O path) /current/path
4. For mihomo config specifically, check validity:
   - tar -xzf backup -O mihomo/run/config.yaml | grep -q '^proxies:' → warn if missing
   - If script points to a different path, check THAT path exists in the backup
5. Check state.db size delta: compare backup size vs current
6. Summarize findings: list what changed, what's missing, what's critical
```

### Memory Keeping

After completing an audit:
- Record the backup timestamp and file size in memory so the next session can detect drift without re-running the full comparison
- If no issues found, note clone backup state with timestamp
- If issues found, record the specific omissions so the user can verify the fix
