#!/bin/bash
# setup-git-token.sh — configure git credential store with a GitHub PAT
#
# Usage in a teaching session (token is user-provided):
#   bash setup-git-token.sh <github-username> <token> [remote-url]
#
# After running, git push/pull should work without password prompts.
# The token is stored in ~/.git-credentials (plaintext, readable only by user).

USERNAME="${1:?Usage: setup-git-token.sh <github-username> <token>}"
TOKEN="${2:?Usage: setup-git-token.sh <github-username> <token>}"
REMOTE="${3:-}"

git config --global credential.helper store

# Write credentials in the format git expects
echo "https://${USERNAME}:${TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# If a remote URL was provided, set it (without embedded token)
if [ -n "$REMOTE" ]; then
  git remote set-url origin "$REMOTE"
fi

echo "✓ Git credentials configured for $USERNAME"
