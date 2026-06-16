# SenseNova (商汤日日新) Provider Notes

Registered: 2026-06-13
Last updated: 2026-06-13 (added SenseCore platform auth)

## ⚠️ Two Separate Platforms — Different Auth

商汤有大模型API的**两个入口**，认证方式完全不同，不能混用：

| Platform | URL | Auth Method | API Endpoint |
|----------|-----|------------|-------------|
| **SenseNova Token Plan** (日日新) | `platform.sensenova.cn` | `sk-` API Key (Bearer) | `token.sensenova.cn/v1` |
| **SenseCore** (大装置) | `console.sensecore.cn` | AccessKey ID + Secret → signed token | `api.sensenova.cn/v1/llm/` |

### Path A: SenseNova Token Plan (Easy Path)

- **Entry point**: https://www.sensenova.cn/token-plan → click "免费开始" to register
- **Console**: https://platform.sensenova.cn
- **Auth**: Create `sk-` key in **Management Center → API Key Management**
- **Base URL**: `https://token.sensenova.cn/v1`
- **OpenAI-compatible**: Yes — drop-in `base_url` swap
- **Free tier**: 公测 Token Plan — phone registration required
- **Models**: `sensenova-6.7-flash-lite` (1500/5h), `deepseek-v4-flash` (500/5h), `sensenova-u1-fast` (1500/5h, image gen only)
- **Anthropic compat**: `https://token.sensenova.cn/` (no `/v1`)
- **Up to 20 API Keys** per account

### Path B: SenseCore Platform (Enterprise Path)

- **Console**: https://console.sensecore.cn/cn-sh-01/home
- **Auth**: Create **AccessKey** at **右上角账号中心 → 访问密钥** → 新增访问密钥
  - Get: `AccessKey ID` + `AccessKey Secret` (Secret only shown once!)
- **Base URL**: `https://api.sensenova.cn/v1/llm/`
- **NOT OpenAI-compatible** — uses its own REST API format
- **First-time activation required**: Go to console → manually confirm and activate "日日新大模型服务" (service starts as "未拥有" status)
- **Documentation**: http://console.sensecore.cn/micro/help/docs/model-as-a-service/nova

### Key Difference Summary

| Aspect | Path A (Token Plan) | Path B (SenseCore) |
|--------|--------------------|--------------------|
| Registration | platform.sensenova.cn | console.sensecore.cn |
| API key format | `sk-xxxxxxxx` | AccessKey ID (32 hex) + Secret |
| Auth header | `Bearer sk-xxx` | `Bearer $API_TOKEN` (generated from AccessKey) |
| Endpoint | `token.sensenova.cn/v1` | `api.sensenova.cn/v1/llm/` |
| Compatibility | OpenAI SDK drop-in | Custom REST API |
| Best for | Individual developers | Enterprise / SenseCore users |

---

### Hermes Config (Path A — Token Plan)

The wiki convention is `SN_API_KEY`:

```bash
# .env
SN_API_KEY=sk-...
```

Config:
```yaml
providers:
  custom:
    sensenova:
      base_url: https://token.sensenova.cn/v1
      api_key: ${SN_API_KEY}
      models:
        - deepseek-v4-flash
        - sensenova-6.7-flash-lite
        - sensenova-u1-fast
```

## Path A Activation Required: Token Plan

**API Key alone is NOT sufficient.** Creating an API Key in the console does not automatically enable it for API calls. The user must activate the Token Plan first.

### The Two-Platform Trap

The single most common pitfall: the user may end up on **two different platforms** without realizing they are separate:

| What they do | Where they end up | Result |
|---|---|---|
| Register at `sensenova.cn/token-plan` | `platform.sensenova.cn` (Path A) | Gets `sk-` key, but still needs Token Plan activation |
| Go to `console.sensecore.cn` from search | `console.sensecore.cn` (Path B) | Gets AccessKey ID + Secret, different system entirely |

**This creates confusion**: the user has credentials from two platforms, neither of which works until the corresponding service is activated. The `sk-` key from Path A returns 401 Forbidden until the Token Plan is activated on `platform.sensenova.cn`.

### Registration Flow (from Amaranth Wiki)

The recommended registration path is via the Token Plan page:

1. Visit https://www.sensenova.cn/token-plan
2. Click "免费开始" (Free Start)
3. Enter a mainland China mobile number to register
4. Set username and password
5. Log in → enter **管理中心 → API Key 管理**
6. Click **创建 API Key** → **copy and save immediately** (shown only once)

### Activation Steps (on platform.sensenova.cn)

1. Log in to https://platform.sensenova.cn
2. Navigate to the **Token Plan** section (or "快速接入" / Quick Access)
3. **Manually confirm and activate** the service
4. Only after activation does the key return 200 instead of 401

### Env Var Convention

The Amaranth Wiki uses `SN_API_KEY` as the environment variable name:

```bash
# .env — wiki convention
SN_API_KEY=sk-...

# .env — alternative (also works)
SENSENOVA_API_KEY=sk-...
```

Either works if the config.yaml references the right var name.

### Config.yaml (Hermes Provider)

```yaml
fallback_providers:
  - provider: custom
    base_url: https://token.sensenova.cn/v1
    api_key: ${SN_API_KEY}
    model: sensenova-6.7-flash-lite
```

### Error 401 / code 16 = Forbidden

This is the specific error when the API key exists but has NOT been linked to an active Token Plan:

```
{'error': {'code': 16, 'message': 'Forbidden'}}
```

**Do NOT chase wrong fixes** (IP whitelist, wrong endpoint, key format, model name) — the fix is always the same: activate Token Plan on the platform.

### Rate Limits (Path A)

| Model | Limit | Window |
|-------|-------|--------|
| `sensenova-6.7-flash-lite` | 1500 calls | 5 hours |
| `deepseek-v4-flash` | 500 calls | 5 hours |
| `sensenova-u1-fast` | 1500 calls | 5 hours |

Limits are model-independent (each model has its own counter).

## Path B Activation Required (SenseCore)

From the official documentation:

> "当您首次完成注册并登录控制台后，服务初始状态为'未拥有'。您需前往商汤大装置开放平台控制台，手动确认并开通日日新大模型服务，开通成功后即可开始调用日日新大模型服务 API。"

Steps:
1. Log in to https://console.sensecore.cn/cn-sh-01/home
2. Find and click the **开通日日新大模型服务** (Activate SenseNova Service) button
3. Alternatively: **左侧菜单 → 资源 → 资源管理** — activate from there
4. After activation, create AccessKey from **右上角账号中心 → 访问密钥**
5. AccessKey is used to generate Bearer token for `api.sensenova.cn/v1/llm/` endpoints

### API Request Format (Path B)

```bash
curl --request POST "https://api.sensenova.cn/v1/llm/chat-completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "model": "sensenova-6.7-flash-lite",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_new_tokens": 1024,
    "temperature": 0.8,
    "top_p": 0.7,
    "stream": false
  }'
```

Note: `max_new_tokens` (not `max_tokens`), `repetition_penalty` supported.

---

## Supported Features (Path A — Token Plan)

- ✅ Text chat (all models except u1-fast)
- ✅ Image input (sensenova-6.7-flash-lite only — multimodal)
- ✅ Streaming (SSE)
- ✅ Tool calling (function calling)
- ✅ JSON mode (`response_format: {"type": "json_object"}`)
- ✅ Reasoning modes (`reasoning_effort`: low/medium/high/none)
- ✅ Anthropic-compatible endpoint (for Claude Code)
- ❌ Image gen via chat (u1-fast uses separate `/v1/images/generations` endpoint)
- ❌ No documented embeddings endpoint

## Key Parameters (Path A — Token Plan)

| Parameter | Default | Range | Notes |
|-----------|---------|-------|-------|
| `temperature` | 0.6 (sensenova) / 1.0 (deepseek) | [0,2] | |
| `top_p` | 0.95 | [0,1] | |
| `max_tokens` | 65535 | up to 65536 | deepseek max output: 384K |
| `reasoning_effort` | "medium" | low/medium/high/none | none = no chain-of-thought |
| `tool_choice` | "auto" | auto/none/required | |
| `parallel_tool_calls` | true | | |

## Vision/Multimodal

`sensenova-6.7-flash-lite` supports `image_url` in messages (standard OpenAI format). Use as a fallback VL provider when SiliconFlow key is unavailable.

## Troubleshooting — 401 Forbidden (Path A)

When the user says "我申请了Key但不能用":
1. Confirm the key was created on `platform.sensenova.cn` (not `console.sensecore.cn`)
2. Confirm the user activated Token Plan on that platform
3. Test with `sensenova-6.7-flash-lite` model (has highest quota: 1500/5h)
4. If still 401, ask the user to check the Token Plan page for activation status

When the user shares an AccessKey ID + Secret from console.sensecore.cn:
1. These are NOT `sk-` keys and cannot be used with `token.sensenova.cn/v1` endpoint
2. They need a different endpoint: `api.sensenova.cn/v1/llm/`
3. The AccessKey needs to be converted to a Bearer token (via signing)
4. The service must be activated first on the SenseCore console
