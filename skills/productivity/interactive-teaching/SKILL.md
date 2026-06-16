---
title: Interactive Teaching
name: interactive-teaching
description: Teach technical concepts to beginners using Feynman technique + Socratic questioning + scaffolding. Step-by-step, ask-don't-tell, confirm understanding before advancing.
trigger: User asks to learn a new technical concept (GitHub, git, Python, PR, etc.) OR says "教教我" / "teach me" / "教我xx" OR references Feynman/Socratic teaching method from a video or article.
---

# Interactive Teaching (费曼 + 苏格拉底教学法)

Teach technical concepts to a beginner through structured Q&A, not lecture. Inspired by the Claude Code "learning skill" approach: Feynman technique, Socratic questioning, scaffolding, and encouraging mistakes.

## Core Principles

| Principle | How to apply |
|-----------|-------------|
| **费曼技巧** (Feynman) | Explain the concept in the simplest possible language first. Then ask the user to rephrase in their own words. If they can't, you've found a gap. |
| **苏格拉底式提问** (Socratic) | Don't give the answer outright. Ask leading questions that force the user to connect dots themselves. |
| **脚手架** (Scaffolding) | Break the concept into layers. Cover layer 1 → confirm understanding → layer 2 → confirm → layer 3. Never go two layers ahead of where the user is. |
| **鼓励犯错** (Encourage mistakes) | Explicitly tell them "you can be wrong, that's fine". Create a safe space. When they guess wrong, explain why it's wrong and what the right direction is. |

## 开场规则（先亮底牌）

在开始教学前，先说清楚规则：

> "我不会一口气把所有东西倒给你。每讲完一个概念就问你一句，确保你真的懂了再往下走。你可以答错，可以说'不懂'，那是正常的。"

这能消除用户的压力，建立安全的学习氛围。

## Teaching Protocol

### Step 1: Establish the mental model (费曼版)

Begin with a real-world analogy the user already understands. In this session:
- GitHub → "百度网盘 + 修改历史 + 多人协作" (based on their Word论文/U盘 workflow)
- PR → compared to their existing 导师改论文 process
- Branch → separate copy to experiment in

Analogy rules:
- Must be based on something the user **already does**
- Keep it under 3 sentences
- End with: "你用自己的话理解一下，你觉得XX是什么？"

### Step 2: First checkpoint (confirm understanding)

After the analogy, ask an open-ended question that forces them to articulate it back. Not "懂了吗？" (yes/no trap) but rather:
- "你觉得XX和你平时做Y的方式，最大的区别是什么？"
- "如果用一句话跟别人解释XX，你会怎么说？"

**Do NOT advance until they demonstrate understanding in their own words.**

### Step 3: Scaffold the next layer

Once checkpoint passed, introduce the next concept as a **contrast** or **extension** of what they just learned. For example:
- 导师改论文 → PR (compare and contrast)
- Fork → "复制别人的项目到你名下"

Use comparison tables for contrast:

| | Concept A | Concept B |
|--|-----------|-----------|
| Who does the work? | ... | ... |
| Who decides? | ... | ... |

### Step 4: Second checkpoint (deepen understanding)

Ask a compare-and-contrast question that requires them to apply both concepts:
- "你觉得这两种方式各自在什么场景下更合适？"
- This forces higher-order thinking, not just recall.

### Step 5: Handoff to practice

Once conceptual understanding is solid, transition to hands-on:
- 接下来我们动手。按这个顺序：1) 2) 3) 准备好了吗？
- List the exact steps in order
- Let them confirm before starting

**优先方案：从用户自己的仓库开始，而不是 fork 别人的。**
- 让用户在网页上创建新仓库（github.com/new）是最好的一步，零风险、有成就感
- Fork + Edit + PR 流程涉及的概念太多（fork、分支、PR、base/head、maintainer），新手容易迷失
- 推荐序列：创建自己的仓库 → 推送本地内容 → 网页编辑自己仓库 → 学会 PR 概念后，再 fork 别人的做 PR
- 详见 references/github-teaching-analogies.md 中的"备用实操路径"

## Sequence Template (for technical concepts)

```
Layer 1: What is X? (real-world analogy + user rephrases)
Layer 2: How does X differ from what user already knows? (compare/contrast)
Layer 3: Related concepts (extend from Layer 2)
Layer 4: Hands-on practice (if applicable)
```

## Pitfalls

- **不要问"懂了吗"** — 用户会条件反射说懂了。必须让他们用自己的话解释。
- **不要一次讲太多** — 两个概念之间一定要有确认环节。用户能复述 = 真懂了。
- **不要纠正得太快** — 用户答错了，先问"为什么你觉得是这样？"了解他们的思维过程，再指出具体哪里错了。
- **不要用专业术语解释专业术语** — 比如不要用"repository"解释"fork"，用"复制别人的项目到你的账号"。
- **如果用户说"算了""以后再说"** — 尊重节奏，把进度保存下来（save to memory/README），下次从断点继续。
- **教 Web UI 操作时，给位置指引 > 给动作指引** — 不要只说"点提交按钮"，要说明"编辑框下面，往下滚，有一个 Commit changes 标题，下面绿色的 Commit changes 按钮"。零基础用户在页面上找不到按钮是高频卡点。
- **当用户说"重新开始吧，我已经有点迷茫"** — 立即切换到更简单的方案。不要试图在原有路径上补充说明，直接重置到最少步骤的最小可行方案。
- **避免让新手导航到 /compare 页面** — 新手自己仓库的 /compare 页面会显示一个空比较（base=main, compare=main），没有任何差异，用户看到后会困惑。直接引导他们到正确的 PR 路径：从 fork 的仓库主页 → Pull requests → New Pull Request。

## Session Interruption Handoff

When a teaching session is interrupted before the user completes all hands-on steps (network down, user has to leave, proxy expired, etc.):

1. **Save conceptual progress to memory** — Record which layers the user has completed and which remain, using concise declarative facts (under 200 chars).
2. **Prepare a local artifact** — Create a local working directory with README capturing what was learned, a PRACTICE.md with the remaining steps, and any scaffold files the user will need. If applicable, git init and commit so it is push-ready when connectivity is restored.
3. **Give a clear resume path** — Tell the user exactly what command(s) to run when they are back (e.g. "when your proxy is restored, run: `git remote add origin ... && git push`").
4. **Reference existing analogies** — See `references/github-teaching-analogies.md` for the analogy set used in one successful session with a Chinese-speaking beginner.
