---
name: wechat-gateway
description: Manage the WeChat (微信) gateway lifecycle — setup, s6 integration, watchdog, token refresh, and troubleshooting.
category: devops
---

# WeChat Gateway Management

Manage the Hermes WeChat gateway — the messaging bridge that delivers agent responses to your WeChat via iLink Bot (ClawBot). The authoritative setup guide is at the [Amaranth Wiki: 微信接入](https://wiki-for-amaranth.pages.dev/hermes-agent/wechat-gateway/).

## Architecture

| Component | Role | Location |
|-----------|------|----------|
| **s6 service** | Manages gateway lifecycle (auto-start on container boot, auto-restart on crash) | `/run/service/gateway-default/` |
| **Gateway process** | Persistent Python process connecting to WeChat iLink | `hermes gateway run` via s6 |
| **Cron watchdog** | Backup health check every 5 min (if s6 fails) | cron `wechat-gateway-watchdog` |
| **start-gateway.sh** | Script to start gateway manually or via cron | `/opt/data/青桑/脚本/start-gateway.sh` |
| **.env credentials** | WEIXIN_ACCOUNT_ID, WEIXIN_TOKEN, etc. | `~/.hermes/.env` (mounted from Windows host) |
| **State file** | JSON with gateway_state + weixin.state | `/opt/data/gateway_state.json` |

## Setup (Following Wiki)

### Step 1: Get Credentials (QR Code)

```bash
# Must unset proxy before any iLink API call
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# Generate QR code
curl -s "https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3"
# Returns: {"qrcode": "...", "qrcode_img_content": "...", "ret": 0}

# Generate QR image from qrcode_img_content
# Use quickchart.io — api.qrserver.com is blocked in China
python3 -c "
import urllib.request, urllib.parse
qr_url = '<qrcode_img_content from above>'
api_url = 'https://quickchart.io/qr?text=' + urllib.parse.quote(qr_url) + '&size=300'
req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req, timeout=15).read()
with open('/opt/data/青桑/photo/wechat_qrcode.png', 'wb') as f: f.write(data)
print(f'OK: {len(data)} bytes, PNG={data[:4]==b\"\\x89PNG\"}')"

# Poll for scan result (long-poll, ~30s timeout)
curl -s "https://ilinkai.weixin.qq.com/ilink/bot/get_qrcode_status?qrcode=<qrcode>"
# Status flow: wait → scaned → confirmed
# Returns: ilink_bot_id, bot_token, baseurl, ilink_user_id
```

### Step 2: Configure .env

```bash
cat >> ~/.hermes/.env << 'EOF'

# WeChat iLink Bot
WEIXIN_ACCOUNT_ID=xxx@im.bot
WEIXIN_TOKEN=xxx@im.bot:hex字符串
WEIXIN_BASE_URL=https://ilinkai.weixin.qq.com
WEIXIN_CDN_BASE_URL=https://novac2c.cdn.weixin.qq.com/c2c
WEIXIN_DM_POLICY=pairing
WEIXIN_ALLOW_ALL_USERS=true
EOF
```

**Note:** Token contains `@` and `:`, so `cat >>` append is safe, but `export $(cat .env | xargs)` WILL truncate it. Use Python to update .env:

```python
import os, re
env_path = '/opt/data/.env'
with open(env_path) as f: content = f.read()
updates = {
    'WEIXIN_ACCOUNT_ID': '<ilink_bot_id>',
    'WEIXIN_TOKEN': '<bot_token>',
    'WEIXIN_BASE_URL': 'https://ilinkai.weixin.qq.com',
    'WEIXIN_CDN_BASE_URL': 'https://novac2c.cdn.weixin.qq.com/c2c',
    'WEIXIN_DM_POLICY': 'pairing',
    'WEIXIN_ALL_ALL_USERS': 'true',
}
for key, val in updates.items():
    pattern = re.compile(r'^' + re.escape(key) + r'=.*$', re.MULTILINE)
    if pattern.search(content): content = pattern.sub(f'{key}={val}', content)
    else: content += f'\n{key}={val}'
with open(env_path, 'w') as f: f.write(content)
```

### Step 3: Fix s6 Run Script

The Docker image ships s6-overlay managing `gateway-default`. Add `unset proxy` and ensure correct permissions:

```bash
# Path: /run/service/gateway-default/run
#!/command/with-contenv sh
set -e
export HOME=/opt/data
cd /opt/data
. /opt/hermes/.venv/bin/activate
export HERMES_S6_SUPERVISED_CHILD=1
# WeChat iLink needs direct connection (proxy can't reach weixin.qq.com)
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy
[ "$(id -u)" = 0 ] || exec hermes gateway run
exec s6-setuidgid hermes hermes gateway run
```

**CRITICAL:** The run script MUST have 755 permissions (`chmod 755`). 600 permissions cause silent failure (s6 marks service as "down" with no useful error).

### Step 4: Start via s6

```bash
s6-svc -u /run/service/gateway-default/
# Check: s6-svstat /run/service/gateway-default/
# Should show: "up (pid X) N seconds"

# Check connection:
cat /opt/data/gateway_state.json | python3 -m json.tool
# Expected: "gateway_state": "running", "weixin": {"state": "connected"}
```

### Step 5: Set Up Cron Watchdog (Backup)

```bash
# Script: ~/.hermes/scripts/start-gateway.sh
# Cron: every 5 min, no_agent=true, script=start-gateway.sh, deliver=local
```

The cron watchdog is a safety net. s6 handles the primary lifecycle; the watchdog catches cases where s6 itself dies.

## Manual Start (Without s6)

When s6 is unavailable or you need to test:

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy
cd /opt/hermes  # Prevent working directory hang
setsid /opt/hermes/.venv/bin/hermes gateway run --replace --no-supervise < /dev/null > /dev/null 2>&1 &
```

The `cd /opt/hermes` is important — starting from `/opt/data` can cause a blocking hang during initialization (deprecation warning printed, state file never written).

### Token Persistence

Credentials in `.env` survive container lifecycles because `.env` is mounted from the Windows host via `--env-file`. When restarting the container, the gateway will use the existing token. **No need to re-scan QR unless the token expires.**

When token expires (weixin.state stays "disconnected" with no error), follow Step 1 again to generate new QR and get fresh credentials.

### Image/Media Support (WeChat → Agent)

The WeChat iLink gateway **does support receiving images** from users, despite common assumptions. Confirmed from gateway logs (`media=1` flag):

```
[Weixin] inbound from=o9cq802Z type=dm media=1
Image routing: text (mode=text). Pre-analyzing 1 image(s) via vision_analyze.
```

When a user sends an image via WeChat DM:
1. Gateway detects `media=1` and downloads the image via WeChat CDN
2. Auto-routes to `vision_analyze` for server-side image understanding
3. Forwards the vision analysis result as text to the conversation session

**Limitations:**
- The analysis result goes to the WeChat-originated session only — the CLI session won't see the original image
- Gateway restarts invalidate the upload context_token — wait 1-2 min after restart before sending images
- First message after restart: send a text first to rebuild session context

**Troubleshooting when images don't seem to work:**
1. Check gateway log: `grep "media=1\|Image routing\|vision_analyze" /opt/data/logs/gateway.log`
2. If `media=1` appears, the image was received and analyzed
3. If no `media=1`, the gateway may not be forwarding the message type

## Common Error: "Gateway is shutting down and is not accepting another turn"

See `references/gateway-shutdown-error.md` for a full diagnostic procedure. The most common cause is starting the gateway from the wrong working directory (`/opt/data` instead of `/opt/hermes`) — the init hangs and the gateway never writes `gateway_state.json`.

## Draining State (Root Execution)

**Symptom:** WeChat is connected (`weixin.state: "connected"`) and the gateway process is alive, but messages get rejected with "Gateway is shutting down." The state file shows `gateway_state: "draining"`.

**Root cause:** The Docker entrypoint was overridden (e.g., `bash startup.sh` instead of the official `entrypoint.sh`), so the gateway runs as **root**. Hermes v0.16.0+ enters a self-protection draining mode when running as root inside the official image — it stays connected but refuses to process turns.

**This is NOT the s6 restart loop.** In draining mode:
- The gateway stays up (PID doesn't cycle)
- WeChat shows connected
- No repeated "Gateway Starting" in logs
- Only one or two "Refusing to run as root" entries in the log

**Fix:** Recreate the container with `-e HERMES_ALLOW_ROOT_GATEWAY=1`:
```powershell
docker stop hermes
docker rm hermes
docker run -d --restart unless-stopped --name hermes `
  -v "$env:USERPROFILE\.hermes:/opt/data" `
  --env-file "$env:USERPROFILE\.hermes\.env" `
  -e ... -e HERMES_ALLOW_ROOT_GATEWAY=1 `
  nousresearch/hermes-agent:latest `
  bash /opt/data/.../startup.sh
```

**Verification:** After fix, `gateway_state` should show `"running"` (not `"draining"`).

## Pitfalls

- **Proxy kills iLink:** `ilinkai.weixin.qq.com` is a domestic Chinese server — it's unreachable through overseas proxies. Always `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY` before any iLink API call or gateway launch.
- **s6 run script permissions:** Must be 755. If it's 600, s6-supervise marks the service as "down" immediately with no useful log.
- **Working directory hang:** Starting the gateway from `/opt/data` can cause an initialization hang. Always `cd /opt/hermes` first.
- **Token format:** `WEIXIN_TOKEN` is `bot_id:hex_string`. The `:` and `@` in the value break naive env loading. Use Python to parse, not `export $(cat .env | xargs)`.
- **QR code TTL:** QR codes expire in ~2 minutes. Generate, scan, and poll promptly.
- **Image send failure after restart:** gateway restart invalidates the upload context_token. Send a text message first to rebuild the session before sending images. Wait 1-2 minutes after restart.
- **no_agent cron scripts:** Must be placed in `~/.hermes/scripts/` and referenced by filename only (not absolute path).
- **`nohup` vs `setsid`:** `nohup` does NOT fully detach the process from the terminal session — the gateway can still hang on stdout/stderr flush at exit. Always use `setsid` for the gateway launch (as documented in Manual Start). If `start-gateway.sh` uses `nohup`, replace with `setsid` + `cd /opt/hermes`.
- **`.env` HTTP_PROXY overrides shell unset:** The `start-gateway.sh` script unsets proxy vars, but `load_hermes_dotenv()` in Python re-loads them from `.env` at startup. If `.env` contains `HTTP_PROXY=http://127.0.0.1:7890`, the gateway will inherit the proxy and fail to connect to `ilinkai.weixin.qq.com`. **Fix:** Remove `HTTP_PROXY`/`HTTPS_PROXY` from `.env`. Use wrapper scripts (like `run_gateway.sh`) that export the vars explicitly, OR add the proxy env only in the CLI session context (not in .env).
- **`s6-svc` not in PATH:** The `s6-svc` binary may be at `/package/admin/s6-<version>/command/s6-svc`. Find it with `find / -name "s6-svc" -type f 2>/dev/null | head -3`.
- **start-gateway.sh missing `cd /opt/hermes`:** The watchdog script (`start-gateway.sh`) may start the gateway from an unspecified working directory (defaults to `/opt/data` or crond cwd). This causes the initialization hang — no `gateway_state.json` is ever written. The script MUST `cd /opt/hermes` before launching the gateway process.
- **s6-svstat not found:** Some Docker images may have s6 run scripts but not s6 tools in PATH. To check s6 gateway status when `s6-svstat` is unavailable: inspect `/run/service/gateway-default/run` for `sleep infinity` (s6 bypassed) vs `hermes gateway run` (s6 managing), and cross-check with `ps aux | grep "hermes gateway"`.

## s6 Gateway Restart Loop Bug

**Symptom:** The WeChat connection repeatedly drops and reconnects, flooding the conversation with "gateway shutdown/interruption" system notes. User sees you "constantly typing" as the gateway cycles.

**Root cause:** s6-supervise manages the gateway process and restarts it whenever it exits. The gateway exits ~14s–8min after starting under s6 (likely iLink connection timeout or health-check exit). Each restart drops the WeChat connection, then reconnects — generating an interruption each time. Logs show 7+ restarts in 20 minutes.

**Why others don't have this:** Most Hermes users run the gateway directly via `hermes gateway run --replace --no-supervise` without s6 supervision. The Docker s6-overlay is specific to this deployment. The s6-managed pattern is inherently less stable for iLink gateways.

**User confusion handling:** When the user sees these "gateway shutdown/interruption" system notes in chat, they will naturally think the connection is actually broken and ask "为什么总在反复重连？" or "你怎么说没在运行？" or "不是后台运行吗为什么我一关掉Hermes CLI就断开链接了？". The correct response:

1. **Acknowledge the confusion:** The system notes are internal Hermes process logs (s6 restart events) that leaked into the conversation display — they are NOT actual connection failures.
2. **Clarify CLI vs daemon:** The gateway is managed by s6-supervise inside the Docker container. Closing the PowerShell/terminal window (which ran `docker exec -it hermes bash`) does NOT affect the container or the gateway. The container runs with `docker run -d --restart unless-stopped` — it stays alive independently. If the gateway drops when you close something, you're likely running the gateway directly (not via Docker daemon mode).
3. **Reassure:** The WeChat gateway connection is actually still working. You and the user are communicating normally.
4. **Explain (if asked):** This is a known behavior of the s6-supervised Docker deployment where the gateway exits and restarts frequently, generating interruption events. The fix (bypass s6, use setsid + cron) is already in place.
5. **Don't over-explain:** If the user just asks "你现在通着吗？", answer directly that you are connected and chatting normally. Only explain s6 internals if they ask further.

**Key phrasing:** "那些是 Hermes 服务端内部的日志，被错误地注入了聊天记录里，但实际连接并没有中断——我们现在就在正常聊天。"

**Fix (bypass s6, use setsid + cron):**

```bash
# 1. Replace s6 run script with sleep infinity (disables s6 management)
cat > /run/service/gateway-default/run << 'SCRIPT'
#!/command/with-contenv sh
exec sleep infinity
SCRIPT
chmod 755 /run/service/gateway-default/run

# 2. Start gateway independently as background process
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy
rm -f /opt/data/gateway_state.json /opt/data/home/.hermes/gateway_state.json 2>/dev/null
cd /opt/hermes
setsid /opt/hermes/.venv/bin/hermes gateway run --replace --no-supervise < /dev/null > /dev/null 2>&1 &

# 3. Set up cron watchdog (5 min check)
cronjob action=create \
  prompt='' \
  schedule='every 5m' \
  name='wechat-gateway-watchdog' \
  script='start-gateway.sh' \
  no_agent=true \
  deliver=local
```

**CRITICAL: Fix does not survive container restart.** After `docker rm` + `docker run` (e.g. to pull a new image), s6 returns to its default state. The user may believe s6 is "already disabled" from a previous session, but `ps aux` will show s6-supervise `gateway-default` running again. Use `ps aux | grep -E "s6|gateway" | grep -v grep` to verify actual state. See `s6-service-management` skill → `references/verify-service-state.md` for the full diagnostic procedure. After `docker restart`, s6 re-creates the run script with the original gateway-run content (or the gateway itself rewrites it at ~14s post-boot). The fix must be reapplied after each restart. Options:
- **Manual reapply:** run the fix commands each time after restart
- **Startup script:** add the fix to a pre-boot hook or startup.sh that runs before s6 launches
- **Watchdog dependency:** the cron watchdog (`start-gateway.sh`) detects when the gateway is down and starts it independently — but if s6 is still managing it, the processes conflict. The s6 bypass MUST be in place for the watchdog to work correctly.

**Verification:**
- Check `ps aux | grep -E 'gateway|s6-supervise.*gateway'`: the gateway process should be a child of PID 1 (s6-svscan) via s6-supervise if s6 is managing it. To check bypass is working, verify the run script contains `sleep infinity` and the gateway process is NOT under s6-supervise.
- Check `cat /run/service/gateway-default/run` for `sleep infinity` marker.
- Check gateway log `/opt/data/logs/gateways/default/current` for excessive "Gateway Starting" entries (>1 per 10 min = problem).

## Verification

- [ ] s6-svstat /run/service/gateway-default/ → up
- [ ] cat /opt/data/gateway_state.json → gateway_state: running, weixin.state: connected
- [ ] ps aux | grep hermes gateway → PID matches state file
- [ ] Send a test text message via WeChat and confirm response

## Sending Messages to WeChat

The send_message tool delivers agent messages to the WeChat user. Two conditions must be met:

1. WEIXIN_HOME_CHANNEL env var — The send_message tool checks os.getenv(WEIXIN_HOME_CHANNEL) as a fallback (in send_message_tool.py lines 374-378). This env var must be set BEFORE the CLI or gateway process starts. Add it to a wrapper script:
   export WEIXIN_HOME_CHANNEL=o9cq802ZAibV-JIFIUS2MPTdimUo@im.wechat
   hermes gateway run

2. Gateway must be running — The gateway process handles message delivery.

Diagnosing send failures:
- If send_message returns "No home channel set for weixin", the CLI process doesn't have WEIXIN_HOME_CHANNEL in its environment. Fix: Kill the CLI process and restart, or set the var in the parent shell before launching Hermes.

Example wrapper script (/opt/data/mihomo/run_gateway.sh):
  #!/bin/bash
  export WEIXIN_HOME_CHANNEL=o9cq802ZAibV-JIFIUS2MPTdimUo@im.wechat
  cd /opt/hermes
  exec .venv/bin/hermes gateway run
