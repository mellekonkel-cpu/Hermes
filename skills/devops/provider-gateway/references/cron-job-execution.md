# Cron Job Execution Notes

## Observed Behavior

In this Hermes environment, cron jobs configured with `no_agent: true` + `script:` may silently fail to execute — `last_run_at` remains `null` and no output file is produced. This was observed with the daily news brief cron job (original ID: `8defb0d9b510`).

## Root Cause (Speculative)

Likely the no_agent scheduler process does not have access to the Python runtime or the script path, or the execution simply never fires despite `state: scheduled` and correct `next_run_at`.

## Workaround

**Use agent-mode cron jobs instead** — omit `no_agent` (defaults to `false`). The agent prompt should instruct the agent to run the script:

> "执行 fetch-daily-news.py 脚本来获取今天的新闻并更新每日新闻简报文件。"

This works because the agent has terminal access and can invoke the Python script directly.

## Manual Trigger Verification

`cronjob(action='run')` is not synchronous — calling it updates `next_run_at` immediately but the job may not actually run. To verify:

1. Run `cronjob(action='run')` 
2. Wait 15-30 seconds
3. Check the output file's last-modified time
4. If unchanged, run the script manually: `python3 <script_path>`

## Schedule

Recommended schedule for daily morning news: `0 0 * * *` (00:00 UTC = 08:00 CST = daily morning)
