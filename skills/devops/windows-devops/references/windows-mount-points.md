# Windows Drive Mount Points

This environment runs Docker on Windows via WSL. The Windows C: drive mount point
varies by setup — **always verify with `df -h` before resolving Windows paths.**

## Current Environment (as of 2026-05-28)

| Windows Path | Container/WSL Path |
|---|---|
| `C:\` | `/opt/data/` |
| `C:\Users\WuShiChun\...` | `/opt/data/Users/WuShiChun/...` |
| `C:\...` | `/opt/data/...` |

**Note:** Not all user files live under the mapped Windows home directory.
Some files (especially project-specific ones) are placed directly under
`/opt/data/青桑/` rather than `/opt/data/Users/WuShiChun/...`.
Always check multiple locations.

## General Rule

Never assume `/mnt/c/` is the mount point. Run:

```bash
df -h | grep "^[A-Z]:"
```

This shows which Windows drive is mounted where. The mount path could be
`/mnt/c/`, `/opt/data/`, `/data/`, or something else entirely.
