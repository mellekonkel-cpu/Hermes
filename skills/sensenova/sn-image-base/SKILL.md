---
name: sn-image-base
description: |
  Base-layer skill for the SenseNova-Skills project, providing low-level APIs for image generation, recognition (VLM), and text optimization (LLM).
  This skill does not preprocess inputs; it only calls backend services and returns results.
  This skill is not user-facing and is intended for upper-layer skills only.
triggers:
  - "SenseNova-Skills Image Generation"
  - "SenseNova-Skills 图像基础工具"
  - "sn 图像基础工具"
  - "SenseNova 图像基础工具"
  - "SenseNova Image Generation"
  - "sn-image-base"
metadata:
  project: SenseNova-Skills
  tier: 0
  category: infrastructure
  user_visible: false
---

# sn-image-base

## Dependency Installation

```bash
pip install -r requirements.txt
```

## Overview

`sn-image-base` is the base-layer skill (tier 0) of the SenseNova-Skills project and provides three low-level tools:

- `sn-image-generate`: image generation (calls text-to-image-no-enhance API)
- `sn-image-recognize`: image recognition (uses VLM to analyze image content)
- `sn-text-optimize`: text optimization (uses LLM to process text)

This skill **does not perform any input preprocessing** and only calls backend services to return results.

## Tools List

### sn-image-generate

Image generation tool that calls the text-to-image-no-enhance API.

`--prompt` is required; all other parameters are optional:

| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--prompt` | string | **Required** | Prompt text for image generation |
| `--negative-prompt` | string | `""` | Negative prompt |
| `--image-size` | string | `2k` | Image size preset (case-insensitive). Recommended: `2k`. `4k` optional, needs model support (sensenova rejects it → `status=failed`). Other values → `status=failed`. |
| `--aspect-ratio` | string | `16:9` | Aspect ratio, e.g. `1:1`, `16:9`, `9:16` |
| `--seed` | int | `None` | Random seed for reproducible generation |
| `--unet-name` | string | `None` | Specify a UNet model name |
| `--api-key` | string | `SN_IMAGE_GEN_API_KEY` -> `SN_API_KEY` | API key (CLI argument has priority; `MissingApiKeyError` is raised when all are empty) |
| `--base-url` | string | `SN_IMAGE_GEN_BASE_URL` -> `SN_BASE_URL` | API base URL (CLI argument has priority) |
| `--poll-interval` | float | `5.0` | Polling interval (seconds) |
| `--timeout` | float | `300.0` | Timeout (seconds) |
| `--insecure` | flag | `False` | Disable TLS verification |
| `--save-path` | Path | Auto-generated | Save path |

### sn-image-recognize

Image recognition tool that uses VLM (Vision Language Model) to analyze image content. Supports multiple image inputs.

`--images` and `--user-prompt` (or `--user-prompt-path`) are required. All other parameters use three-level defaults (CLI > env var > built-in default):

| Parameter | Type | Built-in Default | Env Var | Description |
|------|------|-----------|---------|------|
| `--api-key` | string | No hardcoded default | `SN_VISION_API_KEY` -> `SN_CHAT_API_KEY` -> `SN_API_KEY` | Chat runtime API key; raises `MissingApiKeyError` when all are unset |
| `--base-url` | string | `SN_CHAT_BASE_URL` default | `SN_VISION_BASE_URL` -> `SN_CHAT_BASE_URL` -> `SN_BASE_URL` | Vision provider base URL; falls back to shared chat/global provider |
| `--model` | string | `sensenova-6.7-flash-lite` | `SN_VISION_MODEL` -> `SN_CHAT_MODEL` | Vision-capable model name |
| `--vlm-type` | string | `openai-completions` | `SN_VISION_TYPE` -> `SN_CHAT_TYPE` | Chat protocol type override |
| `--user-prompt-path` | string | `None` | - | Local file path, mutually exclusive with `--user-prompt` |
| `--system-prompt-path` | string | `None` | - | Local file path, mutually exclusive with `--system-prompt` |

Available values for `--vlm-type`:

- `openai-completions`: OpenAI-compatible `/v1/chat/completions` interface
- `anthropic-messages`: Anthropic Messages `/v1/messages` interface

### sn-text-optimize

Text optimization tool that uses LLM (Language Model) to optimize text content. Does not accept image inputs.

`--user-prompt` (or `--user-prompt-path`) is required. All other parameters use three-level defaults (CLI > env var > built-in default):

| Parameter | Type | Built-in Default | Env Var | Description |
|------|------|-----------|---------|------|
| `--api-key` | string | No hardcoded default | `SN_TEXT_API_KEY` -> `SN_CHAT_API_KEY` -> `SN_API_KEY` | Chat runtime API key; raises `MissingApiKeyError` when all are unset |
| `--base-url` | string | `SN_CHAT_BASE_URL` default | `SN_TEXT_BASE_URL` -> `SN_CHAT_BASE_URL` -> `SN_BASE_URL` | Text provider base URL; falls back to shared chat/global provider |
| `--model` | string | `sensenova-6.7-flash-lite` | `SN_TEXT_MODEL` -> `SN_CHAT_MODEL` | Text model name |
| `--llm-type` | string | `openai-completions` | `SN_TEXT_TYPE` -> `SN_CHAT_TYPE` | Chat protocol type override |
| `--user-prompt-path` | string | `None` | - | Local file path, mutually exclusive with `--user-prompt` |
| `--system-prompt-path` | string | `None` | - | Local file path, mutually exclusive with `--system-prompt` |

Available values for `--llm-type`:

- `openai-completions`: OpenAI-compatible `/v1/chat/completions` interface
- `anthropic-messages`: Anthropic Messages `/v1/messages` interface

## VLM vs LLM

| Tool | Model Type | Image Input | Interface Type Parameter |
|------|----------|-----------------|-------------|
| `sn-image-recognize` | VLM (Vision Language Model) | Yes, supports multiple images | `--vlm-type` |
| `sn-text-optimize` | LLM (Language Model) | No, text only | `--llm-type` |

## Usage

All tools are called through the unified `sn_agent_runner.py` entrypoint:

```bash
# Image generation (only prompt required; api-key/base-url have defaults)
python scripts/sn_agent_runner.py sn-image-generate \
    --prompt "..."

# Image generation (override base-url)
python scripts/sn_agent_runner.py sn-image-generate \
    --prompt "..." \
    --base-url "https://custom-endpoint.com/v1"

# Image generation (explicitly override api-key)
python scripts/sn_agent_runner.py sn-image-generate \
    --prompt "..." \
    --api-key "sk-xxx"

# Image recognition (VLM) - minimal call (uses built-in Sensenova defaults)
python scripts/sn_agent_runner.py sn-image-recognize \
    --user-prompt "Describe the image" \
    --images "path/to/image.png"

# Image recognition (VLM) - override to Anthropic Claude API compatible (messages interface)
python scripts/sn_agent_runner.py sn-image-recognize \
    --user-prompt "Describe the image" \
    --images "path/to/image.png" \
    --api-key "sk-ant-xxx" \
    --base-url "https://api.anthropic.com" \
    --model "claude-sonnet-4-6" \
    --vlm-type "anthropic-messages"

# Text optimization (LLM) - minimal call (uses built-in Sensenova defaults)
python scripts/sn_agent_runner.py sn-text-optimize \
    --user-prompt "Optimize the text: ..."

# Text optimization (LLM) - override to Anthropic Claude API compatible (messages interface)
python scripts/sn_agent_runner.py sn-text-optimize \
    --user-prompt "Optimize the text: ..." \
    --api-key "sk-ant-xxx" \
    --base-url "https://api.anthropic.com" \
    --model "claude-sonnet-4-6" \
    --llm-type "anthropic-messages"
```

### Default Parameter Behavior

Authentication parameters for `sn-image-generate` have the following default behavior:

| Parameter | Default | Override | Description |
|------|--------|----------|------|
| `--base-url` | `SN_IMAGE_GEN_BASE_URL` -> `SN_BASE_URL` | `--base-url "..."` | CLI argument has priority |
| `--api-key` | `SN_IMAGE_GEN_API_KEY` -> `SN_API_KEY` | `--api-key "..."` | CLI argument has priority; throws `MissingApiKeyError` if all values are empty |

`sn-image-recognize` and `sn-text-optimize` use priority: **CLI argument > command-specific env var > shared `SN_CHAT_*` env var > global `SN_*` env var > built-in default**.

| Parameter | Built-in Default | Vision Env Var | Text Env Var |
|------|-----------|-------------|-------------|
| `--api-key` | None (must be provided) | `SN_VISION_API_KEY` -> `SN_CHAT_API_KEY` -> `SN_API_KEY` | `SN_TEXT_API_KEY` -> `SN_CHAT_API_KEY` -> `SN_API_KEY` |
| `--base-url` | `https://token.sensenova.cn/v1` | `SN_VISION_BASE_URL` -> `SN_CHAT_BASE_URL` -> `SN_BASE_URL` | `SN_TEXT_BASE_URL` -> `SN_CHAT_BASE_URL` -> `SN_BASE_URL` |
| `--model` | `sensenova-6.7-flash-lite` | `SN_VISION_MODEL` -> `SN_CHAT_MODEL` | `SN_TEXT_MODEL` -> `SN_CHAT_MODEL` |
| `--vlm-type` / `--llm-type` | `openai-completions` | `SN_VISION_TYPE` -> `SN_CHAT_TYPE` | `SN_TEXT_TYPE` -> `SN_CHAT_TYPE` |

`api_key` resolution order (high to low): CLI `--api-key` > command-specific key (`SN_VISION_API_KEY`/`SN_TEXT_API_KEY`) > `SN_CHAT_API_KEY` > `SN_API_KEY`. If all are unset, `MissingApiKeyError` is raised.

Only `--api-key` must be provided via CLI or environment; base URL, model, and interface type have shared chat defaults.

## Agent Configuration Integration

The agent can automatically read parameters from `openclaw.json` without manual input:

| CLI Parameter | openclaw.json Field | Example |
|-----------|-------------------|--------|
| `--base-url` | `providers.<name>.baseUrl` | `https://api.anthropic.com` |
| `--llm-type` | `providers.<name>.api` | `anthropic-messages` / `openai-completions` |
| `--vlm-type` | `providers.<name>.api` | `anthropic-messages` / `openai-completions` |
| `--model` | `providers.<name>.models[].id` | `claude-sonnet-4-6` |
| `--api-key` | `providers.<name>.apiKey` or env var | `sk-cp-...` |

Note: `--llm-type` and `--vlm-type` share the same `providers.<name>.api` field and are used by LLM and VLM tools respectively.

Mapping between `provider.api` and interface type:

| api Value | Corresponding `--llm-type` / `--vlm-type` | Endpoint Path |
|--------|----------------------------------|---------------|
| `anthropic-messages` | `anthropic-messages` | `/v1/messages` |
| `openai-completions` | `openai-completions` | `/v1/chat/completions` |
| `openai-responses` | (future extension) | `/responses` |

## Mapping Between base-url and Interface Type

Different API types have different requirements for base-url format:

| Type | `--llm-type` / `--vlm-type` | Recommended base-url | Code Appended Path | Final URL Example |
|------|------------------------------|---------------|--------------|---------------|
| LLM | `openai-completions` | `https://token.sensenova.cn/v1` | `/chat/completions` | `https://token.sensenova.cn/v1/chat/completions` |
| LLM | `anthropic-messages` | `https://api.anthropic.com/v1` | `/messages` | `https://api.anthropic.com/v1/messages` |
| VLM | `openai-completions` | `https://token.sensenova.cn/v1` | `/chat/completions` | `https://token.sensenova.cn/v1/chat/completions` |
| VLM | `anthropic-messages` | `https://api.anthropic.com/v1` | `/messages` | `https://api.anthropic.com/v1/messages` |

**Note**:

- Recommended chat base URLs include the provider API version path, for example `/v1`.
- For compatibility, if the configured chat base URL has no path, the runner appends `/v1/chat/completions` or `/v1/messages`.
- If the configured chat base URL already has a path such as `/v1`, the runner appends only `/chat/completions` or `/messages`.
- Some providers use versioned paths other than `/v1`, such as Gemini's `/v1beta/openai`.

## User Interaction Style (for this user)

When delivering generated images to the user:

- **Send images directly** — the user wants the media, not a paragraph about it. A one-line label (e.g. "① 荷花金鱼") before each image is fine, but skip the philosophical descriptions, color analysis tables, and elaborate multi-paragraph framing.
- **Action over explanation** — when the user asks "生成" or "发给我", generate and send. Don't narrate the process.
- **Impatience signal** — [敲打] emoji means "too slow / too verbose." Cut the chatter and deliver.
- **Avatar-specific requests** — the user wants WeChat-headshot-appropriate images: 1:1 aspect ratio (`aspect_ratio="1:1"` → 2048x2048 at 2K), 水墨风 (ink wash style), clean minimal compositions (nature close-ups, single subject, plenty of 留白). Content directions that work: 荷花金鱼, 山水孤舟, 梅花鸟鸣, 竹林明月, 金凤.

## Prompt Engineering: Multi-Fusion (多方面融合)

The user responds well to prompts that blend contrasting aesthetic traditions:

- **Eastern × Western**: 水墨 + 几何, 中国画 + 赛博朋克, 古建筑 + 数据流
- **Classical × Modern**: 发条心脏 + 霓虹城市, 金色光粒子 + 水晶王座
- **Nature × Machine**: 樱花 + 数学公式, 竹林 + 数据流
- **Ink wash style** (水墨风): works especially well for avatar generation. Use Chinese-language prompts for best results with SenseNova (domestic model).

Avoid: purely abstract or surreal concepts (the model generates literal interpretations). Prefer concrete imageable scenes.

## Non-trivial Techniques

### Avatar Generation with SenseNova

```bash
python3 scripts/sn_agent_runner.py sn-image-generate \\
    --prompt "水墨风格，荷花，金色锦鲤，禅意，留白，适合头像" \\
    --aspect-ratio "1:1" \\
    --image-size "2k"
```

- `"1:1"` at 2K resolution → 2048×2048 pixel output (ideal for WeChat avatar)
- Use Chinese prompts for better cultural reference alignment
- Keep composition centered and minimal (one subject, plenty of negative space)
- Output files are ~5MB PNGs — acceptable for WeChat delivery

### Dual-Engine Fallback

When generating for this user:

1. **Primary**: SenseNova `sensenova-u1-fast` via `SensenovaText2ImageClient` — works without proxy (domestic Chinese service)
2. **Backup**: Agnes AI `agnes-image-2.1-flash` via `dual_vision.py` — requires working mihomo proxy (GFW blocked)
3. If proxy nodes are all timing out on the same IP range → subscription likely expired (see container-network-proxy pitfalls)

The `dual_vision.py` script at `/opt/data/sn_scripts/dual_vision.py` orchestrates both engines:
```
python3 /opt/data/sn_scripts/dual_vision.py gen "<prompt>"
```

If SenseNova alone is used, use `aspect_ratio="1:1"` for avatars or `"16:9"` for landscape/scenic.

---

## Output Format

See `references/api_spec.md` for details.