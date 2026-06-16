# "Gateway is shutting down" — Troubleshooting Guide

## Error Text

> Gateway is shutting down and is not accepting another turn right now.

## Meaning

The gateway process received a WeChat message but was in the process of exiting — it couldn't queue or process the turn. The user sees this message instead of an agent response.

## Root Causes (in order of likelihood)

### 1. Working Directory Hang (Most Common)

**Symptom:** Gateway process exists (`ps aux | grep gateway` shows it) but no `gateway_state.json` is ever written. The gateway logs show initialization started but never completed.

**Root cause:** Gateway started from `/opt/data` without `cd /opt/hermes` first. The initialization code hangs (likely deprecation warning printed to a blocking stdout). The process never finishes startup, then exits after a timeout.

**Fix (in the start script):**
```bash
cd /opt/hermes
setsid /opt/hermes/.venv/bin/hermes gateway run --replace --no-supervise < /dev/null > /dev/null 2>&1 &
```

**Check:** If `gateway_state.json` is missing but the process is alive, this is almost certainly the issue.

---

### 2. s6 Restart Loop

**Symptom:** Gateway repeatedly exits and is restarted by s6-supervise. The process tree shows `s6-supervise → hermes gateway run`. The gateway state cycles running/shutdown.

**Check:** `cat /run/service/gateway-default/run` — if it contains `hermes gateway run` (not `sleep infinity`), s6 is managing the process.

**Fix:** See `references/s6-restart-loop.md` — bypass s6 with `sleep infinity` run script + setsid background process.

---

### 3. iLink Connection Drop

**Symptom:** Gateway connects successfully (gateway_state.json shows `connected`), stays up for minutes, then disconnects. The state file updates to `disconnected` or `reconnecting`. During the disconnect window, incoming messages get the "shutting down" response.

**Common triggers:**
- Network transient (WSL host sleep/resume, DNS hiccup)
- iLink server-side timeout (idle connection has ~5-10min TTL)
- Proxy interference — `http_proxy` env vars not unset (iLink is domestic Chinese server, unreachable through overseas proxies)

**Check:**
```bash
env | grep -i proxy
```

Any proxy var set = fix: `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy`

---

### 4. First-Start Race Condition

**Symptom:** You or another user sends a message within seconds of the gateway starting. The gateway hasn't finished initializing yet.

**Fix:** Wait 10-15 seconds after gateway start before sending the first message. Send a simple text message first to "warm up" the session (the first message after startup has extra overhead).

---

## Diagnostic Procedure (in order)

```bash
# 1. Is gateway process alive?
ps aux | grep "hermes gateway run"

# 2. Is state file present?
cat /opt/data/gateway_state.json

# Expected: {"gateway_state": "running", "weixin": {"state": "connected"}, ...}

# 3. Check gateway logs
cat /opt/data/logs/gateways/default/current | tail -30

# Look for: "Gateway Starting", "connected", "disconnected", stack traces

# 4. Check proxy env
env | grep -i proxy

# Any proxy set = likely cause

# 5. Check if s6 is managing
cat /run/service/gateway-default/run

# If contains "hermes gateway run" → s6 is managing (see s6-restart-loop.md)
# If contains "sleep infinity" or file not found → not s6-managed
```

## Process Tree — Healthy State (no s6)

```
PID 1 (s6-svscan)
  └─ sleep infinity  (at /run/service/gateway-default/)
  └─ hermes gateway run --replace --no-supervise  (setsid-d, PPID=1)
```

The gateway is NOT a child of s6-supervise. It's independently launched.
