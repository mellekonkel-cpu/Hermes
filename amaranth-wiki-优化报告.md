# 系统优化报告

> 来源：Amaranth Wiki (wiki-for-amaranth.pages.dev) — 学习总结
> 生成时间：2026-06-17

---

## 已实施的优化

### 1. Ops Profile 错误记录协议 ✅

安装 `/opt/data/skills/devops/ops-profile/SKILL.md`

借鉴 Amaranth 的 Ops Worker 设计，今后所有系统缺陷记录采用四段式格式：

```
[现象] <具体错误/症状>
[原因] <根因分析>
[修复] <实际解决步骤>
[坑] <下次避免这个问题的提示>
```

已迁移已知缺陷（s6 重启循环、网关启动挂起、.env proxy 覆盖等）到 ops-profile 技能中。

### 2. 视觉 + 画图全链路协作 ✅

之前配置，参考 Amaranth Wiki 的架构思想：
- `auxiliary.vision` → 商汤 `sensenova-6.7-flash-lite`（看图）
- Agnes AI `agnes-image-2.1-flash` + 商汤 `sensenova-u1-fast`（双引擎画图）
- 双引擎看图：商汤快（~3s）+ Agnes 慢（~47s）不同视角

### 3. 错误记忆协议已在 memory 中启用 ✅

---

## 值得关注的优化方向（待实施）

### 方向 A：Search Routing（搜索路由降级）

Amaranth Wiki 描述了一套完整的 MCP 搜索路由系统，聚合 9 个引擎，按 mode 自动选首引擎，失败自动降级：

| mode | 首引擎 | 说明 |
|------|--------|------|
| auto | tinyfish | 免费，5次/分钟 |
| zh | anysearch | 中文优化 |
| academic | exa | 论文搜索 |
| google | serper | Google 风格 |

**价值：** 当前使用 Heremes 内置 web_search，引擎选择有限。MCP 路由能大幅提升搜索成功率。

**成本：** 需要注册多个搜索引擎的 API Key，部署 MCP 服务器。

### 方向 B：Cloud Server 部署（24/7 在线）

Amaranth 在腾讯云 ¥99/年 的服务器上跑了完整的 Hermes + 微信网关。

**价值：** 当前在 WSL 上跑，Windows 关机后服务停止。云服务器能做到 24h 在线。

**成本：** ¥99/年 + 配置时间。

### 方向 C：SiliconFlow 文生图备用通道

Amaranth Wiki 描述了硅基流动（siliconflow.cn）的免费额度方案。可作为 Agnes AI + 商汤之外的第三画图通道。

**价值：** 多一个不花钱的生图渠道，风格更多样。

**成本：** 需注册手机号获取 API Key。

### 方向 D：多模型路由增强

当前 fallback_providers 只配了商汤。可在 fallback 链中加入更多模型：
- 小米 MiMo (token-plan-cn.xiaomimimo.com) — 商汤同款 Token Plan
- SiliconFlow 上的开源模型

**价值：** DeepSeek 挂掉时有更多兜底选择。

---

## 从 Amaranth Wiki 学到的架构原则

1. **错误结构化记录** — 不是"重启解决了"，是"因为 X 所以 Y 所以修好了"
2. **三层路由** — backbone + vision + fallback 分层清晰
3. **no_agent 模式** — 0 token 开销的 cron watchdog 设计
4. **Profile 隔离** — 不同任务用不同 Profile（Ops/Worker 分离）
5. **先计划后执行** — 破坏性操作前出计划，用户确认再动手

---

## 已拉取的技能列表

| 技能包 | 来源 | 状态 |
|--------|------|------|
| async-delegate | Amaranth Wiki | ✅ 已安装 (delegate skill) |
| review-writing (4 skills) | Amaranth Wiki | ✅ 已安装 |
| resonance-engine | Amaranth Wiki | ✅ 已安装 (/opt/data/resonance-engine/) |
| ops-profile | Amaranth Wiki | ✅ **本次安装** |
| social-mcp | Amaranth Wiki | ❌ 未安装（需小红书账号+Docker） |
| search-routing | Amaranth Wiki | ❌ 架构指南，非技能包 |
