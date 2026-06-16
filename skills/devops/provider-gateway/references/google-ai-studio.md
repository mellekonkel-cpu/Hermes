# Google AI Studio Provider

**Registered**: 2026-05-06

- **API Key**: `AIza...your-gemini-key`
- **Base URL**: `https://generativelanguage.googleapis.com/v1`
- **Format**: **NOT OpenAI-compatible** — uses native Google AI API format (`contents/parts`)

## API Format Differences

| Aspect | OpenAI-compatible | Google AI Studio |
|--------|------------------|------------------|
| Endpoint | `/v1/chat/completions` | `/v1/models/{model}:generateContent?key={key}` |
| Auth header | `Authorization: Bearer {key}` | Query param `?key={key}` |
| Message format | `{"messages": [{"role": "user", "content": "hi"}]}` | `{"contents": [{"parts": [{"text": "hi"}]}]}` |
| Config | In request body | Under `generationConfig` key |
| Streaming | SSE with `data:` lines | Different SSE format |

## Available Models (verified)

| Model ID | Type | Notes |
|----------|------|-------|
| `gemini-2.5-flash` | Fast reasoning | Latest gen |
| `gemini-2.5-pro` | Deep reasoning | Slower, smarter |
| `gemini-2.0-flash` | Standard | Stable |
| `gemini-2.0-flash-lite` | Lightweight | Cheapest |
| `gemini-2.5-flash-lite` | Lightweight | Latest lite |

## Quirks & Pitfalls

- **Free tier quota**: Free tier has strict rate limits. Expect **HTTP 429** ("quota exceeded") if limits are hit. May resolve after quota reset window. To use reliably, enable billing in Google AI Studio console.
- **Model listing works** even when quota is exhausted (`GET /v1/models?key={key}` returns all models with 200).
- **No streaming via simple curl** — SSE format is different from OpenAI. Use Python with iterative reads.
- **Safety filters** may block innocuous content by default. Can configure `safetySettings` in request body.

## Usage Example

```python
import json, urllib.request

api_key = "AIza...your-gemini-key"
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
payload = json.dumps({
    "contents": [{"parts": [{"text": "Hello"}]}],
    "generationConfig": {"maxOutputTokens": 100}
}).encode()
req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read())
    print(data["candidates"][0]["content"]["parts"][0]["text"])
```
