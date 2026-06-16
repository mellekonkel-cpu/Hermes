# Free Vision Provider Alternatives

当 SiliconFlow Key 不可用或余额不足时，可以用以下免费替代方案做图片理解（VLM）。

## 1. Agnes AI (Agnes-2.0-Flash + 文生图 + 视频)

- **永久免费**，注册即用，无额度限制
- **Base URL:** `https://apihub.agnes-ai.com/v1`
- **注册:** [platform.agnes-ai.com](https://platform.agnes-ai.com) → Settings → API Keys → Create new secret key
- **注册方式:** 邮箱 / Google / GitHub，不绑卡
- **团队:** 清华系（Sapiens AI，新加坡），ClawEval + PinchBench Top 10
- **上下文:** 256K，支持工具调用 / Agent

### 可用模型

| 模型 | 用途 | 说明 |
|------|------|------|
| `agnes-2.0-flash` | 文本 + 视觉理解 | OpenAI 兼容，支持 `image_url` 输入 |
| `agnes-image-2.1-flash` | 文生图 | OpenAI `/v1/images/generations` 格式 |
| `agnes-image-2.0-flash` | 文生图（旧版） | 同上 |
| `agnes-video-v2.0` | 视频生成 | OpenAI 兼容 |
| `agnes-1.5-flash` | 文本（旧版） | 备选 |

### 中国的网络限制（⚠️ 必须走代理）

`apihub.agnes-ai.com` 使用 Cloudflare CDN，在国内网络环境下 **SSL 握手阶段会被 GFW 干扰**，无法直连。必须在 WSL/容器内运行 mihomo/Clash 代理：

```bash
# 环境变量
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

详细代理部署 → `container-network-proxy` skill。

### 视觉理解 API（看图）

```bash
curl -x http://127.0.0.1:7890 -sk https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-2.0-flash",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}},
          {"type": "text", "text": "描述这张图片"}
        ]
      }
    ]
  }'
```

### 文生图 API（画图）

```bash
curl -x http://127.0.0.1:7890 -sk -X POST https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "a cute cat on a Chinese roof",
    "n": 1,
    "size": "1024x1024"
  }'
# 返回: {"data":[{"url":"https://..."}]}
```

### 注意事项

- 支持图片 URL 和 Base64 格式
- 仅受 RPM（每分钟请求次数）限制，触顶后稍后重试
- 注册送 $0.1 初始余额（供付费模型用），免费模型不扣余额
- **在国内必须走 HTTP 代理** 才能连接（Cloudflare CDN 被干扰）
- Python httpx 使用 `proxy="http://127.0.0.1:7890"`（注意是 `proxy` 单数，不是 `proxies`）

### Hermes 完整配置方式

```yaml
# .env
AGNES_AI_API_KEY=sk-your-key
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# config.yaml — 注册为 custom provider
providers:
  custom:
    agnes:
      base_url: https://apihub.agnes-ai.com/v1
      api_key: ${AGNES_AI_API_KEY}
      models:
        - agnes-2.0-flash
        - agnes-image-2.1-flash

# config.yaml — 配置辅助视觉
auxiliary:
  vision:
    provider: custom
    model: agnes-2.0-flash
    base_url: https://apihub.agnes-ai.com/v1
    api_key: ${AGNES_AI_API_KEY}
    timeout: 120

# config.yaml — 配置文生图（可选）
image_gen:
  provider: custom
  model: agnes-image-2.1-flash
  base_url: https://apihub.agnes-ai.com/v1
  api_key: ${AGNES_AI_API_KEY}
  timeout: 120
  n: 1
  size: 1024x1024
```

---

## 2. 商汤 SenseNova 6.7 Flash-Lite

- **免费额度:** 1500 次 / 5 小时（公测期）
- **Base URL:** `https://token.sensenova.cn/v1`
- **模型:** `sensenova-6.7-flash-lite`
- **格式:** OpenAI 兼容，支持 `image_url` 输入
- **注册:** [sensenova.cn/token-plan](https://sensenova.cn/token-plan) → 国内手机号注册
- **架构:** 原生多模态（图片 → 直接理解，非 OCR 中间管道）
- **256K 上下文**

### API 调用示例

```bash
curl https://token.sensenova.cn/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-你的Key" \
  -d '{
    "model": "sensenova-6.7-flash-lite",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "描述这张图片"},
          {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
      }
    ]
  }'
```

### 注意事项

- 最多创建 20 个 API Key
- 仅限国内网络（服务部署在国内，代理可能导致连接失败）
- 公测期随时可能结束
- 26 个开源办公 Skills 可用

### Hermes 配置方式

```yaml
auxiliary:
  vision:
    provider: sensenova
    model: sensenova-6.7-flash-lite
    base_url: https://token.sensenova.cn/v1
    api_key: ${SENSENOVA_API_KEY}
```

---

## 3. EasyOCR (本地离线兜底)

- **零成本**，纯本地运行
- 仅 OCR（光学字符识别），非真正的 VLM
- 适合提取图片中的文字，不适合理解图片语义

### 安装与使用

```python
import easyocr
reader = easyocr.Reader(['ch_sim', 'en'])
result = reader.readtext('image.jpg')
for (bbox, text, confidence) in result:
    print(f'{text} ({confidence:.2f})')
```

---

## Quick Comparison

| Provider | Cost | Speed | Quality | Setup Effort | Best For |
|----------|------|-------|---------|-------------|----------|
| SiliconFlow Qwen3-VL-32B | 按量付费 | ~60-120s | Best | Already configured | Scientific figures, dense annotations |
| Agnes AI Agnes-2.0-Flash | Free + unlimited | Fast (vision) / ~10s (image gen) | Good (vision) / Decent (image gen) | Quick signup + proxy setup | Daily vision, quick checks, image gen, video gen |
| SenseNova 6.7 Flash-Lite | Free (1500/5h) | Fast | Good | Phone registration | Native multimodal, Chinese content |
| EasyOCR | Free | Instant | Text-only | pip install | Text extraction, offline fallback |

## Amaranth Wiki Recommended Pipeline

```
Primary:   SiliconFlow Qwen3-VL (via SILICONFLOW_KEY)
Fallback:  Agnes AI Agnes-2.0-Flash (free, unlimited vision + image gen)
Last:      SenseNova 6.7 Flash-Lite (free, native multimodal)
Offline:   EasyOCR (local, zero-cost offline)
```
