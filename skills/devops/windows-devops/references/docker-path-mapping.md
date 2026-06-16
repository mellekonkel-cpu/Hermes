# Docker Path Mapping: Windows Host ↔ Container

## The Double Mapping Problem

The Hermes Agent setup uses **two different `/opt/data` mounts** depending on the context:

| Context | `/opt/data` resolves to |
|---------|------------------------|
| **Inside the Docker container** | `C:\Users\<WindowsUser>\.hermes\` (via `-v "$env:USERPROFILE\.hermes:/opt/data"`) |
| **WSL (user's terminal)** | `C:\` root (via 9p filesystem mount) |

## Why This Causes Bugs

A file written at `/opt/data/青桑/run_hermes.bat`:

- **Inside the container** → `C:\Users\WuShiChun\.hermes\青桑\run_hermes.bat` ✓ (the user's actual file)
- **WSL perspective** → `C:\青桑\run_hermes.bat` (WRONG — this is a different location!)

**Result:** When modifying files from WSL `/opt/data/`, you're writing to `C:\青桑\...` which the user never sees. The user sees `C:\Users\WuShiChun\.hermes\...`.

## But for 武士淳's Hermes Agent Setup

In the **specific case of 武士淳's Hermes Agent daemon container**, I (the agent) am running **inside the container** (hostname is a Docker container ID, `/opt/hermes/.venv/bin/hermes` exists). So:

- `/opt/data/` inside the container = `C:\Users\WuShiChun\.hermes\` on Windows ✓
- Files I write to `/opt/data/青桑/...` ARE the files the user sees at `C:\Users\WuShiChun\.hermes\青桑\...` ✓

The mapping is only problematic when using the WSL terminal directly (not inside the container).

## How to Detect Which Context You're In

```bash
# Check if inside container
hostname
# Container: looks like "734a1d86db2a" (Docker container ID)
# WSL: looks like a proper hostname

# Check for Hermes binary
ls -la /opt/hermes/.venv/bin/hermes 2>/dev/null
# Exists in container, doesn't exist in WSL

# Check user
whoami
# Container: "hermes" (non-root user)
# WSL: "root" or actual username
```

## Best Practice

When told the user's file path is `C:\Users\WuShiChun\.hermes\...`, translate to the **container path**:

```python
# Container perspective (where the agent runs):
C:\Users\WuShiChun\.hermes\青桑\file.txt
→ /opt/data/青桑/file.txt

# WSL perspective (when running outside container):
C:\Users\WuShiChun\.hermes\青桑\file.txt
→ /opt/data/Users/WuShiChun/.hermes/青桑/file.txt
```

Always confirm which environment you're in before manipulating files in `/opt/data/`.
