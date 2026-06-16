---
name: s6-service-management
description: Manage s6-overlay supervised services inside the Hermes Docker container — list, stop, restart, permanently disable, and re-enable services.
category: devops
---

# s6 Service Management (Hermes Docker Container)

The Hermes Docker image ships with s6-overlay to supervise built-in services. These run under `s6-supervise` and auto-restart when killed — `pkill` is not enough. To permanently stop a service, you must disable the s6 supervision itself.

## Key Fact

`s6-svc -d` (down) tells s6-supervise to stop the service, but s6-supervise itself survives. If the service's `run` script still exists, s6 will bring it back up again (eventually or immediately depending on notification-fd settings).

**To permanently disable:** rename the `run` script so s6 can't execute it.

## Commands

### List services

```bash
ls /run/service/
```

Common services: `gateway-default`, `main-hermes`, `dashboard`.

### Stop a service (temporary)

```bash
s6-svc -d /run/service/<name>/
```

The service stops but s6-supervise stays alive. On container restart the service comes back.

### Permanently disable a service

```bash
mv /run/service/<name>/run /run/service/<name>/run.disabled
s6-svc -d /run/service/<name>/
```

Now s6-supervise has no `run` script to execute. The service stays down even across `s6-svc -u` attempts.

### Re-enable a service

```bash
mv /run/service/<name>/run.disabled /run/service/<name>/run
s6-svc -u /run/service/<name>/
```

### Check service state

```bash
s6-svstat /run/service/<name>/
```

Output: `up (pid N) N seconds` or `down (exitcode N) N seconds, normally up, ready N seconds`.

## Startup Hook Pattern

To ensure a service stays disabled across container restarts, add the disable command to the container's startup script (e.g. `startup.sh`) **before** the Hermes CLI exec:

```bash
s6-svc -d /run/service/gateway-default/ 2>/dev/null || true
```

Note: this is a soft disable (not renaming the run script) — it works because startup.sh runs after s6 has initialized but before the service has fully started. If s6 starts faster, the `run.disabled` rename is more reliable.

## Full Recovery: Re-enabling a Disabled Service

If you renamed the run script and need to restore it:

```bash
# Check what's disabled
ls /run/service/*/run.disabled 2>/dev/null

# Restore
mv /run/service/gateway-default/run.disabled /run/service/gateway-default/run
s6-svc -u /run/service/gateway-default/
```

## Windows Docker: flock() on Bind Mounts

When Hermes runs in Docker on Windows (WSL2 backend) and `/opt/data` is a host bind mount (e.g., `%USERPROFILE%\\.hermes:/opt/data`), **s6-log may fail to acquire its file lock**.

**Symptom:** On container init, `docker logs` shows:

```
s6-log: fatal: unable to lock /opt/data/logs/gateways/default/lock: Resource busy
```

**Root cause:** s6-log uses POSIX `flock()` to ensure exclusive write access to its log directory. The lock file lives at `/opt/data/logs/gateways/<service>/lock`. But `/opt/data` is a Windows NTFS volume mounted via WSL2's **DrvFs** (9P protocol), which does NOT properly support POSIX advisory file locking. The `flock()` call returns `EAGAIN`/`EWOULDBLOCK` → s6-log exits with "Resource busy."

**See also** `windows-devops` skill for general Windows Docker constraints.

## Impact

**None.** This error is:

- **Transient** — Only fires during container initialization when s6 is starting up and competing for the lock. Once s6-log is running (verify with `ps aux | grep s6-log`), it won't re-fire until the next container restart.
- **Harmless** — The gateway process (`hermes gateway run`) runs independently of its log supervisor. Even if s6-log fails to lock, the gateway continues to function normally (WeChat connection, message processing, etc.).
- **Cosmetic** — You see it in `docker logs` output or Docker Desktop's log viewer because s6-svscan (PID 1) emits it to stderr, which Docker captures. It does NOT affect the running container.

## Fix

**Option A: Ignore** (recommended) — the error is cosmetic and the gateway works fine.

**Option B: Move log output to a container-internal path** — Modify the s6 log `run` script to write to `/var/log/` (not the bind mount). Requires editing `/run/service/<name>/log/run` inside the container. This only lasts until the container is recreated (e.g., `docker rm` + `docker run`).

**Option C: Disable s6 log sub-supervisor** — Rename the log `run` script to disable it:

```bash
mv /run/service/gateway-default/log/run /run/service/gateway-default/log/run.disabled
s6-svc -d /run/service/gateway-default/log/
```

Gateway logs will go to the container's stdout/stderr instead (visible via `docker logs`). Downside: no file-based log rotation, and the change is lost on container recreate.

## Reference: Verifying Service State vs Expected State

See `references/verify-service-state.md` for the complete diagnostic guide — process tree inspection, run script checks, edge cases where user-intended state differs from actual running state (common after container recreate), and specific commands from a live debugging session.

## Pitfalls

- **`s6-svc -d` alone is not permanent** — the service returns after container restart.
- **`run.disabled` only works until `docker rm`** — when you delete and recreate the container, you get a fresh image with the original run script. The rename must be re-applied.
- **Multiple s6-supervise for one service** — some services have a `/log` sub-supervisor (e.g. `gateway-default/log`). Disabling the main one stops the log too.
- **`pkill -f "hermes gateway"` can kill the current agent session** if the agent is also a `hermes` process. Use explicit PIDs or target-specific patterns (`pgrep -f "hermes gateway run"`) instead.
- **s6 state files persist** — even after disabling the service, stale state files (e.g. `gateway_state.json`) written by the service before shutdown remain on disk. Clean them manually.
- **User intention ≠ actual s6 state after container recreate.** The user may have disabled s6-supervise (`run.disabled`) in an earlier container, but after `docker rm` + `docker run` (new container from image), s6 comes back with the default run scripts. When debugging, always check the actual process tree (`ps aux | grep s6-supervise`), never trust what "was done before".
