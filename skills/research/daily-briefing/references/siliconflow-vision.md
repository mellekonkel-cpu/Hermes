# SiliconFlow Vision Analysis (Qwen3-VL)

When the main model (DeepSeek) doesn't support `image_url`, use SiliconFlow's API directly for image analysis.

## Available Models (confirmed working)

| Model | Speed | Quality | Best for |
|-------|-------|---------|----------|
| `Qwen/Qwen3-VL-8B-Instruct` | Fast | Good | Food, objects, scenes |
| `Qwen/Qwen3-VL-32B-Instruct` | Slower | Better | Complex visual reasoning |
| `Qwen/Qwen3-VL-32B-Thinking` | Slowest | Best | Deep analysis with reasoning |

## Working Code Pattern

```python
import base64, json, urllib.request

# 1. Read key from .env
with open('/opt/data/.env') as f:
    for line in f:
        if 'SILICONFLOW_KEY' in line and '=' in line:
            key = line.strip().split('=', 1)[1]
            break

# 2. Base64-encode the image
with open('/path/to/image.jpg','rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

# 3. Build the request
payload = {
    'model': 'Qwen/Qwen3-VL-8B-Instruct',  # or 32B
    'messages': [{
        'role': 'user',
        'content': [
            {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{img_b64}'}},
            {'type': 'text', 'text': '分析这张图片里的内容'}
        ]
    }],
    'max_tokens': 800
}

req = urllib.request.Request(
    'https://api.siliconflow.cn/v1/chat/completions',
    data=json.dumps(payload).encode(),
    headers={
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
)
resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
print(resp['choices'][0]['message']['content'])
```

## Avoiding "Argument list too long"

When the image is large, the base64 string exceeds shell argument limits. **Write payload to a file first**:

```python
import json
# ... build payload as above ...
with open('/tmp/vision_payload.json', 'w') as f:
    json.dump(payload, f)
with open('/tmp/silicon_key.txt', 'w') as f:
    f.write(key)

# Then use curl:
# curl -s --max-time 90 https://api.siliconflow.cn/v1/chat/completions \
#   -H "Authorization: Bearer *** /tmp/silicon_key.txt)" \
#   -H "Content-Type: application/json" \
#   -d @/tmp/vision_payload.json > /tmp/vision_result.json
```

## Listing Available Models

```bash
curl -s https://api.siliconflow.cn/v1/models \
  -H "Authorization: Bearer *** SILICONFLOW_KEY /opt/data/.env | cut -d= -f2)" \
  | python3 -c "import sys,json; data=json.load(sys.stdin); [print(m['id']) for m in data.get('data',[]) if 'vl' in m['id'].lower() or 'vision' in m['id'].lower()]"
```

## Key Location

The key lives in `/opt/data/.env` as `SILICONFLOW_KEY=sk-...`

## Limits

- Max image size: ~20MB (tested)
- Max tokens per response: configurable (tested up to 800)
- Timeout: 60-90 seconds recommended for large images
