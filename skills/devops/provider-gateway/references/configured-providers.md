# Configured Providers (as of 2026-05-07)

## SiliconFlow (硅基流动) — Primary

- **Base URL**: `https://api.siliconflow.cn/v1`
- **API Key**: `sk-...your-siliconflow-key`
- **Auth**: Bearer token in Authorization header
- **Format**: OpenAI-compatible
- **Capabilities**: text chat, image gen (images/generations), video, voice, OCR, embedding, **VL/vision analysis**
- **VL/vision models**: `Qwen/Qwen3-VL-32B-Instruct` (best quality), `Qwen/Qwen3-VL-8B-Instruct` (fast), `Qwen/Qwen3-VL-30B-A3B-Instruct` (MoE). Use `/v1/chat/completions` with `image_url` in content array. See `siliconflow-image` skill's `references/siliconflow-vl-models.md` for API format, pre-processing (TIF → JPG), and limitations.
- **Region**: 🇨🇳 Domestic (fast)

### Tested working models
- `deepseek-ai/DeepSeek-V4-Flash` (✅ ping, ~1176ms)
- `Kwai-Kolors/Kolors` (image gen — ✅ tested in previous session)

---

## Google AI Studio — Overseas LLM

- **Base URL**: `https://generativelanguage.googleapis.com/v1`
- **API Key**: `AIza...your-gemini-key`
- **Format**: ❌ NOT OpenAI-compatible — native Google AI API (`contents/parts` format)
- **Auth**: Query parameter `?key={key}` (not Authorization header)
- **Region**: 🌐 Overseas (Google)
- **Ping result (2026-05-07)**: ✅ Model listing works (574ms, 7 models), but content gen returns **429 quota exceeded** (free tier limit)

### Models
`gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-2.5-flash-lite`

### Known issues
- Free tier quota very limited — expect 429 under normal use
- See `references/google-ai-studio.md` for full API format details

---

## Tavily — Web Search

- **Endpoint**: `https://api.tavily.com/search`
- **API Key**: `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`
- **Format**: POST with JSON body (api_key in body, not header)
- **Parameters**: `query`, `search_depth` (basic/deep), `max_results`
- **Response**: `results[]` array with title, url, content
- **Ping result (2026-05-07)**: ✅ ~2221ms, returned 1 result

---

## OpenRouter — Overseas Complement

- **Base URL**: `https://openrouter.ai/api/v1`
- **API Key**: `sk-or-...your-openrouter-key-here`
- **Format**: OpenAI-compatible
- **Constraint**: FREE MODELS ONLY — cannot call paid models

### Allowed models (4 total)
| Model ID | Params | Context | Status (2026-05-07) |
|----------|--------|---------|---------------------|
| `nousresearch/hermes-3-llama-3.1-405b:free` | 405B | 131K | ❌ 429 (rate limited) |
| `meta-llama/llama-3.3-70b-instruct:free` | 70B | 65K | ❌ 429 (rate limited) |
| **`minimax/minimax-m2.5:free`** | ? | 196K | ✅ **有时可用** (2516ms) |
| `qwen/qwen3-coder:free` | 480B MoE | 262K | ❌ 429 (rate limited) |

### Rate limiting behavior (observed pattern)
- **minimax-m2.5** is the most stable of the 4 — it was the only one that recovered from 429 between 2026-05-06 and 2026-05-07
- The other 3 models have been consistently 429 across multiple test attempts
- Retry with backoff may help during low-traffic periods

### Known issues
- **HTTP 429** — rate limited. Free tier is restricted. Retry after cooldown.
- Only 1 of 4 models (minimax-m2.5) is currently usable under normal conditions
