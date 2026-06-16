---
name: hermes-integration-removal
description: >-
  Systematically remove a Hermes integration (messaging platform, cron job, service) — find all
  components, stop processes, delete files, clean skills, config, and memory.
---

# Hermes Integration Removal

Fully decommission a feature or platform integration from Hermes. Applicable to: gateway platforms
(WeChat, Telegram, Discord, etc.), background services, and self-hosted cron jobs — anything that
spans processes, cron, scripts, skills, config, and memory.

## Systematic Discovery — Find All Components

Before removing, locate every piece. Do not rely on memory — search systematically:

```bash
# 1. Running processes
ps aux | grep -i "hermes.*gateway"      # gateway process
ps aux | grep -i "gateway-watchdog"      # watchdog/keeper process
pgrep -f "hermes gateway run"

# 2. Cron jobs (use the tool)
cronjob action=list
# OR from CLI: hermes cron list

# 3. Scripts on disk
ls /opt/data/青桑/脚本/*gateway* /opt/data/青桑/脚本/*wechat* /opt/data/青桑/脚本/*watchdog* 2>/dev/null

# 4. State/lock files
ls /opt/data/gateway_state.json /opt/data/gateway.lock 2>/dev/null
ls /opt/data/home/.hermes/gateway_state.json 2>/dev/null

# 5. Skills (use tool or CLI)
skills_list   # then search for related skill names
# OR: hermes skills list | grep -i wechat

# 6. Config files
cat ~/.hermes/channel_directory.json   # look for platform entries
grep -i "weixin\|wechat\|gateway" ~/.hermes/config.yaml 2>/dev/null
ls ~/.hermes/weixin/ 2>/dev/null       # platform-specific data dirs

# 7. Log files
ls /opt/data/青桑/每日简报存档/*gateway* /opt/data/青桑/每日简报存档/*watchdog* 2>/dev/null

# 8. Photos / media
ls /opt/data/青桑/photo/*qrcode* /opt/data/青桑/photo/*wechat* 2>/dev/null

# 9. Startup scripts referencing the integration
grep -n "gateway\|微信\|wechat\|weixin\|watchdog" /opt/data/青桑/脚本/startup.sh /opt/data/青桑/脚本/startup-inner.sh 2>/dev/null

# 10. Instruction docs referencing the integration
grep -n "微信\|gateway\|watchdog" /opt/data/青桑/指令/指令.txt 2>/dev/null

# 11. Memory entries (use memory tool — list all and scan)
# memory entries are shown at session start in the MEMORY block
```

## Removal Sequence (order matters)

### Phase 1 — Stop Active Services

```bash
# Kill running gateway process
pkill -f "hermes gateway run" 2>/dev/null

# Kill watchdog process
pkill -f "gateway-watchdog" 2>/dev/null

# Pause/remove cron jobs (use tool)
cronjob action=remove job_id=<id>
```

### Phase 2 — Disable Auto-Restart

Hermes Docker images use s6-overlay to manage services. Killing a gateway process is not enough
— s6-supervise will restart it within seconds.

**Method A — Graceful stop (preferred):**
```bash
s6-svc -wd /run/service/gateway-default/
```

**Method B — Disable run script (most reliable):**
```bash
mv /run/service/gateway-default/run /run/service/gateway-default/run.disabled
s6-svc -d /run/service/gateway-default/ 2>/dev/null
```

**Method C — Startup script guard** (prevents restart on container restart):
Add to `startup.sh` (or the relevant entrypoint script):
```bash
echo "[startup] 禁用 s6 gateway 服务..."
s6-svc -d /run/service/gateway-default/ 2>/dev/null || true
```

### Phase 3 — Delete Infrastructure Files

```bash
# Scripts
rm -v /opt/data/青桑/脚本/start-gateway.sh /opt/data/青桑/脚本/gateway-watchdog.sh

# State/lock files
rm -v /opt/data/gateway_state.json /opt/data/gateway.lock
rm -v /opt/data/home/.hermes/gateway_state.json /opt/data/home/.hermes/gateway.lock

# Logs
rm -v /opt/data/青桑/每日简报存档/gateway-watchdog.log

# Platform data directories
rm -rf ~/.hermes/weixin/

# Associated media (QR codes, etc.)
rm -v /opt/data/青桑/photo/*wechat* /opt/data/青桑/photo/*qrcode*

# Old state files at other candidate paths
rm -v ~/.hermes/gateway_state.json ~/.hermes/gateway.lock 2>/dev/null
```

### Phase 4 — Clean Configuration

```bash
# channel_directory.json — remove the platform entry
python3 -c "
import json
path = '<path-to-channel_directory>'
with open(path) as f:
    d = json.load(f)
d.pop('weixin', None)   # replace 'weixin' with your platform key
with open(path, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
"
```

### Phase 5 — Delete Associated Skills (use tool)

```bash
skill_manage action=delete name=<skill-name> absorbed_into=""
```

### Phase 6 — Clean Memory

Find and remove memory entries that reference the removed integration:
```bash
memory action=remove target=memory old_text="<identifying text>"
```

### Phase 7 — Update Documentation

```bash
# Update 指令.txt to remove references
# Update startup.sh to remove/replace gateway-related steps
```

## Verification

After each phase, verify the component is gone. After all phases, run a comprehensive check:

```bash
echo "=== 1. 进程 ==="
ps aux | grep "hermes gateway" | grep -v grep || echo "✓ 无"
echo "=== 2. cron ==="
hermes cron list 2>/dev/null | grep -i <platform> || echo "✓ 无"
echo "=== 3. 脚本 ==="
ls <script-paths> 2>&1
echo "=== 4. 状态文件 ==="
ls <state-file-paths> 2>&1
echo "=== 5. 技能 ==="
hermes skills list 2>/dev/null | grep -i <platform> || echo "✓ 无"
echo "=== 6. 数据目录 ==="
ls ~/.hermes/<platform-dir>/ 2>&1
echo "=== 7. channel_directory ==="
cat ~/.hermes/channel_directory.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('<platform>' in d and '× 还在' or '✓ 已清')" 2>/dev/null
echo "=== 8. 文档引用 ==="
grep "<platform>" /opt/data/青桑/指令/指令.txt || echo "✓ 无"
echo "=== 9. s6 服务 ==="
s6-svstat /run/service/gateway-default/ 2>/dev/null
```

## Pitfalls

- **s6-supervise persists after `s6-svc -d`.** The supervisor process itself stays alive and may
  rewrite state files. Always rename the run script (`run → run.disabled`) as a backup measure.
- **Multiple state file locations.** Gateway writes state based on runtime `HOME`. Check at least
  three candidate paths: `/opt/data/`, `/opt/data/home/.hermes/`, and `~/.hermes/`. Pick the
  freshest `updated_at`.
- **Skills survive in the library.** Even if processes are killed, the skill remains loadable and
  will guide future sessions to use the now-deleted integration. Delete skills explicitly.
- **Memory persists across sessions.** Memory entries that describe the integration's setup will
  cause future sessions to reference it. Clean them proactively.
- **Docker container restart re-enables s6 services.** Adding a guard to the startup script
  (`s6-svc -d /run/service/gateway-default/`) is essential for durability.
- **Channel directory stale entries.** Even after gateway deletion, `channel_directory.json` may
  retain empty platform entries (`"weixin": []`). Clean them manually — they won't cause errors but
  are misleading.
