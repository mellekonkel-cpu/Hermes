#!/usr/bin/env python3
"""
Ping all configured external API providers to verify they're working.
Run this to check connectivity and response times.

Usage:
    python3 /opt/data/skills/devops/provider-gateway/references/ping-script.py
"""
import json, urllib.request, urllib.error, time, sys

results = []
SUCCESS_EMOJI = "  "
FAIL_EMOJI = "  "

def get_json(url, headers, data=None, method="POST", timeout=15):
    """Send HTTP request and return parsed JSON response."""
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        latency = round((time.time() - t0) * 1000)
        return latency, json.loads(resp.read())

# ─── SiliconFlow ───────────────────────────────────────────────
SF_KEY = "sk-...your-siliconflow-key"
SF_URL = "https://api.siliconflow.cn/v1/chat/completions"
try:
    lat, data = get_json(SF_URL, {
        "Authorization": f"Bearer {SF_KEY}",
        "Content-Type": "application/json"
    }, {
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    })
    ok = "choices" in data and len(data["choices"]) > 0
    results.append(f"  SiliconFlow (deepseek-ai/DeepSeek-V4-Flash) — {lat}ms  {'OK' if ok else 'UNEXPECTED'}")
except Exception as e:
    results.append(f"  SiliconFlow — {type(e).__name__}: {str(e)[:80]}")

# ─── Tavily ────────────────────────────────────────────────────
TAVILY_KEY = "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"
try:
    lat, data = get_json("https://api.tavily.com/search", {
        "Content-Type": "application/json"
    }, {
        "api_key": TAVILY_KEY,
        "query": "ping",
        "search_depth": "basic",
        "max_results": 1
    })
    n = len(data.get("results", []))
    results.append(f"  Tavily — {lat}ms  results={n}")
except Exception as e:
    results.append(f"  Tavily — {type(e).__name__}: {str(e)[:80]}")

# ─── Google AI Studio ───────────────────────────────────────────
GEMINI_KEY = "AIza...your-gemini-key"
try:
    # Model listing (reliable even when quota exhausted)
    lat, data = get_json(
        f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_KEY}",
        {}, None, "GET"
    )
    models = [m["name"] for m in data.get("models", []) if "gemini" in m["name"]]
    results.append(f"  Google AI Studio (model list) — {lat}ms  {len(models)} models")

    # Content gen test (may 429 if quota exhausted)
    try:
        lat2, data2 = get_json(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
            {"Content-Type": "application/json"},
            {"contents": [{"parts": [{"text": "ping"}]}], "generationConfig": {"maxOutputTokens": 5}}
        )
        ok = "candidates" in data2 and len(data2["candidates"]) > 0
        results.append(f"  Google AI Studio (gemini-2.0-flash) — {lat2}ms  {'OK' if ok else 'UNEXPECTED'}")
    except urllib.error.HTTPError as e:
        results.append(f"  Google AI Studio content gen — HTTP {e.code}: quota issue (free tier)")
except Exception as e:
    results.append(f"  Google AI Studio — {type(e).__name__}: {str(e)[:80]}")

# ─── OpenRouter (4 free models) ────────────────────────────────
OR_KEY = "sk-or-...your-openrouter-key-here"
OR_MODELS = [
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "minimax/minimax-m2.5:free",
    "qwen/qwen3-coder:free",
]
for model in OR_MODELS:
    try:
        lat, data = get_json("https://openrouter.ai/api/v1/chat/completions", {
            "Authorization": f"Bearer {OR_KEY}",
            "Content-Type": "application/json"
        }, {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5
        })
        results.append(f"  OpenRouter {model} — {lat}ms  OK")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            msg = json.loads(body).get("error", {}).get("message", body[:60])
        except:
            msg = body[:60]
        results.append(f"  OpenRouter {model} — HTTP {e.code}: {msg}")
    except Exception as e:
        results.append(f"  OpenRouter {model} — {type(e).__name__}: {str(e)[:60]}")

print("═" * 56)
print("  Provider Gateway Ping Report")
print("═" * 56)
for r in results:
    print(r)
print("═" * 56)
