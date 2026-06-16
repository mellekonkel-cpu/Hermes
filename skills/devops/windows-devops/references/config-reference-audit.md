# Configuration Reference Audit Workflow

When the user says "根据这个 [URL] 核查一下我的文件" (check my files against this reference), follow this workflow.

## Workflow

1. **Ingest the reference**: Fetch the reference URL via `web_extract` or browser. If it's a wiki/doc site with navigation, click through key pages (deployment, config, proxy, gateway, etc.). Get the main content from each.

2. **Inventory local files**: Gather the user's actual config files — typically:
   - `指令.txt` (launch command document)
   - `config.yaml` (Hermes Agent configuration)
   - `.env` (API keys, provider config)
   - Script files: `startup.sh`, `gateway-watchdog.sh`, etc.
   - Running env vars (check `$HERMES_MODEL`, `$HERMES_INFERENCE_MODEL`, etc.)

3. **Cross-reference and identify discrepancies**: Compare each aspect:
   - Deployment approach (compose vs docker run)
   - Model configuration
   - Proxy setup
   - Gateway/WeChat setup
   - File structure
   - Covered/not-covered features

4. **Fix discrepancies** (only what the user asks):
   - **指令.txt**: Backup first (`指令_YYYYMMDD_HHmmSS.txt`), then rewrite
   - **config.yaml**: Use `hermes config set`, NOT direct file edit (write-protected)
   - **Scripts**: Patch via `skill_manage(action='patch')` or terminal `sed`
   - **CRLF enforcement**: All `.txt`/`.bat`/`.ps1` files must use Windows CRLF — verify with `od -c` or `python3` if `file`/`xxd` unavailable

5. **Verify**: Confirm all changes applied correctly, report summary.

## Verification Tools

When `file` and `xxd` are unavailable (as in this containerized environment):

```bash
# Check CRLF with od
od -c /path/to/file | head -5
# Correct: ...\r \n...
# Wrong:   ...\n...

# Python CRLF check
python3 -c "print(repr(open('/path/to/file', 'rb').read(200)))"
# Look for b'\\r\\n' sequences

# Count CRLF lines
grep -c $'\r$' /path/to/file
```

## Common Discrepancies Found in Real Audits

### Amaranth Wiki Audit (2026-06-11)

**Reference**: `https://wiki-for-amaranth.pages.dev/`

| Aspect | Wiki Recommends | User Had | Action Taken |
|--------|----------------|----------|-------------|
| Deployment | `docker compose` (git clone → build → up) | `docker run` with pre-built image | Noted as design choice, no change |
| Proxy | mihomo container in compose, `http_proxy=http://mihomo:7890` | Windows Clash host proxy, container `unset` for WeChat | Noted, no change |
| Container name | `hermes-agent` | Missing (`docker exec hermes` failed) | Restored `--name hermes` in 指令.txt |
| Model | Not specified in wiki guide | Running `deepseek-v4-pro`, doc still said `deepseek-v4-flash` | Updated 指令.txt + config.yaml + reference |
| WeChat restart | Manual `rm -f gateway.lock gateway_state.json` | Already in watchdog | Added log tip about text-first-after-restart |
| Config structure | `providers.deepseek.api_key + models` | `model.provider: custom` + `base_url` | Noted, no change |
| 商汤 SenseNova | Full guide with custom_providers + skills | Not configured | Noted as available but unused |
