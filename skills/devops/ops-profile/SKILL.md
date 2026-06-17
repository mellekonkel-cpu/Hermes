---
name: ops-profile
description: 系统运维 Worker Profile — 专精 Docker/代理/故障恢复/配置管理，附带错误记录协议和已知缺陷清单
category: devops
---

# Ops Profile — 系统维护与故障恢复

> 来源：[Amaranth Wiki: Ops Profile](https://wiki-for-amaranth.pages.dev/skill-share/ops-profile/)

专精系统运维的 Hermes 技能模板。核心价值：**错误记录协议**——每次踩坑都按 [现象→原因→修复→避坑] 结构化记录，日积月累形成运维知识库。

## 错误记录协议（Error Logging Protocol）

每次遇到系统缺陷、修复方案、配置陷阱，必须按以下格式写入持久记忆：

```
[现象] <具体错误/症状>
[原因] <根因分析>
[修复] <实际解决步骤>
[坑] <下次避免这个问题的提示>
```

### 触发条件
- ✅ 完成一次诊断/修复后 → 立即写记忆
- ✅ 发现已知缺陷没覆盖的坑 → 立即写
- ✅ 用户纠正了做法 → 反思后写记忆
- ❌ 不要记"当前状态"（磁盘/进程状态）→ 会过时
- ❌ 不要记任务进度（"修好了X"）→ 下次不需要

### 冲突处理
记新记录前，先搜索记忆是否已有同类条目：
- 有且准确 → 不重复写
- 有但不完整 → 替换更新
- 有但错了 → 替换修正

## 已知系统缺陷（当前环境）

### Docker Desktop WSL2 大文件读取 bug
- ❌ `docker run -v /host/path:/container ...` bind mount 大文件 → 只返回16字节
- ✅ `cat /host/file | docker exec -i container sh -c 'cat > /dest'` → 完整文件
- ✅ 或用 Docker volume 代替 bind mount

### s6 网关重启循环
- s6-supervise 管理网关时，iLink 连接超时导致网关退出（~14s-8min），s6 自动重启 → 循环
- ✅ 修复：替换 s6 run script 为 `sleep infinity`，独立启动网关 + cron watchdog

### 代理端口绑定 IPv6
- 某些代理在 WSL2 上把 `0.0.0.0:port` 解析为 IPv6
- ✅ bridge 模式 + 容器 IP 直连
- ⚠️ 不要用 `--network host`

### 带宽限速导致流式响应超时
- ❌ 切到慢节点时流式输出卡死
- ✅ 切低延迟节点或增大 timeout

### 微信网关启动挂起
- 从 `/opt/data` 启动网关会初始化挂起，gateway_state.json 永远不写入
- ✅ 必须 `cd /opt/hermes` 再启动

### .env HTTP_PROXY 覆盖 shell unset
- start-gateway.sh 虽然 unset proxy，但 Python 加载 .env 时重新设了 HTTP_PROXY
- ✅ 从 .env 移除 HTTP_PROXY/HTTPS_PROXY，用 wrapper 脚本显式 export

## 当前系统架构速查

| 组件 | 详情 |
|:----|:-----|
| **运行环境** | WSL2 (Windows Subsystem for Linux) |
| **Hermes** | CLI + Gateway (PID 146, ~1.5h uptime) |
| **主模型** | DeepSeek `deepseek-v4-flash` (api.deepseek.com) |
| **视觉辅助** | 商汤 `sensenova-6.7-flash-lite` (auxiliary.vision) |
| **画图** | Agnes AI `agnes-image-2.1-flash` + 商汤 `sensenova-u1-fast` |
| **代理** | mihomo (v1.19.27, 72 V2NY nodes) |
| **微信** | iLink Bot 协议，已连接 |
| **Skills** | ~675 files, 25 categories |
| **备份** | GitHub: mellekonkel-cpu/Hermes (SSH) |

## 关键路径

| 路径 | 用途 |
|:----|:-----|
| `/opt/data/config.yaml` | Hermes 主要配置 |
| `/opt/data/.env` | API 密钥 |
| `/opt/data/skills/` | 所有技能文件 |
| `/opt/data/gateway_state.json` | 网关状态 |
| `/opt/data/青山/传入/` | 文件交换 - 传入 |
| `/opt/data/青山/传出/` | 文件交换 - 传出 |
| `/opt/data/Hermes-repo/` | GitHub 备份仓库 |

## 代理诊断流程

```bash
# 验证代理
curl -sk --max-time 10 -x http://container-ip:7890 https://httpbin.org/ip
# 检查当前节点
curl -s http://container-ip:9090/proxies/Proxies | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['now'])"
# 代理订阅更新
```

## 规则

- 破坏性操作前必须先出操作计划，等待确认
- 诊断时先排除已知的系统缺陷
- 改配置后始终验证目标文件内容完整性
- 微信网关启动必须 `cd /opt/hermes` + unset proxy
