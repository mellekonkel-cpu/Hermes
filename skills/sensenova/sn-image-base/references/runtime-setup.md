# Runtime Setup

## Invoking sn-image-base Tools

The sn-image-base scripts (`sn_agent_runner.py` + `sn_image_base/` package) live under `scripts/` in the skill directory. In this environment (`/opt/data/`), the scripts are at `/opt/data/sn_scripts/`.

### With uv (preferred — isolates dependencies)

The scripts need `httpx`, `Pillow`, and `typing-extensions`. Use uv to create a throwaway venv:

```bash
uv run --python 3.13 \
  --with httpx --with Pillow --with typing-extensions \
  --no-project \
  python3 /path/to/script.py
```

The `--no-project` flag prevents uv from treating the scripts directory as a buildable package (which fails because the pyproject.toml expects a build backend).

Set `PYTHONPATH` for the script to find the `sn_image_base` package:

```python
import sys
sys.path.insert(0, "/opt/data/sn_scripts")
```

### Environment Variables

Read from `/opt/data/.env` by `sn_image_base/configs.py` automatically. Key vars:

| Var | Purpose |
|-----|---------|
| `SN_API_KEY` | SenseNova API key (also fallback for image gen) |
| `SN_IMAGE_GEN_BASE_URL` | Default: `https://token.sensenova.cn/v1` |
| `SN_IMAGE_GEN_MODEL` | Default: `sensenova-u1-fast` |
| `AGNES_AI_API_KEY` | Agnes AI key (read by `dual_vision.py` directly from .env) |

The `.env` file is a Hermes credential store — cannot be read via `read_file` tool but IS readable by Python scripts running in the terminal.

### SenseNova API Details

- **Endpoint**: `POST {base_url}/images/generations`
- **Base URL**: `https://token.sensenova.cn/v1`
- **Auth**: Bearer token in `SN_API_KEY` or `SN_IMAGE_GEN_API_KEY`
- **Model**: `sensenova-u1-fast` (text-to-image)
- **Aspect ratios**: `1:1` → 2048×2048 at 2K; `16:9` → 2752×1536 at 2K
- **No proxy needed** — domestic Chinese service

### SenseNova Vision Note

`sensenova-u1-fast` does NOT support multimodal (image + text) input. For image analysis, fall back to:
- Agnes AI `agnes-2.0-flash` (via proxy)
- A second Agnes AI call with an alternate prompt as perspective B

### Dual-Engine Pipeline

`/opt/data/sn_scripts/dual_vision.py` orchestrates both engines:

```bash
python3 /opt/data/sn_scripts/dual_vision.py gen "<prompt>"
python3 /opt/data/sn_scripts/dual_vision.py analyze <image-path>
```

This script reads keys from `/opt/data/.env` and uses `curl` (not httpx) for reliability. It auto-saves images to `/opt/data/青桑/photo/`.
