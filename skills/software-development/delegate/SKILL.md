---
name: delegate
description: 通过 Hermes Kanban 实现异步任务委派——大任务拆解后交给后台 worker 执行，前台保持响应。小任务直接干。
version: 1.0.0
author: Amaranth
license: CC BY-NC-SA 4.0
metadata:
  hermes:
    tags: [delegate, async, kanban, orchestration]
    related_skills: [kanban-orchestrator, kanban-worker]
    source: "https://wiki-for-amaranth.pages.dev/skill-share/async-delegate/"
---

# Delegate — 异步任务委派系统

基于 Hermes Kanban 的异步任务处理架构。大任务拆解为子任务，通过 `kanban_create()` 派发给后台 worker profile 执行，主 agent 立即回复用户不阻塞。

## License

CC BY-NC-SA 4.0。仅供个人学习、研究、开发使用，禁止商用。

## 架构

```
用户 → 主 Agent（前台）
         │ kanban_create() × N → 立即返回
         ↓
      Kanban Queue (SQLite)
         │ dispatcher 每 N 秒轮询
         ↓
      worker profile（后台独立进程）
         │ 读卡片 → 执行 → 写产出
         │ kanban_complete() 完成
```

## 使用

```bash
# 初始化 kanban
hermes kanban init

# 创建 worker profile
hermes profile create worker --clone

# 更新 worker SOUL.md 为 references/worker-SOUL.md 的内容

# 创建任务
hermes kanban create "任务标题" --body "任务描述" --assignee worker
```

## 参数

| 参数 | 推荐 | 说明 |
|------|------|------|
| dispatch_interval | 5s | 轮询间隔 |
| stale_timeout | 600s | 崩溃回收 |
| failure_limit | 3 | 重试次数 |
| max_concurrent | 3 | 并发数 |

## 行为规则

大任务（3+步/需调研/需持久产出）→ kanban → 秒回"已提交"
小任务（1步/纯回复）→ 直接干 → 正常回
**禁止在回复前做调研**。

## Profile 模板

`references/` 目录下 worker-SOUL.md 模板：
| Profile | 专精 |
|---------|------|
| worker | 通用 |
