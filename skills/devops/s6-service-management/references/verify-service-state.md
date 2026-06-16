# Verifying s6 Service State vs Expected State

When debugging s6-managed services inside the Hermes Docker container, the configured state (e.g., "s6 is disabled" / "using setsid + cron watchdog") may differ from the actual running state. This is common after container recreation (`docker rm` + `docker run`) because s6 run scripts inside the image are restored to defaults.

## Process Tree Inspection

The container's PID 1 is always `s6-svscan`. List all s6-supervise instances and their children:

```bash
ps aux | grep -E "s6|gateway" | grep -v grep
```

**Healthy output (s6 managing both service + log):**
```
root         1  s6-svscan                     # PID 1, init supervisor
root        28  s6-supervise main-hermes       # Main Hermes session
root        29  s6-supervise dashboard         # Dashboard
root       135  s6-supervise gateway-default   # Gateway service
hermes     139  hermes gateway run             # ← actual gateway process (child of 135)
root       137  s6-supervise gateway-default/log  # Gateway log sub-supervisor
hermes     141  s6-log ... gateways/default    # ← s6-log (child of 137)
root       140  s6-supervise gateway-worker/log   # Worker log sub-supervisor
hermes     143  s6-log ... gateways/worker     # ← worker s6-log (child of 140)
```

**Bypassed output (s6 bypassed, standalone gateway):**
```
root         1  s6-svscan
root       135  s6-supervise gateway-default   # s6 manages, but run script = sleep infinity
hermes     139  hermes gateway run              # ← gateway NOT under s6 (different parent)
# No gateway-default/log sub-supervisor (or it's also bypassed)
```

## Checking the s6 Run Script

```bash
cat /run/service/gateway-default/run
```

- **s6 managing:** contains `hermes gateway run` → gateway births as child of s6-supervise
- **Bypassed:** contains `sleep infinity` → s6 does nothing, gateway runs independently

Same check for log sub-supervisor:
```bash
cat /run/service/gateway-default/log/run
```

## Checking s6-svstat

```bash
s6-svstat /run/service/gateway-default/
```

- `up (pid N) N seconds` — s6 believes it's managing the service
- `down (exitcode N) N seconds, normally up` — service is stopped (or run script is `sleep infinity` which still counts as "up")

## Edge Cases

| Observed State | Likely Cause |
|---|---|
| s6 run script shows `sleep infinity` but gateway process also exists | Startup script (`start-gateway.sh`) or cron watchdog started the gateway independently — expected bypass pattern |
| s6 run script shows `hermes gateway run` AND `start-gateway.sh` ran successfully | BOTH s6 and setsid are trying to manage the gateway. `start-gateway.sh` checks `pgrep -f "hermes gateway run"` first, so if s6 already started it, the script exits without doing anything. If s6 starts it AFTER the script, you get two gateway processes — the second one will fail to bind. |
| s6 run script disabled (`run.disabled`) but gateway is running | The `startup.sh` or watchdog started it independently. Verify gateway's PPID is not s6-supervise. |
| "s6 is disabled" in memory but `ps aux` shows s6-supervise gateway-default running | Container was recreated since the disable was done. Default image restores s6 run scripts. Re-disable needed. |

## Diagnosing flock() Errors on Windows

When `/opt/data` is a Windows host bind mount:

```bash
# Check lock file
ls -la /opt/data/logs/gateways/default/lock   # Usually 0 bytes on DrvFs
file /opt/data/logs/gateways/default/lock      # Shows: empty

# If s6-log is running successfully:
ps aux | grep s6-log                           # PID exists, State=S (sleeping)

# Container logs showing the error:
s6-log: fatal: unable to lock .../lock: Resource busy
```

See the parent SKILL.md section "Windows Docker: flock() on Bind Mounts" for root cause and mitigation.
