# SiliconFlow Available Models (retrieved 2026-05-06)

API endpoint: `https://api.siliconflow.cn/v1/models`
Auth: Bearer token

## Image Generation Models

| Model ID | Type | Notes |
|----------|------|-------|
| `Kwai-Kolors/Kolors` | Text-to-Image | Default, good quality, 1024x1024 only |
| `Qwen/Qwen-Image` | Text-to-Image | Alternative, best for academic use |
| `Qwen/Qwen-Image-Edit` | Image Editing | Requires input image |
| `Tongyi-MAI/Z-Image` | Text-to-Image | Alternative |
| `Tongyi-MAI/Z-Image-Turbo` | Text-to-Image | Faster variant, lower quality |
| `baidu/ERNIE-Image-Turbo` | Text-to-Image | Baidu ERNIE |

## API Response Format (images/generations)

```json
{
  "images": [
    {"url": "https://s3.siliconflow.cn/temporary/.../xxx.png?X-Amz-..."}
  ],
  "timings": {"inference": 3.197},
  "seed": 55875921,
  "shared_id": "0",
  "data": [
    {"url": "same_url_again"}
  ],
  "created": 1778063547
}
```

## Supported API Parameters

```json
{
  "model": "Kwai-Kolors/Kolors",
  "prompt": "string (required)",
  "n": 1,
  "size": "1024x1024",
  "image_quality": "high",
  "negative_prompt": "string (optional, supported by Kolors)",
  "seed": 42
}
```

## Text Models (same API key)

- `deepseek-ai/DeepSeek-V4-Flash`
- `deepseek-ai/DeepSeek-V3` / `deepseek-ai/DeepSeek-V3.2`
- `deepseek-ai/DeepSeek-R1`
- `Qwen/Qwen3-235B-A22B-Instruct-2507`
- `Qwen/Qwen3-30B-A3B-Thinking-2507`
- `moonshotai/Kimi-K2-Thinking` / `Kimi-K2.6`
- `THUDM/GLM-Z1-32B-0414` / `GLM-4.6` / `GLM-4.7` / `GLM-5` / `GLM-5.1`
- `MiniMaxAI/MiniMax-M2.5`
- `stepfun-ai/Step-3.5-Flash`
- `ByteDance-Seed/Seed-OSS-36B-Instruct`
- `Qwen/Qwen3.5-397B-A17B` / `Qwen3.5-122B-A10B`
- Many more (~90+ models)
