# GitHub 教学类比集

适用于中文零基础用户的 GitHub + PR 概念教学。与 interactive-teaching 技能配合使用。

## GitHub 是什么

> GitHub = 百度网盘 + 修改历史记录本 + 多人协作工具

三项核心功能：
1. **存代码** — 像百度网盘，但更智能
2. **记历史** — 每一次修改都被记录下来，随时可回退到任何历史版本
3. **多人协作** — 别人可以改你的代码，改了什么、谁改的，一目了然

## Git vs GitHub（初学者的常见混淆）

用户经常混淆 git 命令和 GitHub 网站。当用户问 "git 是什么，GitHub 吗？" 时，用这个比喻：

> **Git = 你手机上的相机（拍照的）**
> **GitHub = 你的朋友圈（分享照片的）**

类比展开：
- Git 是装在你电脑上的一个软件（相机），负责记录文件的每一次变化（拍照）
- GitHub 是一个网站（朋友圈），把你的修改历史存到云端并跟别人分享
- 你用 `git add`、`git commit`、`git push` 这些命令 → 相当于拍照、修图、发朋友圈
- GitHub 上能看到你的提交记录 → 相当于你的朋友圈相册

常见场景：用户在 Windows 上没装 git，执行 `git clone` 时提示 "无法将 git 识别为 cmdlet"。此时引导用户安装 git（https://git-scm.com/download/win）或改用一键包。

## PR（Pull Request）是什么

> PR = "我改了一些东西，你来看看，觉得没问题就合并进去"

两种形态：

- **我发 PR 给别人**：我发现问题 → 我修改 → 发 PR 给原作者审核 → 原作者合并
- **别人发 PR 给我**：别人发现我的 bug → 他修好 → 发 PR 给我审 → 我决定是否合并

## PR vs 导师改论文

| 维度 | 导师改论文 | PR 流程 |
|------|-----------|---------|
| 谁动手改 | 导师直接改 | 你自己改（或别人改好发给你） |
| 谁做决定 | 你听导师的 | 维护者（你）决定要不要接受 |
| 修改记录 | 可能没有 | 每一行改动都可见 |
| 关系模式 | **领导与下属**（命令式） | **对等协作**（分布式、审核式） |

## Fork 是什么

> Fork = 复制别人的项目到你的账号下

Fork 后你在自己的副本里随便改，改完通过 PR 发回原版。

## 常用的教学序列（hands-on 顺序）

```
1. Star → 点个赞，熟悉页面
2. Fork → 复制到你的名下
3. 网页修改文件 → 体验第一次 commit
4. 发起第一个 PR → 把修改发回原版
5. 本地 clone + push → 从本地推上 GitHub
```

推荐练习仓库：`firstcontributions/first-contributions`

## 备用实操路径（当用户对 PR 流程感到迷茫时）

如果用户在用 first-contributions 的 PR 流程中卡住（找不到 Commit changes 按钮等），立即切换到此方案：

1. 让用户在 GitHub 网页上创建新仓库（`github.com/new`）
2. 从容器端推送本地已有仓库到该新建仓库
3. 整个过程只需 3 步，零 UI 操作
4. 用户完成后可以在 GitHub 网页上看到自己的文件，建立成就感后再回头学 PR

## PR 成功后的收尾动作

当用户的第一个 PR 成功提交后：

1. **立即告诉用户 PR 编号** — 比如 "PR #117942"，让用户有具体的成果可追踪
2. **给用户 PR 链接** — `https://github.com/{original_owner}/{original_repo}/pull/{number}`，让用户可以自己盯着进度
3. **做个完整进度总结** — 表格列出全部已掌握的操作，给用户「这堂课结束」的仪式感
4. **约定下次续接方式** — 用户可能不经常来，明确说"下次回来直接说继续就行"
5. **为可能的后续任务埋钩子** — 比如：下次可以教 Branch（分支）、本地修改后推送、解决合并冲突等

## PR 流程调试（当 fork 没有变化时）

常见问题：用户 Fork 了一个仓库、在网页上编辑了文件并点了提交，但 /compare 页面的 "Create pull request" 按钮是灰色的（点不动）。

**原因：用户的提交可能没有成功执行。** 即使他们以为点过了 Commit changes，也可能因为页面加载问题、浏览器弹窗拦截等实际没有提交成功。

**调试步骤（在引导用户前往 PR 页面之前，先通过 API 确认）：**

```bash
# 检查 fork 与原版的差异
curl -sL "https://api.github.com/repos/{原版owner}/{原版repo}/compare/main...{用户owner}:{用户repo}:main" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'ahead_by: {d.get(\"ahead_by\")}, files_changed: {len(d.get(\"files\",[]))}')"
```

- 如果 `ahead_by: 0` → 用户 fork 没有改动 → 引导用户回到 fork 仓库，重新编辑文件并提交
- 如果 `ahead_by: > 0` → 有改动 → 引导用户去 PR 页面

**注意：** GitHub 的 raw.githubusercontent.com 有 CDN 缓存，刚提交后直接 curl 可能看到旧版本。用 `api.github.com/repos/{owner}/{repo}/contents/{path}` 或加 `?nocache=$(date +%s)` 参数可绕过。

### 引导用户去 PR 的正确路径

**不要直接给新手 /compare 链接。** 新手看到空白/灰色按钮会困惑。应该：

1. 让他们去 **自己的 fork 仓库主页**（不是原版仓库）
2. 点 **Pull requests** 选项卡
3. 点绿色的 **New pull request** 按钮
4. 页面会自动跳转到比较页，此时按钮应该可用

## GitHub Token 设置（从 CLI/容器推送时需要）

当从非交互式环境（Docker 容器、CLI）推送代码到 GitHub 时，需要 Personal Access Token：

1. 用户打开 https://github.com/settings/tokens
2. 点 Generate new token (classic)
3. Note 填一个名字（如 hermes-agent）
4. 勾选 repo（全选）和 workflow
5. 点 Generate token
6. 复制生成的 token（以 ghp_ 开头）
7. 在 CLI 中配置：
   ```
   git remote set-url origin https://github.com/用户名/仓库名.git
   git config credential.helper store
   echo "https://用户名:$TOKEN@github.com" > ~/.git-credentials
   ```
8. 验证：git push 应无需再次认证

注意：token 只在生成时显示一次，丢失需重新生成。泄露应立即到同一页面 Revoke。token 在 CLI 命令中明文出现会被安全扫描标记为 HIGH 风险，应尽快存入 git-credentials 并从命令历史中消除。
