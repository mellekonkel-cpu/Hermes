# 每日新闻简报 — 脚本参考

## 脚本路径
`/opt/data/skills/devops/provider-gateway/scripts/fetch-daily-news.py`

## 手动运行
```bash
python3 /opt/data/skills/devops/provider-gateway/scripts/fetch-daily-news.py
```

## 搜索分类（共5类，每类最多6条）
1. **国际经济** — major international economic news markets trade policy
2. **前沿科技** — latest technology news AI semiconductor breakthrough innovation
3. **新能源电池** — battery electrolyte lithium metal solid state battery
4. **新材料** — new materials science research breakthrough graphene polymer composite
5. **国内产业** — 中国新能源电池新材料产业政策 market dynamics

## 输出格式（每条新闻3行）
```text
▪ 标题
  🔗 https://完整链接（绝不截断）
  📝 要点摘要（300字以内）
```

## 存档机制
- 主文件: `每日新闻简报.txt`（每天覆盖）
- 存档: `每日新闻简报_YYYY-MM-DD.txt`（永不覆盖，`if not os.path.exists` 检查）

## Cron 故障排查

### 症状: cron job 不执行（简报不更新）

检查方法：
```bash
hermes cron list
```

**关键字段：**
- `last_run_at` — 如果为 `null`，说明从未触发过
- `state` — 如果是 `scheduled` 但从未变成 `running`，说明调度器没有正常触发

**已知问题：`no_agent` 模式的 cron job 有时无法自动触发脚本执行。**
如果发现 `last_run_at` 始终为 `null`，手动删除并重建 cron job。重建后手动验证一次。

### 手动运行脚本
```bash
python3 /opt/data/skills/devops/provider-gateway/scripts/fetch-daily-news.py
```
脚本会：
1. 搜索5个板块，各取6条结果
2. 更新 `每日新闻简报.txt`（覆盖）
3. 生成存档 `每日新闻简报_YYYY-MM-DD.txt`（若不存在）

### 补发历史简报

**⚠️ 限制：脚本不支持日期参数，只能生成当天简报。**
无法通过传参补发过去某天。如需跨天补发，目前无自动化方案，需直接告知用户缺失。
