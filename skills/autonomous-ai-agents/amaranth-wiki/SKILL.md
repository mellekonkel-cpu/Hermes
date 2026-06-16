---
name: amaranth-wiki
description: Source Hermes Agent skills and configurations from the Amaranth Wiki (wiki-for-amaranth.pages.dev) — a personal knowledge base with downloadable Hermes skill packs, architecture guides, and setup recipes.
version: 1.1.0
author: Hermes Agent
license: CC BY-NC-SA 4.0
metadata:
  hermes:
    tags: [wiki, skills, installation, hermes, kanban]
    related_skills: [delegate, native-mcp, hermes-agent-skill-authoring]
    wiki_url: "https://wiki-for-amaranth.pages.dev/"
    github_repo: "HTZY08/wiki-for-Amaranth"
---

# Amaranth Wiki — 技能来源与配置参考

Amaranth Wiki 是用户的个人知识库，托管于 Cloudflare Pages，源码在 GitHub `HTZY08/wiki-for-Amaranth`。其中的 **📦 Skill 分享** 板块提供可下载的 Hermes Agent 技能包。

## 访问方式

```bash
# 网页浏览
open https://wiki-for-amaranth.pages.dev/

# CLI 获取内容（推荐）
curl -sL "https://raw.githubusercontent.com/HTZY08/wiki-for-Amaranth/main/src/content/docs/skill-share/<page>.md"
```

## 导航结构

wiki 侧边栏的 **📦 Skill 分享** 下包含：
- **目录** — 所有技能的概览页
- **Review Writing** — 化学生物综述写作技能包
- **Async Delegate** — 基于 Kanban 的异步任务委派系统
- **Resonance Engine** — 基于共现矩阵的智能 skill 推荐引擎（纯 Python 包，非 Hermes skill 结构）
- **Search Routing** — 搜索路由架构指南（⚠ 非可下载包，见下文）

其他相关板块：
- **🤖 Hermes Agent** — Hermes Agent 完整搭建手册
- **🆓 白嫖指南** — 免费 API 资源

## 技能安装流程

所有技能包以 `.tar.gz` 形式托管在 GitHub 仓库的 `static/skills/` 目录下。

### Step 1: 获取下载链接

从 wiki 页面找到 tar.gz 链接，或在 GitHub 上直接获取：

```bash
# 查看仓库中的技能包列表
curl -sL "https://api.github.com/repos/HTZY08/wiki-for-Amaranth/contents/static/skills/<skill-name>"
```

### Step 2: 下载并解压

```bash
# 下载
curl -sL "https://raw.githubusercontent.com/HTZY08/wiki-for-Amaranth/main/static/skills/<skill-name>/<file>.tar.gz" \
  -o /tmp/<file>.tar.gz

# 解压到 skills 目录
tar xzf /tmp/<file>.tar.gz --no-same-permissions -C ~/.hermes/skills/
```

### Step 3: 查看 SKILL.md 获取安装说明

```bash
cat ~/.hermes/skills/<skill-name>/SKILL.md
```

### Step 4: 执行安装步骤

每个技能包的 SKILL.md 包含具体的配置步骤。通用模式包括：
- `hermes kanban init` — 初始化 Kanban DB
- `hermes profile create <name> --clone` — 创建专用 Profile
- `hermes config set <key> <value>` — 修改配置参数

### ⚠ 鉴别 skill 类型

并非所有 wiki tar.gz 都是 Hermes skill 包。安装前需区分：

| 类型 | 特征 | 解压目标 | 示例 |
|------|------|----------|------|
| **Hermes Skill 包** | 内含 `SKILL.md`（YAML frontmatter） | `~/.hermes/skills/<category>/` | review-writing, async-delegate |
| **纯 Python 工具包** | 无 SKILL.md，含 `.py` + README.md | 独立工具目录（如 `/opt/data/<name>/`） | resonance-engine |
| **模板/配置包** | 无 SKILL.md，含 `.yaml`/`.json`/`.md` | 按具体用途放置 | — |

方法：先 `tar tzf <file>.tar.gz` 检查顶层文件结构。有 `SKILL.md` 的才是 Hermes skill 包。

## 已安装技能

### Async Delegate (`delegate`)

安装于 `~/.hermes/skills/software-development/delegate/`。

**配置要点：**
```bash
# 初始化 kanban
hermes kanban init

# 创建 worker profile
hermes profile create worker --clone

# 替换 worker SOUL.md 为 worker-SOUL.md 模板
cp ~/.hermes/skills/software-development/delegate/references/worker-SOUL.md \
   /opt/data/profiles/worker/SOUL.md

# 配置 kanban 参数（推荐值）
hermes config set kanban.dispatch_interval_seconds 5
hermes config set kanban.failure_limit 3
hermes config set kanban.max_in_progress_per_profile 3
hermes config set kanban.dispatch_stale_timeout_seconds 600
hermes config set kanban.default_assignee worker
```

**行为规则：**
- 大任务（3+步/需调研/需持久产出）→ `kanban_create()` → 秒回"已提交"
- 小任务（1步/纯回复）→ 直接干 → 正常回
- Worker 禁止调用 `clarify()`，卡片 body 含全部需求

**Profile 模板：** 见 `references/worker-SOUL.md`

**Worker 关键约束：**
- 卡片 body 含全部需求，不调用 clarify()
- 每步用 kanban_comment() 记录进度
- 完成前确认 output_path 文件存在
- output_path 必须在白名单目录内
- 剩余 turns ≤ 5 仍未完成则主动 kanban_block()

### Review Writing (`review-chem-bio-pipeline` 等 4 个 skill)

安装于 `~/.hermes/skills/research/`，含 4 个技能：
- `review-chem-bio-pipeline` — 8 阶段写作管道
- `review-chem-bio-writing` — 写作规范
- `precision-review-search` — 精确学术搜索
- `paper-figure-mapper` — 论文配图映射

### Resonance Engine (`resonance-engine`)

安装于 `/opt/data/resonance-engine/`。**非 Hermes skill 结构**，而是纯 Python 包——解压后自带 venv，不放入 `~/.hermes/skills/`。

**安装要点：**
```bash
# 下载
curl -sL "https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/resonance-engine/resonance-engine.tar.gz" -o /tmp/resonance-engine.tar.gz

# 解压到独立目录（不要解压到 ~/.hermes/skills/！）
mkdir -p /opt/data/resonance-engine
tar xzf /tmp/resonance-engine.tar.gz --no-same-permissions --strip-components=1 -C /opt/data/resonance-engine/

# 创建 venv + 安装依赖
cd /opt/data/resonance-engine
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scipy
```

**核心用法：**
- 核心引擎：`resonance/matrix_engine.py` 中的 `ResonanceEngine` 类
- 构建管道：`resonance_cron.py`（需自行提供 `skill_monitor` 适配模块对接 Agent 日志）
- 查询示例：
  ```python
  from resonance import ResonanceEngine, NodeRegistry
  engine = ResonanceEngine()
  v0 = engine.build_v0("需要查论文引用")
  result = engine.compute(v0)
  ```

**性能：** 矩阵构建 ~36ms (N=500)，共振计算 <10ms，Precision@5=0.912

**三平面架构：**
- **Skill 平面** — agent skill 注册表
- **Memory 平面** — hindsight.db 记忆节点
- **Soul 平面** — SOUL.md 行为规则
- 跨平面边以 γ=0.5 折扣处理

**注意：** `resonance_cron.py` 引用的 `skill_monitor` 模块未包含在 tar.gz 中，需按 Agent 框架自行实现 session 日志对接。

## 注意

### Search Routing 是架构指南，非可下载包

wiki 中的 **Unified Search Routing** 页面是架构设计文档，不包含可下载的 tar.gz。它描述了需要自行创建的三层搜索路由架构：

1. **MCP 统一搜索服务器** (`/opt/data/scripts/mcp_search_server.py`) — 聚合 9 引擎的 MCP 服务
2. **公共 API 路由 skill** (`~/.hermes/skills/software-development/public-api-brain-router/SKILL.md`)
3. **TinyFish 搜索 skill** (`~/.hermes/skills/research/tinyfish-search-fetch/SKILL.md`)

需要 `mcp` Python 包（`pip install mcp`）和搜索 API Key。

### 搜索 API Key 需求

| 引擎 | 环境变量 | 注册 |
|------|----------|------|
| Tavily | `TAVILY_API_KEY_1` 等 | tavily.com (1000次/月) |
| AnySearch | `ANYSEARCH_API_KEY_OUTLOOK` 等 | anysearch.ai |
| Firecrawl | `FIRECRAWL_API_KEY_GOOGLE` 等 | firecrawl.dev (500次/月) |
| You.com | `YOUCOM_API_KEY_GOOGLE` 等 | you.com |
| Exa | `EXA_API_KEY` | exa.ai (1000次/月) |
| Serper | `SERPER_API_KEY` | serper.dev (2500次/月) |
| TinyFish | `~/.tinyfish-key` | tinyfish.io (5次/分钟) |

### License

所有技能包遵循 CC BY-NC-SA 4.0，仅供个人学习、研究、开发使用，禁止商用。
