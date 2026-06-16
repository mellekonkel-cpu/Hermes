#!/bin/bash
set -e

HERMES_HOME="${HERMES_HOME:-/opt/data}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/3] 复制 config.yaml..."
mkdir -p "$HERMES_HOME"
if [ -f "$HERMES_HOME/config.yaml" ] && [ ! -f "$HERMES_HOME/config.yaml.bak" ]; then
  cp "$HERMES_HOME/config.yaml" "$HERMES_HOME/config.yaml.bak"
  echo "  备份原配置 → config.yaml.bak"
fi
cp "$SCRIPT_DIR/.hermes/config.yaml" "$HERMES_HOME/config.yaml"

echo "[2/3] 复制 skills..."
if [ -d "$HERMES_HOME/skills" ]; then
  cp -r "$HERMES_HOME/skills" "${HERMES_HOME}/skills.bak" 2>/dev/null || true
  echo "  备份原 skills → skills.bak"
fi
rm -rf "$HERMES_HOME/skills"
cp -r "$SCRIPT_DIR/skills" "$HERMES_HOME/skills"

echo "[3/3] 复制 SOUL.md..."
cp "$SCRIPT_DIR/SOUL.md" "$HERMES_HOME/SOUL.md" 2>/dev/null || true

echo ""
echo "✅ 部署完成！"
echo ""
echo "下一步："
echo "  1. cp .env.example $HERMES_HOME/.env"
echo "  2. 编辑 $HERMES_HOME/.env 填入 API Key"
echo "  3. hermes doctor 验证"
echo ""
