#!/bin/bash
# Daily news brief cron job setup
# Run after the user provides their API keys

# 1. Ensure script exists under ~/.hermes/scripts/
mkdir -p ~/.hermes/scripts/
cp /opt/data/skills/devops/provider-gateway/scripts/fetch-daily-news.py ~/.hermes/scripts/

# 2. Create the cron job (agent mode, no no_agent flag)
cronjob action=create \
  name="每日国际新闻晨报" \
  schedule="0 0 * * *" \
  script=fetch-daily-news.py \
  deliver=local

# 3. Verify by running once manually
python3 /opt/data/skills/devops/provider-gateway/scripts/fetch-daily-news.py
echo "Verification: output file exists = $(test -f /opt/data/青桑/每日新闻简报.txt && echo YES || echo NO)"
