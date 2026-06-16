# SiliconFlow + Qwen3-VL (verified working setup)

## Environment

- Config: `/opt/data/config.yaml`
- Env file: `/opt/data/.env`
- Key: `SILICONFLOW_KEY=sk-...your-siliconflow-key`
- Key also injected into Hermes Docker container environment (visible via `docker exec hermes env`)

## Config (applied 2026-06-13)

```yaml
auxiliary:
  vision:
    provider: custom
    model: Qwen/Qwen3-VL-32B-Instruct
    base_url: https://api.siliconflow.cn/v1
    api_key: ${SILICONFLOW_KEY}
    timeout: 120
    download_timeout: 30
```

## Available Models on SiliconFlow

| Model ID | Size | Notes |
|---|---|---|
| `Qwen/Qwen3-VL-32B-Instruct` | 32B dense | Good quality, recommended primary choice |
| `Qwen/Qwen3-VL-8B-Instruct` | 8B | Faster, cheaper, good for quick checks |
| `Qwen/Qwen3-VL-235B-A22B-Thinking` | 235B MoE | Best quality but more expensive |

## Model Support

- `image_url` input: yes (OpenAI-compatible format)
- Tool calling: yes (for unnormalized Qwen models via SiliconFlow, API must be called directly)
- Context: 262K tokens
- Streaming: yes

## Provider Registration

- Site: https://cloud.siliconflow.cn
- Free tier: ¥14 credit on registration, some free models available
- API format: OpenAI-compatible

## Related Skills

- `daily-briefing` skill has SiliconFlow vision fallback in `references/siliconflow-vision.md`
