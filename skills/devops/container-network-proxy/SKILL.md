---
title: Container Network Proxy
name: container-network-proxy
description: Deploy and manage network proxy services (mihomo, Clash derivatives) in restricted containers without root/apt-get. Covers binary download, configuration with subscription links, background daemon management, and proxy verification.
trigger: User asks to set up external network access, proxy, tunnel, or "外网访问" in a container environment; or needs to route traffic through a proxy; or provides a Clash/subscription link.
---

# Container Network Proxy

Deploy a proxy daemon (mihomo / Clash Meta) in a container with no root access, no apt-get, and no Docker socket. The proxy enables external network access (翻墙/科学上网) for the container.

## Prerequisites

- Container environment (Debian, Alpine, etc.) — any distribution works
- No root required — binaries run as the container user
- Network (curl) must be available for downloading binaries and subscription configs
- Architecture detection: `uname -m` (x86_64, aarch64, etc.)

## Steps

### 1. Detect CPU capabilities

```bash
uname -m                     # architecture
grep flags /proc/cpuinfo | head -1  # check for avx2/bmi1/bmi2 -> supports v3
```

For x86_64:
- **v3** (has AVX2, BMI1, BMI2) → use `mihomo-linux-amd64-v3-*.gz`
- **v2** (has SSE4.1/4.2, POPCNT) → use `mihomo-linux-amd64-v2-*.gz`
- **v1** (basic) → use `mihomo-linux-amd64-compatible-*.gz`

### 2. Download binary from GitHub releases

```bash
mkdir -p /opt/data/mihomo/{config,run,ui}
```

**China network note:** GitHub releases are often blocked by the GFW. Use a mirror:

```bash
# Direct (if accessible)
curl -L -o mihomo.gz "https://github.com/MetaCubeX/mihomo/releases/download/v1.19.27/mihomo-linux-amd64-v3-v1.19.27.gz"

# Via China mirror (ghproxy.net)
curl -L -o mihomo.gz "https://ghproxy.net/https://github.com/MetaCubeX/mihomo/releases/download/v1.19.27/mihomo-linux-amd64-v3-v1.19.27.gz"

# Verify
gunzip mihomo.gz && chmod +x mihomo
./mihomo -v   # should print "Mihomo Meta vX.Y.Z linux amd64"
```

Check latest version at https://github.com/MetaCubeX/mihomo/releases — use the latest stable release.

### 3. Determine subscription format and config strategy

The user provides a subscription link. There are **two fundamentally different strategies** depending on the format:

### 3A. Strategy A: proxy-provider (preferred for large/updating subscriptions)

If the subscription returns **base64-encoded proxy URLs** (trojan://, vless://, vmess://, ss:// etc., not Clash YAML), use Mihomo's `proxy-providers` feature to pull the subscription dynamically. This avoids manual config building and enables auto-updates.

**Detect the format:**

```bash
# Step A: Save raw subscription output to backup first
curl -s -o config/raw_sub.yaml \
  -H "User-Agent: clash" \
  "https://api.example.com/sub?target=clash&url=..."

head -c 200 config/raw_sub.yaml
# If it's < 5KB and has no "port:" or "proxies:" lines → base64-encoded
# Test decode:
head -1 config/raw_sub.yaml | python3 -c "import base64,sys; d=base64.b64decode(sys.stdin.read().strip()); print(d[:200].decode())"
```

**Build proxy-provider config instead of manual node definition:**

```yaml
port: 7890
socks-port: 7891
mixed-port: 7892
redir-port: 7893
allow-lan: false
mode: rule
log-level: info
external-controller: 0.0.0.0:9090
external-ui: ui
secret: ""
ipv6: false

proxy-providers:
  provider1:
    type: http
    url: "https://your-subscription-url-here"
    interval: 3600           # auto-refresh every hour
    health-check:
      enable: true
      url: http://www.gstatic.com/generate_204
      interval: 300

proxy-groups:
  - name: "Proxy"
    type: select
    use:
      - provider1
    proxies:
      - "Auto"
      - DIRECT

  - name: "Auto"
    type: url-test
    use:
      - provider1
    url: http://www.gstatic.com/generate_204
    interval: 300
    tolerance: 50

rules:
  - DOMAIN-SUFFIX,example.com,DIRECT       # <-- IMPORTANT: bypass proxy for subscription domain
  - GEOIP,CN,DIRECT
  - MATCH,Proxy
```

**⚠️ CRITICAL: Add DOMAIN-SUFFIX rule for subscription domain before GEOIP** — The proxy-provider fetches the subscription URL through mihomo itself. If the subscription domain is NOT routed DIRECT, mihomo will try to use the provider's nodes to fetch the provider's own subscription — a chicken-and-egg deadlock. Always add `- DOMAIN-SUFFIX,<provider-domain>,DIRECT` at the top of rules, before GEOIP.

**Decode and inspect the base64 content to verify nodes loaded:**

```python
import base64, urllib.parse
with open('config/raw_sub.yaml') as f:
    raw = f.read().strip()
lines = base64.b64decode(raw).decode().strip().split('\n')
for i, line in enumerate(lines):
    name = urllib.parse.unquote(line.split('#')[-1]) if '#' in line else 'unknown'
    print(f'{i+1}. {name}')
    if line.startswith('vless://'):
        rest = line[8:]
        userinfo, rest = rest.split('@', 1)
        hostport, rest = rest.split('?', 1)
        host, port = hostport.rsplit(':', 1)
        params = dict(urllib.parse.parse_qsl(rest.split('#')[0]))
        print(f'   Host: {host}:{port}')
        print(f'   Type: {params.get("type","tcp")}')
        print(f'   Security: {params.get("security","none")}')
        print(f'   Flow: {params.get("flow","")}')
        print(f'   PBK: {params.get("pbk","")[:20]}...')
    elif line.startswith('trojan://'):
        rest = line[9:]  # strip trojan://
        # trojan://password@host:port?allowInsecure=1&peer=sni&fp=chrome#name
        password, rest = rest.split('@', 1)
        hostport, rest = rest.split('?', 1)
        host, port = hostport.rsplit(':', 1)
        params = dict(urllib.parse.parse_qsl(rest.split('#')[0]))
        print(f'   Host: {host}:{port}')
        print(f'   Password/ID: {password[:20]}...')
        print(f'   SNI: {params.get("sni","")}')
        print(f'   Peer: {params.get("peer","")}')
    elif line.startswith('vmess://'):
        # vmess:// is base64-encoded JSON
        import json
        try:
            vconf = json.loads(base64.b64decode(line[8:]).decode())
            print(f'   Host: {vconf.get("add","?")}:{vconf.get("port","?")}')
            print(f'   Type: {vconf.get("type","tcp")}')
        except:
            print(f'   (vmess parse error)')
```

### 3B. Strategy B: static config (for manually built or single-node setups)

If the subscription returns **valid Clash YAML** or the user provides a single node manually, use the traditional approach below.

**Download and validate:**

```bash
# Save raw subscription output to backup
curl -s -o config/raw_sub.yaml \
  -H "User-Agent: clash" \
  "https://api.example.com/sub?target=clash&url=..."

# Validate — check if it's valid YAML with proxies
head -5 config/raw_sub.yaml
# Expect: port:, socks-port:, proxies:, etc.
# If it says "no valid node info", "404", or is empty — the subscription is dead

# Copy to active config only if valid
cp config/raw_sub.yaml run/config.yaml
```

If it's vless:// links from a raw subscription, you may need to **build config.yaml manually** — see `references/vless-reality-config-template.md`.

### 3C. Subscription metadata lines (info-only, not proxies)

Providers often encode metadata as fake proxy URLs at the top of the base64 output. The first 3 lines are typically:
1. `剩余流量：XXX GB`
2. `距离下次重置剩余：XX 天`
3. `套餐到期：YYYY-MM-DD`

These share the same UUID/host/port as real nodes but differ only in the name. **Do NOT filter them out** — mihomo's proxy-provider handles them gracefully. They'll appear as selectable "nodes" in the API but won't break anything.

### 3D. Switching from static config to proxy-provider

When replacing an existing static config (manually defined proxies) with a proxy-provider subscription:

1. Remove the entire `proxies:` block (manually defined nodes)
2. Add `proxy-providers:` block with the subscription URL
3. Change `proxy-groups` from listing individual `proxies:` to using `use:` referencing the provider name
4. Add a `DOMAIN-SUFFIX` bypass rule for the subscription domain (see pitfall below)
5. Stop mihomo → write new config → restart → verify nodes loaded via API

**Common issues:**
- HTTP 400 → subscription token may be expired or the inner URL is dead
- HTTP 404 → subscription resource deleted by provider (expired token)
- Try different User-Agent: `clash`, `OpenClash`, `ClashMeta`
- Try different format parameters: remove `&sip002=1` or change to `&target=clash` if present
- For cn converters, try direct access to the inner subscription URL
- **Subscription says "no valid node info" but user says it works** → the subscription converter API may be broken. Ask the user to paste their full Clash config directly from their client (copy the config.yaml contents). Write it to `config/raw_sub.yaml` then `cp` to `run/config.yaml`. The proxies/proxy-groups/rules sections are valid YAML.

**Fallback: user-pasted config** — When the subscription endpoint is dead but the user's client still works, they can export/copy the config text. Write it verbatim to `run/config.yaml`. Add Agnes AI / other target domains to the `rules:` section so they route through the proxy:
```yaml
rules:
 - DOMAIN-SUFFIX,agnes-ai.com,Proxies
 - DOMAIN-SUFFIX,apihub.agnes-ai.com,Proxies
 ...
```

**DNS IP hardcoding** — When proxy nodes use hostnames that resolve to unreachable IPs (common with CDN/load-balanced nodes behind the GFW), diagnose with:
```bash
# Check which IP the hostname resolves to
getent hosts <node-hostname>
# Test if the port is actually reachable on the resolved IP
timeout 3 bash -c "echo > /dev/tcp/<resolved-ip>/<port>" 2>/dev/null && echo OPEN || echo TIMEOUT
# Try the same port on a different IP in the same /24 range
timeout 3 bash -c "echo > /dev/tcp/<alternate-ip>/<port>" 2>/dev/null && echo OPEN
```
If an alternate IP works, replace `server:` hostnames with the working IP directly in config.yaml:
```bash
sed -i 's|server: <dead-hostname>|server: <working-ip>|g' run/config.yaml
```

Also download GeoIP database:

```bash
curl -sL -o config/Country.mmdb \
  "https://github.com/Dreamacro/maxmind-geoip/releases/latest/download/Country.mmdb"
```

**GeoIP download fails in China** — GitHub is often blocked. Use a mirror (order by reliability):
```bash
# 1st choice: jsdelivr CDN (fastest, most reliable from China)
curl -sL -o run/geoip.metadb \
  "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.metadb"

# 2nd choice: ghproxy mirror
curl -sL -o run/geoip.metadb \
  "https://ghproxy.net/https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/geoip.metadb"
```

**⚠️ ghproxy may return corrupted MMDB** — If mihomo logs `MMDB invalid, remove and download` but the file exists, the download was corrupted (common with ghproxy for large binary files). Re-download from jsdelivr CDN instead.

If all mirrors fail, remove `GEOIP,CN` rules from config.yaml so mihomo starts without the MMDB file:
```bash
sed -i '/GEOIP/d' run/config.yaml
```

### 4. Handle SS+obfs nodes

Many Chinese proxy subscriptions use **Shadowsocks + obfs (simple-obfs)** for camouflage. Mihomo requires the `obfs-server` binary in PATH to handle these nodes. Without it, connections hang with `i/o timeout` even though the port is open.

**Diagnose:**
```bash
# Check if obfs-server is available
which obfs-server
# Test if the SS port accepts HTTP obfs connections
timeout 5 curl -vsk -H "Host: <obfs-host>" "http://<server-ip>:<port>/" 2>&1 | grep "Connected"
```

**Compile from source:**
```bash
# Install build dependencies
apt-get update && apt-get install -y --no-install-recommends \
  git autoconf libtool libc-ares-dev libev-dev libsodium-dev automake pkg-config

# Build simple-obfs
cd /tmp
git clone --depth 1 https://ghproxy.net/https://github.com/shadowsocks/simple-obfs.git
cd simple-obfs
git submodule update --init --recursive
./autogen.sh
./configure --prefix=/opt/data/mihomo --disable-documentation
make -j$(nproc)
make install
ls /opt/data/mihomo/bin/obfs-server   # verify

# Start mihomo with obfs-server in PATH
PATH="/opt/data/mihomo/bin:$PATH" /opt/data/mihomo/mihomo -d /opt/data/mihomo/run -f config.yaml
```

**Alternative:** If the obfs binary can't be compiled, switch to nodes that don't use obfs (e.g., pure SS AEAD, VMess, or Trojan).

### 5. Start as background process

Use Hermes' `terminal(background=true)` for long-lived processes:

```bash
/path/to/mihomo -d /path/to/dir -f /path/to/config.yaml
```

The process runs until explicitly stopped. Track its PID via the returned session_id.

### 6. Verify proxy is working

Check the external controller API (configured in config.yaml as `external-controller`):

```bash
curl -s http://127.0.0.1:9090/version
# Expect: {"meta":true,"version":"v1.19.27"}
```

Test HTTP proxy (port 7890 by default) and SOCKS5 proxy (port 7891):

```bash
curl -s -x http://127.0.0.1:7890 -o /dev/null -w "%{http_code}" https://www.google.com
# Expect: 200

curl -s -x socks5://127.0.0.1:7891 -o /dev/null -w "%{http_code}" https://www.google.com
# Expect: 200
```

**Verify nodes loaded from proxy-provider:**

After startup with a proxy-provider config, check the `/proxies` endpoint to confirm nodes were fetched:

```bash
# Show all proxy group states
curl -s http://127.0.0.1:9090/proxies | python3 -c "
import json,sys
data = json.load(sys.stdin).get('proxies',{})
for name, v in data.items():
    typ = v.get('type','')
    now = v.get('now','')
    if typ in ('Selector','URLTest'):
        print(f'GROUP {name:20s} type={typ:12s} now={now}')
    elif typ in ('Trojan','Vless','Vmess','Shadowsocks','Hysteria2'):
        print(f'NODE  {v.get(\"name\",name):40s} type={typ}')
"
```

This shows all proxy groups (Selector/URLTest) with their currently selected node, and all individual nodes loaded from the provider. Expect 50+ nodes from a typical subscription. If the list is empty, the provider fetch failed — check mihomo logs.

**Watch connection routing live:**

```bash
tail -f /opt/data/mihomo/mihomo.log | grep --line-buffered "Match using"
```

This shows which proxy group matches each request — useful for verifying the DOMAIN-SUFFIX bypass rule works and that actual traffic flows through the provider's nodes.

**Troubleshooting failed proxy tests:**
- Check mihomo.log for connection errors: `tail -20 /opt/data/mihomo/mihomo.log`
- Look for `dial tcp <ip>:<port>: i/o timeout` — the node is unreachable or needs obfs
- Look for `dial Final (match Match/)` — check which proxy group is being used
- Verify the node port is open: `timeout 3 bash -c "echo > /dev/tcp/<ip>/<port>" 2>/dev/null && echo OPEN`

### 7. Route API calls through the proxy

Once mihomo is running, set environment variables or use `-x` flag with curl to route traffic through the proxy. This makes external API providers (OpenRouter, Google AI Studio) reachable from behind the Great Firewall.

```python
# In Python: use proxies parameter
urllib.request.urlopen(req, timeout=15, context=ssl_context)

# Or set environment variables
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
```

**Persist in .env for Hermes gateway processes:**
```bash
echo -e "\n# Proxy for overseas API access (mihomo)\nHTTP_PROXY=http://127.0.0.1:7890\nHTTPS_PROXY=http://127.0.0.1:7890" >> /opt/data/.env
```
**Note:** Use `http://` (not `socks5://`) for `HTTPS_PROXY` — httpx and curl handle HTTPS-over-HTTP-proxy correctly via CONNECT tunnel.

### 8. Persistence across reboots

Create a start script and register with system cron:

```bash
cat > /opt/data/mihomo/start.sh << 'SCRIPT'
#!/bin/bash
MIHOMO_DIR=/opt/data/mihomo
MIHOMO_BIN=$MIHOMO_DIR/mihomo
CONFIG=$MIHOMO_DIR/run/config.yaml
LOG=$MIHOMO_DIR/mihomo.log
OBFS_BIN=$MIHOMO_DIR/bin
PIDFILE=$MIHOMO_DIR/mihomo.pid

if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
    echo "mihomo already running (PID $(cat $PIDFILE))"
    exit 0
fi

PATH="$OBFS_BIN:$PATH" nohup "$MIHOMO_BIN" -d "$MIHOMO_DIR/run" -f "$CONFIG" > "$LOG" 2>&1 &
echo $! > "$PIDFILE"
echo "mihomo started (PID $(cat $PIDFILE))"
SCRIPT
chmod +x /opt/data/mihomo/start.sh

apt-get install -y cron
(crontab -l 2>/dev/null; echo "@reboot /opt/data/mihomo/start.sh > /opt/data/mihomo/start.log 2>&1") | crontab -
```

## Default Ports

| Port | Protocol | Config key |
|------|----------|------------|
| 7890 | HTTP proxy | `port` |
| 7891 | SOCKS5 proxy | `socks-port` |
| 7892 | Redirect | `redir-port` |
| 7893 | Mixed | `mixed-port` |
| 9090 | External controller (API) | `external-controller` |
| 53 | DNS (fake-ip) | `dns.listen` |

## Pitfalls

- **No root + no loopback TUN** — TUN mode requires cap_net_admin. In restricted containers, use HTTP/SOCKS5 proxy mode instead (works without any special capabilities).
- **Binary incompatible** — if ./mihomo -v shows Exec format error, you downloaded the wrong arch. Use uname -m to double-check.
- **Subscription expired** — 400 doesn't contain any valid node info or 404 means the token/URL is dead. User must provide a new one.
- **Subscription expiry diagnosis** — All proxy nodes timing out concurrently with i/o timeout errors on the same IP range is the signature of an expired subscription, even if mihomo is still running. Check node names for an expiry date pattern like Expire: 2026-06-09. The user may need to refresh the subscription on their provider's website; the new config uses the same hostnames/ports — the backend just reactivates. After updating config, apply IP-hardcoding if DNS still resolves to unreachable IPs.
- **SS+obfs nodes require obfs-server binary** — Mihomo needs the obfs-server binary in PATH for Shadowsocks + obfs nodes. Diagnose with which obfs-server. Compile from source: git clone simple-obfs, install deps (autoconf libtool libc-ares-dev libev-dev libsodium-dev automake pkg-config), then ./autogen.sh && ./configure && make && make install. Start mihomo with PATH including the bin/ directory.
- **DNS IP hardcoding** — In China, proxy hostnames may resolve to IPs that are unreachable while alternate IPs in the same /24 work. Diagnose with getent hosts + timeout bash dev-tcp probe. Fix with sed replacing server hostnames with working IPs.
- **GEOIP rules fail without geoip.metadb** — GitHub is blocked by GFW. Remove all GEOIP,CN lines from config: sed -i '/GEOIP/d' run/config.yaml. Copy local Country.mmdb to run/ directory.
- **Background process lifecycle** — Hermes tracks the process via proc_* session_id. Use process(action=poll) to check status.
- **Proxy not working** — check mihomo.log for connection errors.
- **Config modifications** — edit config.yaml and restart mihomo (stop + start again) to apply changes.
- **Config corruption detection** — Before starting mihomo, validate run/config.yaml: `grep -q '^proxies:' run/config.yaml` should succeed. If the file only contains an error message (e.g. "The following link doesn't contain any valid node info"), restore from backup: `cp config/raw_sub.yaml run/config.yaml`. Always save a fresh subscription download to `config/raw_sub.yaml` (backup) before overwriting `run/config.yaml` (active). **Note:** proxy-provider configs won't contain `proxies:` key — instead check for `proxy-providers:`.
- **Subscription link still visitable but Clash can't use it** — The subscription URL may return HTTP 200 with an error message body instead of YAML. This happens when the token is expired but the API server still responds. Check raw response content with `curl -s SUB_URL | head -5`. If it says "no valid node info" or similar, the subscription is dead even though the URL "works". Expired subscriptions often have a node named "Expire: YYYY-MM-DD" in the last valid config — check `raw_sub.yaml` for this pattern.
- **base64 subscriptions may have info lines disguised as nodes** — Providers encode metadata (remaining traffic, reset time, expiry date) as vless:// links with the same UUID/host/port as the real node, differing only in the URL-encoded name after `#`. When inspecting 4 lines and only 1 is a real node name you recognize, ignore lines 1-3 — they're informational, not proxies. Do not add them to config.yaml.
- **s6/supervisor auto-restart interference** — If mihomo is managed by s6-overlay (common in Hermes Docker container), `pkill -f mihomo` triggers an auto-respawn. The proper fix is to **disable the s6 service first** — see `s6-service-management` skill (`s6-rc -d change <service-name>` or rename the `run` script). In non-Docker environments (WSL, bare Linux), mihomo may be managed by crontab @reboot with a start.sh script; kill the process and the cron won't respawn until next boot.
- **Proxy-provider subscription fetch deadlock** — When using `proxy-providers.type: http`, mihomo must fetch the subscription URL to know which nodes exist. If the subscription domain routes through the proxy group (which doesn't exist yet because providers haven't been fetched), mihomo deadlocks. **Fix:** Always add `- DOMAIN-SUFFIX,<provider-domain>,DIRECT` before GEOIP rules. Test by curling the subscription URL through the proxy after startup — if it fails with connection refused/timeout, the bypass rule is missing.
- **Mihomo API `/proxies` returns nested structure** — The endpoint returns `{"proxies": {"ProxyName": {...}}}`, not a flat dict. Always unwrap with `data.get('proxies',{})` when querying programmatically. Common mistake: iterating the top-level dict and getting no results.
- **Mihomo process keeps respawning despite pkill** — On WSL/non-Docker systems, check for crontab @reboot entries (`crontab -l | grep mihomo`). The start.sh script is typically registered at @reboot and won't respawn mid-session — only on next boot. If respawning mid-session, it's likely s6 supervision in a Docker container; disable via s6-service-management skill.

## Related Skills

- `provider-gateway` — API provider routing (use proxy to reach overseas providers)

## References

- `references/provider-evaluation.md` — How to evaluate proxy provider reliability (run-risk assessment, safe-buying signals, verification commands). Consult when the user asks if a provider/节点 is trustworthy or wants recommendations.
- `references/dual-vision-pipeline.md` — How to configure and use the dual-engine vision pipeline (Agnes AI + SenseNova) after the proxy is running.
- `references/vless-reality-config-template.md` — Template for building mihomo config.yaml from base64-encoded vless:// subscription links, with full vless+reality parameter mapping.
