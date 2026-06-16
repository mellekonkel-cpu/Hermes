# SiliconFlow Vision-Language (VL) Models — API Reference

Retrieved: 2026-05-07 from `https://api.siliconflow.cn/v1/models`

These models support **image + text** input (vision analysis) via the OpenAI-compatible chat completions endpoint. The main chat model (e.g. `DeepSeek-V4-Flash`) does NOT support `image_url` in messages — route to these instead when the user asks to analyze an image.

## Endpoint

```
POST https://api.siliconflow.cn/v1/chat/completions
Authorization: Bearer {key}
Content-Type: application/json
```

This is the **same** `/v1/chat/completions` endpoint used for text models — VL models accept `image_url` in a content **array** alongside text.

## Available VL Models

| Model ID | Speed | Quality | Notes |
|----------|-------|---------|-------|
| `Qwen/Qwen3-VL-32B-Instruct` | Slow (~60-120s) | Best | Recommended default for scientific figures |
| `Qwen/Qwen3-VL-32B-Thinking` | Slow | Best | Thinking variant, more thorough on complex visual reasoning |
| `Qwen/Qwen3-VL-8B-Instruct` | Fast (~20-40s) | Good | Good for simple charts, logos, photos |
| `Qwen/Qwen3-VL-8B-Thinking` | Fast | Good | Fast + reasoning |
| `Qwen/Qwen3-VL-30B-A3B-Instruct` | Medium | Very Good | MoE, good speed/quality balance |
| `Qwen/Qwen3-VL-30B-A3B-Thinking` | Medium | Very Good | MoE thinking variant |
| `zai-org/GLM-4.6V` | Medium | Good | Alternative, different training data |
| `zai-org/GLM-4.5V` | Fast | Moderate | Lighter GLM vision model |
| `THUDM/GLM-4.1V-9B-Thinking` | Fast | Good | GLM variant with thinking |

## API Call Format

```json
{
  "model": "Qwen/Qwen3-VL-32B-Instruct",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}},
        {"type": "text", "text": "Describe this image in detail."}
      ]
    }
  ],
  "temperature": 0.1,
  "max_tokens": 1024
}
```

Key points:
- Use `data:` URI scheme for inline images — do NOT pass external URLs (they may not reach the API server from the China domestic endpoint)
- `image_url` must be paired with `text` in a content **array** (not a string)

## Image Pre-processing

### Unsupported formats
- `.tif` / `.tiff` — **NOT supported**. Convert to JPEG first.
- `.bmp` — not tested, convert to JPEG to be safe.
- `.svg` — not supported, requires rasterization.

### Conversion (using ffmpeg)
```bash
# Simple conversion
ffmpeg -y -i input.tif -q:v 2 output.jpg

# Resize to control payload size (recommended for large scientific figures)
ffmpeg -y -i input.tif -vf scale=1200:-1 -q:v 2 output.jpg
```

### Base64 encoding (Python)
```python
import base64
with open('output.jpg', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
data_url = f"data:image/jpeg;base64,{b64}"
```

### Payload size guidelines
- Images up to ~1400px width and ~85KB base64 (~63KB JPEG) work reliably
- Larger images (2774px) should be scaled down to avoid timeout/deserialization errors
- If the model errors with `Failed to deserialize the JSON body`, the image is too large

## Known Limitations

### Small text / dense annotation
VL models struggle with **small text labels** on scientific figures:
- ESP maps with Emax/Emin values in sub-10pt font — frequently misread or missed entirely
- Axis ticks, legend text, chart annotations
- The 32B model performs noticeably better than 8B but still not 100% reliable

**Recommended iterative approach:**
1. **Pass 1** — Ask for general description (colors, layout, visible structure)
2. **Pass 2** — Inject context to guide confirmation ("This is an ESP map of FEC/DEC/PFPN/TMSB — can you read the Emax/Emin values?")
3. **Fallback** — When precision matters, combine VL output with known literature values and domain knowledge

### Color interpretation
VL models can reliably identify colors but may mislabel the **meaning** of color scales (e.g. red=negative vs red=positive in ESP maps) — this requires domain context.

### Response timeout
Complex images + 32B model can take >120s. Set request timeout accordingly. The 8B model is faster (~30s) but less accurate for detailed visual analysis.

### Token cost
Each image consumes ~258 tokens for a 800px-wide JPEG. Larger images cost proportionally more.
