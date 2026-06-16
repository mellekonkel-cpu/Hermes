# s6 Gateway Run Script Fix

## The Script

Path: `/run/service/gateway-default/run`

```bash
#!/command/with-contenv sh
# shellcheck shell=sh
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

## Key Fixes

### 1. Proxy Unset (Line 9)
The Docker container may have proxy env vars set globally. iLink servers are domestic Chinese — unreachable via overseas proxies. Without `unset`, the gateway starts but never connects to WeChat.

### 2. Permissions (CRITICAL)
```
chmod 755 /run/service/gateway-default/run
```
s6-supervise requires the run script to be executable. If permissions are 600 (common when created by `write_file` tool), s6 marks the service as `down (exitcode 1)` immediately with no useful error in logs.

### 3. `--no-supervise` NOT needed here
The `--no-supervise` flag is only for manual gateway starts outside s6. When s6 manages it, the flag is implicit — s6 IS the supervisor.

## Restoration

If the run script was renamed/disbled:
```bash
# Restore from .disabled
mv /run/service/gateway-default/run.disabled /run/service/gateway-default/run
chmod 755 /run/service/gateway-default/run

# Or recreate from scratch (see script above)

# Start
s6-svc -u /run/service/gateway-default/

# Verify
s6-svstat /run/service/gateway-default/
cat /opt/data/gateway_state.json
```
