---
title: 排障手册
description: 组件级故障排查——按频率排序，30 秒定位
---

> 所有故障按频率排序，最常见的排最前面。

## 微信网关

### 连不上 / 消息发不出

**症状：** 消息发出去没回复，日志出现 `Cannot connect to host ilinkai.weixin.qq.com` 或 `rate limited`

**30 秒定位：**

```bash
ps aux | grep "hermes gateway run"                  # ① 进程活着吗？
cat /opt/data/gateway_state.json | python3 -m json.tool    # ② 连接状态？
tail -20 /opt/data/logs/agent.log                    # ③ 最新错误？
```

**#1 原因：代理冲突** — gateway 继承了代理环境变量，连不上国内微信服务器

```bash
pkill -f "hermes gateway run"
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
HERMES_ALLOW_ROOT_GATEWAY=1 /opt/hermes/.venv/bin/hermes gateway run --replace
```

永久修复：修改 s6 run 脚本（`find /run -name "run" -path "*/gateway*/run"`），在 `exec` 前加 `unset http_proxy`。

**#2 原因：iLink 限流** — 日志出现 `rate limited`，消息能收到但发不出回复

重启 gateway（同上），等 1-2 分钟让限流计数器复位。不要在限流期间连续重发，会加剧问题。

**#3 原因：s6 路径/环境问题**

- HOME 路径不对 → 确认 s6 run 脚本中 `HOME` 指向实际 home 目录（含 `.env` 的位置）
- 锁文件被 root 抢占 → `rm -f /opt/data/gateway.lock /opt/data/gateway_state.json` 后重启
- state.json 引用僵尸 PID → 对照 `ps aux` 确认 PID 存活

## Docker / 容器

### 权限问题

```bash
sudo usermod -aG docker $USER
# 退出重新登录
```

### 容器内 GPU 不可用

```bash
# 安装 NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 容器映射目录为空

检查 Docker Desktop → Settings → Resources → WSL Integration，确保对应发行版已开启集成。

## 网络与代理

### 代理启动顺序

mihomo 启动时若订阅 URL 尚未拉取完成，容器虽运行但无可用节点。启动后检查：

```bash
docker compose logs mihomo | tail -20
```

### 订阅链接过期

```bash
curl -x http://127.0.0.1:7890 -I https://api.openai.com
```

过期则所有海外 API 调用失败。

### 日本节点带宽限速

日本节点 ping 低但流式响应易超时（Codex / PackyAPI 大 payload SSL EOF）。切到美国节点：

```bash
curl -X PUT http://127.0.0.1:9090/proxies/Proxies \
  -d '{"name": "US"}'
curl -X PUT http://127.0.0.1:9090/proxies/US \
  -d '{"name": "🇺🇸 美国实验性 IEPL 专线 1"}'
```

## Hermes Agent

### Docker 部署顺序

一次性启动全部容器时，mihomo 可能尚未就绪。分步启动或等 mihomo 日志显示节点已加载再发请求。

### CI Secret 名不一致

GitHub Actions 中 Secret 名必须与 workflow 文件完全一致。本站使用 "CLOUDFARE"（非标准拼写）。

### Codex 认证方式

Codex 同时支持 ChatGPT Plus OAuth 和 API Key 两种认证，不是只能 OAuth。

## GPU / ComfyUI

### `--force-fp16` 参数必须开启

SDXL 默认 FP32 推理，12GB 显存直接 OOM。启动 ComfyUI 时必须加 `--force-fp16`。

### 自定义节点版本冲突

ComfyUI 自定义节点的依赖互相覆盖时，用 venv 隔离或 docker 分装。

### Docker 内 torch 装不上

WSL2 + Docker 容器内 `pip install torch` 可能挂死，手动下载 wheel 安装。详见 `notes/gpu-training-pitfalls`。
