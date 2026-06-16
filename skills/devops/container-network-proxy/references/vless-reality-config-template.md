# VLESS + Reality Config Template (for mihomo)

When a subscription returns base64-encoded vless:// links instead of Clash YAML,
build a config.yaml manually following this template.

## Decode vless:// links

```python
import base64, urllib.parse

# The raw subscription body (base64-encoded)
raw = open('raw_sub.yaml').read().strip()
lines = base64.b64decode(raw).decode().strip().split('\n')

for line in lines:
    name = urllib.parse.unquote(line.split('#')[-1]) if '#' in line else 'unknown'
    if line.startswith('vless://'):
        rest = line[8:]  # strip 'vless://'
        userinfo, rest = rest.split('@', 1)
        hostport, rest = rest.split('?', 1)
        host, port = hostport.rsplit(':', 1)
        params = dict(urllib.parse.parse_qsl(rest.split('#')[0]))
        
        print(f"Node: {name}")
        print(f"  server: {host}")
        print(f"  port: {port}")
        print(f"  uuid: {userinfo}")
        print(f"  type: {params.get('type', 'tcp')}")
        print(f"  security: {params.get('security', 'none')}")
        print(f"  flow: {params.get('flow', '')}")
        print(f"  servername (SNI): {params.get('sni', '')}")
        print(f"  public-key (pbk): {params.get('pbk', '')}")
        print(f"  short-id (sid): {params.get('sid', '')}")
```

## Info lines disguised as nodes

Some providers encode subscription metadata (remaining traffic, reset time, expiry)
as vless:// links with the same UUID/host/port as the real node, differing only
in the URL-encoded name after `#`. Skip these — only the actual node names are real proxies.

Example: first 3 lines may decode to "剩余流量：2 GB", "距离下次重置剩余：1 天", "套餐到期：2026-06-17"
— these are the same vless parameters but are informational only.

## Full config.yaml

```yaml
port: 7890
socks-port: 7891
mixed-port: 7892
redir-port: 7893
allow-lan: false
mode: rule
log-level: info
external-controller: 0.0.0.0:9090
ipv6: false

proxies:
  - name: "🇺🇸 US08"                              # from the name after #
    type: vless
    server: node.example.com                       # from vless:// host
    port: 36699                                    # from vless:// port
    uuid: 7672f253-4171-47a4-9d5e-1d5ae1faabae    # from vless:// uuid
    tls: true                                      # required for reality
    udp: true                                      # enable UDP over TCP
    flow: xtls-rprx-vision                         # from ?flow= parameter
    servername: swdist.apple.com                   # from ?sni= parameter (SNI spoof)
    reality-opts:
      public-key: rBLgYxDPw9nmzppUc_8Hr-...       # from ?pbk= parameter
      short-id: 5f7b                               # from ?sid= parameter
    client-fingerprint: chrome                     # TLS fingerprint to mimic

proxy-groups:
  - name: "Proxy"
    type: select
    proxies:
      - "🇺🇸 US08"
      - DIRECT

rules:
  - GEOIP,CN,DIRECT
  - MATCH,Proxy
```

## Key parameters explained

| vless param   | mihomo config key    | Meaning |
|---------------|---------------------|---------|
| `type=tcp`    | TLS layer (hardcoded) | Transport protocol (always tcp for reality) |
| `encryption=none` | (implied)        | No additional encryption (TLS/reality handles it) |
| `security=reality` | `tls: true` + `reality-opts:` | REALITY anti-censorship |
| `flow=xtls-rprx-vision` | `flow: xtls-rprx-vision` | XTLS flow control (reality vision) |
| `sni=...`     | `servername: ...`    | TLS SNI spoof (valid domain, not checked by server) |
| `pbk=...`     | `reality-opts.public-key` | Server's REALITY public key |
| `sid=...`     | `reality-opts.short-id` | Server's REALITY short ID |
| `fp=chrome`   | `client-fingerprint: chrome` | TLS fingerprint |
| `host=` (empty) | (not needed)       | No custom Host header needed for reality |

## Verification

After config is deployed and mihomo running:

```bash
# Check API is alive
curl -s http://127.0.0.1:9090/version

# Test proxy is routing
curl -s --proxy http://127.0.0.1:7890 -o /dev/null -w "%{http_code}" https://www.google.com

# Check logs for actual proxy usage
tail -5 /path/to/mihomo.log
# Look for: "[TCP] mihomo --> target.com:443 match Match using Proxy[🇺🇸 US08]"
```
