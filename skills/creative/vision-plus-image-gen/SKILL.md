---
name: vision-plus-image-gen
description: 看图+画图结合管道。商汤 SenseNova 负责看懂图片，Agnes AI 负责生成新图，DeepSeek 主模型串联。实现 1+1>2 的效果。
category: creative
---

# 看图+画图结合管道

当用户提出"看这张图，然后画一个类似的/改个风格/换个主题"这类需求时，执行以下流程。

## 架构

| 环节 | 服务 | 模型 |
|---|---|---|
| 🧠 主脑 | DeepSeek | `deepseek-v4-flash` (api.deepseek.com) |
| 👁️ 视觉理解 | 商汤 SenseNova | `sensenova-6.7-flash-lite` (auxiliary.vision) |
| 🎨 文生图 | Agnes AI | `agnes-image-2.1-flash` (apihub.agnes-ai.com) |

## 工作流程

### Step 1: 看图片

用户发来图片或图片路径，用 `vision_analyze` 工具分析：

```
vision_analyze(image_url="<图片路径或URL>", question="详细描述这张图")
```

`vision_analyze` 会自动路由到 `auxiliary.vision`（商汤 `sensenova-6.7-flash-lite`）。

### Step 2: 理解用户意图

主模型（DeepSeek）根据视觉分析结果 + 用户的需求，理解要做什么改动：
- 换风格（像素风→水彩风）
- 换主体（猫→狗）
- 延续构图（同角度不同主题）
- 基于图片里的元素创作新内容

### Step 3: 生成新图

调用 Agnes AI 的 `agnes-image-2.1-flash` 模型生成图片：

```python
import os, urllib.request, json

# 从 .env 读取 Agnes key
key_lines = [l for l in open("/opt/data/.env").read().splitlines() if l.startswith("AGNES_AI_API_KEY=")]
key = key_lines[0].split("=", 1)[1]

data = json.dumps({
    "model": "agnes-image-2.1-flash",
    "prompt": "<根据视觉理解和用户意图构造的 prompt>",
    "n": 1
}).encode()

req = urllib.request.Request(
    "https://apihub.agnes-ai.com/v1/images/generations",
    data=data,
    headers={"Content-Type": "application/json", "Authorization": "Bearer " + key}
)
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read().decode())
image_url = result["data"][0]["url"]
```

### Step 4: 保存并展示

```bash
# 下载到传出目录
curl -sL "<image_url>" -o /opt/data/青山/传出/<filename>.png

# 产出一份报告
写一段话说明：原图是什么 → 用户要什么改变 → 生成了什么 → 保存位置
```

## 注意事项

- **Agnes AI 需要绕过代理** — 调用前必须 `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY`（ilinkai.weixin.qq.com 同理，但 apihub.agnes-ai.com 当前无需代理，可直接访问）
- **API Key 读取** — Agnes key 在 `/opt/data/.env` 中，格式 `AGNES_AI_API_KEY=...`
- **Key 含特殊字符** — 用 Python 读取，不要用 shell `export $(cat .env | xargs)`，`@` 和 `:` 会破坏 shell 解析
- **Timeout** — 文生图通常需要 10-30 秒，`urllib` timeout 设 30s
- **网络差异** — `token.sensenova.cn`（商汤，国内直连）和 `apihub.agnes-ai.com`（Agnes，Cloudflare，从当前网络可直连）都能直接访问
- **视觉描述** — 调用 `vision_analyze` 时要给具体 question，引导商汤关注用户关心的细节
- **Prompt 构造** — 基于商汤的视觉分析结果 + 用户的修改意图，构造高质量的文生图 prompt。可在 prompt 中引用原图的构图、色调、氛围等元素
