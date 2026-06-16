# Agnes AI Provider

A free multimodal API provider compatible with Hermes.

## Details

| Field | Value |
|-------|-------|
| Provider slug | `agnes` |
| Website | https://platform.agnes-ai.com |
| API base URL | https://apihub.agnes-ai.com/v1 |
| Text model | `agnes-2.0-flash` |
| Image model | `agnes-image-2.1-flash` |
| Video model | `agnes-video-v2.0` |
| Pricing | **Free** (no credit card required) |

## Env Var

```
AGNES_AI_API_KEY=sk-your-key-here
```

## Config Entry

```yaml
providers:
  custom:
    agnes:
      base_url: https://apihub.agnes-ai.com/v1
      api_key: ${AGNES_AI_API_KEY}
      models:
        - agnes-2.0-flash
        - agnes-image-2.1-flash
```

## Registration

Sign up at https://platform.agnes-ai.com, then Settings → API Keys to create a key.
