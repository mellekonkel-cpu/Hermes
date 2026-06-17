---
name: delegate
description: 基于 Hermes Kanban 的异步任务委派系统——大任务拆解后后台执行，前台秒回不阻塞。7 大瓶颈全解决。
version: 2.0.0
author: Amaranth (adapted)
license: CC BY-NC-SA 4.0
metadata:
  hermes:
    tags: [delegate, async, kanban, orchestration]
    related_skills: [kanban-orchestrator, kanban-worker]
    source: "https://wiki-for-amaranth.pages.dev/skill-share/async-delegate/"
    adapted_from: "Amaranth Wiki Async Delegate"
---

# Delegate — 异步任务委派系统

基于 Hermes Kanban 的异步任务处理架构。核心原则：**大任务拆解为子任务 → kanban_create() 派发 → 秒回"已提交" → worker 后台执行**。小任务直接干。

## 为什么不用 delegate_task()

Hermes 内置的 `delegate_task()` 是 **同步阻塞的**——主 agent 派发子任务后必须等所有子任务完成，期间用户不可用。Kanban 方案将任务持久化到 SQLite，通过 gateway dispatcher 异步派发给独立 worker 进程，主 agent 立即释放。详见 [Amaranth Wiki](https://wiki-for-amaranth.pages.dev/skill-share/async-delegate/)。

---

## 架构

```
用户 → 主 Agent（前台）
         │ kanban_create() × N → 立即返回"已提交"
         ↓
      Kanban Queue (SQLite, WAL 模式)
         │ dispatcher 每 5s 轮询
         ↓
      worker profile（独立 OS 进程，完整工具集）
         │ 读卡片 → 执行 → 验证 → kanban_complete()
```

任务生命周期：

```
创建(ready) → 派发(running) → 完成(done)
                              → 阻塞(blocked，需人工介入)
                              → 失败重试(failure_limit 次内自动)
                              → 超时回滚(stale_timeout 后重置 ready)
```

## 7 大瓶颈与解决方案

| # | 瓶颈 | 等级 | 方案 |
|---|------|:----:|------|
| 1 | `delegate_task()` 同步阻塞 | P0 | 全量迁移至 Kanban，主 agent 秒回 |
| 2 | Worker 崩溃无回收 | P1 | `stale_timeout=600s` + `failure_limit=3` |
| 3 | API Key 过权限（提示注入风险） | P0 | Worker profile 独立 .env，保留最少 key |
| 4 | 输出路径无限制（覆盖系统文件风险） | P0 | output_path 硬性白名单 |
| 5 | Shell 传参换行符丢失 | P0 | 用 stdin 读取多行 body |
| 6 | Max Turns 耗尽卡死 | P1 | ≤5 turns 时主动 kanban_block() |
| 7 | 完成验证缺失（summary 自述不可信） | P1 | 完成前检查 output_path 文件真实存在 |

---

## 参数推荐

| 参数 | 推荐值 | 说明 |
|------|:------:|------|
| `dispatch_interval` | 5s | Dispatcher 轮询间隔 |
| `stale_timeout` | 600s (10min) | 任务卡死后自动回收回滚 |
| `failure_limit` | 3 | 重试次数，超限标记 failed |
| `max_concurrent` | 3 | 每 profile 同时运行的任务数 |
| `worker max_turns` | 90 | 每 worker 最大对话轮数 |

```bash
hermes config set kanban.dispatch_interval_seconds 5
hermes config set kanban.failure_limit 3
hermes config set kanban.max_in_progress_per_profile 3
hermes config set kanban.dispatch_stale_timeout_seconds 600
hermes config set kanban.default_assignee worker
```

## Profile 特化

| Profile | 主模型 | 副模型 | 专精 |
|---------|-------|-------|------|
| **worker** | DeepSeek V4 Flash | — | 通用任务 |
| compute | DeepSeek V4 Flash | Gemini 3.1 Pro | ORCA/计算/对接 |
| code | DeepSeek V4 Flash | Claude Sonnet | 脚本/coding/debug |
| writer | Claude Sonnet | DeepSeek V4 Flash | Wiki/翻译/润色 |
| researcher | Gemini 3.1 Pro | DeepSeek V4 Flash | 文献/深度分析 |

## 行为规则

**路由决策：**
- 大任务（3+步/需调研/需持久产出）→ `kanban_create()` → 秒回"已提交"
- 小任务（1步/纯回复）→ 直接干 → 正常回
- **禁止在回复前做调研**

**Worker 约束（写入 worker SOUL.md）：**
- 卡片 body 含全部需求，不调用 `clarify()`
- 每步用 `kanban_comment()` 记录进度
- 剩余 turns ≤ 5 仍未完成 → 主动 `kanban_block()`
- 完成前确认 output_path 文件真实存在
- output_path 必须在白名单目录内（禁止写入 config.yaml/.env/SOUL.md/kanban.db）

## 性能基准（实测）

| 场景 | 耗时 |
|------|------|
| 单文件创建 → 完成 | ~35s（含 5s dispatch + 30s worker） |
| 5 个并行任务批量 | ~2min（并发 3，排队 2） |
| Worker 冷启动 | ~10-15s（MCP + skill 加载） |
| kanban_create 单次 | <1s |
| kanban_list | <0.5s |

## 安全边界

| 维度 | 保障措施 |
|------|---------|
| API key 泄露 | Worker .env 精简至最少 key |
| 文件系统越权 | Output path 白名单 |
| 提示注入 | Worker 不执行用户直接输入，仅执行卡片 body |
| 任务隔离 | 每个 worker 独立进程，互不共享 memory/sessions |
| 崩溃恢复 | Stale timeout 600s + failure_limit 3 自动处理 |

## 安装

```bash
# 初始化 kanban
hermes kanban init

# 创建 worker profile
hermes profile create worker --clone

# 替换 SOUL.md
cp ~/.hermes/skills/software-development/delegate/references/worker-SOUL.md \
   /opt/data/profiles/worker/SOUL.md

# 配置 kanban 参数（见上）
```
