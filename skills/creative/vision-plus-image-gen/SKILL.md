---
name: vision-plus-image-gen
description: 看图+画图协作管道。商汤 SenseNova 和 Agnes AI 在视觉理解和文生图两个环节中协同工作，由 DeepSeek 主模型串联。实现 1+1>2 的效果。
category: creative
---

# 看图+画图协作管道

当用户提出"看这张图然后画个类似的/换个风格/换个主体"或任何涉及图片理解和生成的需求时，使用本管道。

核心理念：**两个环节都让商汤和 Agnes 协作**，不是各干各的。

## 能力矩阵

| 环节 | 商汤 SenseNova | Agnes AI |
|---|---|---|
| 👁️ **看图** | `sensenova-6.7-flash-lite` ✅ 快（<5s） | `agnes-2.0-flash` ✅ 慢（~47s）但角度不同 |
| 🎨 **画图** | `sensenova-u1-fast` ✅ 已通 | `agnes-image-2.1-flash` ✅ 快（~13s） |

## 架构

| 环节 | 角色 |
|---|---|
| 🧠 **主模型** | DeepSeek `deepseek-v4-flash` — 主脑，连接所有能力，汇总意见 |
| 👁️ **视觉理解** | `auxiliary.vision` → 商汤 `sensenova-6.7-flash-lite`（默认快速通道）<br>手动再调 Agnes `agnes-2.0-flash` 做二次分析 |
| 🎨 **文生图** | Agnes `agnes-image-2.1-flash`（主通道）+ 商汤 `sensenova-u1-fast`（备选/对比） |

## 工作流程

### 👁️ 看图协作

当用户发来一张图要求理解时：

1. **商汤快速看** — 调用 `vision_analyze(image_url, question="详细描述这张图")`，自动走 `auxiliary.vision`，数秒返回结构化描述
2. **Agnes 补充看** — 手动调用 Agnes AI chat completions 传图片 URL（端点：`https://apihub.agnes-ai.com/v1/chat/completions`，模型 `agnes-2.0-flash`，用 OpenAI 兼容的 `image_url` 格式）。**注意 timeout 要设 60-120s**，Agnes 看图较慢
3. **汇总** — DeepSeek 对比两家的分析结果，整合成一份更全面的理解（商汤重结构细节，Agnes 重整体印象）

```python
# Agnes 看图参考代码
import urllib.request, json
data = json.dumps({
    "model": "agnes-2.0-flash",
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": "描述这张图片"},
        {"type": "image_url", "image_url": {"url": image_url}}
    ]}],
    "max_tokens": 200
}).encode()
req = urllib.request.Request(
    "https://apihub.agnes-ai.com/v1/chat/completions",
    data=data,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {agnes_key}"}
)
resp = urllib.request.urlopen(req, timeout=120)  # 至少 60s+
agnes_analysis = json.loads(resp.read().decode())["choices"][0]["message"]["content"]
```

### 🎨 画图协作

当用户要求生成或修改图片时：

1. **Agnes 主通道** — 调用 `agnes-image-2.1-flash`（快，~13s）
2. **商汤备选通道** — 同时调用 `sensenova-u1-fast`（端点：`/v1/images/generations`，需要传 `size` 参数，可选值: 1664x2496, 2496x1664, 1760x2368, 2368x1760, 1824x2272, 2272x1824, 2048x2048, 2752x1536, 1536x2752, 3072x1376, 1344x3136）
3. **互相评价** — 用商汤看 Agnes 的图给出改进建议，或用 Agnes 看商汤的图做风格评析
4. **择优/融合** — 根据两边结果和用户偏好，选更好的图，或描述差异让用户选择

```python
# 商汤文生图参考代码
data = json.dumps({
    "model": "sensenova-u1-fast",
    "prompt": prompt,
    "n": 1,
    "size": "2048x2048"
}).encode()
req = urllib.request.Request(
    "https://token.sensenova.cn/v1/images/generations",
    data=data,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {sn_key}"}
)
resp = urllib.request.urlopen(req, timeout=60)
result = json.loads(resp.read().decode())
image_url = result["data"][0]["url"]
```

### 第三步：保存并展示

```bash
# 下载到传出目录
curl -sL "<image_url>" -o /opt/data/青山/传出/<filename>.png

# 告诉用户
写一段话说明：原图是什么 → 用户要什么改变 → 两家各生了什么图 → 差异在哪 → 保存位置
```

## API Key 读取（Python 安全方式）

```python
env_lines = open("/opt/data/.env").read().splitlines()
agnes_key = ""
sn_key = ""
for l in env_lines:
    if "AGNES_AI_API_KEY=*** in l:
        agnes_key = l.split("=", 1)[1]
    if "SN_API_KEY=*** in l:
        sn_key = l.split("=", 1)[1]
```

⚠ 不要用 `export $(cat .env | xargs)`，key 含 `@` 和 `:` 会破坏 shell 解析。

## 注意事项

- **调用前 unset proxy** — `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY`，两个 API 当前网络都能直连
- **Agnes 看图 timeout 要大** — 至少 60s，实测 ~47s
- **商汤 u1-fast size 参数必传** — 可选值见上方列表，推荐 `2048x2048`
- **视觉描述 prompt** — 调用 `vision_analyze` 时要给具体 question，引导模型关注用户关心的细节
- **Prompt 构造** — 基于视觉分析结果 + 用户意图构造高质量文生图 prompt，可在 prompt 中引用原图的构图、色调、氛围
- **商汤 u1-fast 不是 chat 模型** — 别用 `/v1/chat/completions`，它只支持 `/v1/images/generations`
- **判断哪个模型更适合当前任务** — 风格化/创意图优先 Agnes（快，风格灵活），信息图/正式排版优先商汤（u1-fast 专攻信息图）
